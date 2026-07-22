import os
import httpx
import logging
from typing import Dict, Any
from azure.identity.aio import DefaultAzureCredential

logger = logging.getLogger("uvicorn.error")

class AzureFHIRClient:
    """Manages secure communication and FHIR R4 resource syncing with Azure Health Data Services."""
    
    def __init__(self):
        self.fhir_url = os.environ.get("AZURE_FHIR_SERVICE_URL") # e.g. https://workspace-fhir.fhir.azurehealthcareapis.com

    async def _get_access_token(self) -> str:
        """Acquires a secure bearer token for Azure Health Data Services via Microsoft Entra ID."""
        if not self.fhir_url:
            raise ValueError("AZURE_FHIR_SERVICE_URL environment variable is not configured.")
        
        credential = DefaultAzureCredential()
        # The scope for Azure Health Data Services FHIR service is the resource base URL + /.default
        token = await credential.get_token(f"{self.fhir_url.rstrip('/')}/.default")
        return token.token

    async def push_fhir_bundle(self, fhir_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submits an HL7 FHIR R4 transaction or batch bundle directly to the Azure Health Data Services API.
        """
        if not self.fhir_url:
            logger.warning("AZURE_FHIR_SERVICE_URL missing. Simulating FHIR sync response.")
            return {"resourceType": "Bundle", "id": "simulated-bundle-id", "type": "transaction-response"}

        token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/fhir+json",
            "Accept": "fhir+json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.fhir_url.rstrip('/')}",
                json=fhir_bundle,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code not in [200, 201]:
                logger.error(f"Azure FHIR Server failed with status {response.status_code}: {response.text}")
                raise RuntimeError(f"FHIR Server error [{response.status_code}]: {response.text}")
            
            return response.json()
