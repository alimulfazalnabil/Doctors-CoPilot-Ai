import os
import logging
from typing import List, Dict, Any
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.identity.aio import DefaultAzureCredential
from openai import AsyncAzureOpenAI

logger = logging.getLogger("uvicorn.error")

class MedicalRAGService:
    """Handles vector and hybrid retrieval-augmented generation (RAG) against medical guidelines and RxNorm drug data."""
    
    def __init__(self):
        self.search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT") # e.g. https://your-service.search.windows.net
        self.index_name = os.environ.get("AZURE_SEARCH_INDEX", "medical-guidelines-index")
        self.openai_api_key = os.environ.get("AZURE_OPENAI_KEY")
        self.openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.openai_embedding_deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")

    async def _get_embedding(self, text: str) -> List[float]:
        """Generates a text vector embedding using Azure OpenAI."""
        client = AsyncAzureOpenAI(
            api_key=self.openai_api_key,
            api_version="2023-12-01-preview",
            azure_endpoint=self.openai_endpoint
        )
        response = await client.embeddings.create(
            input=[text],
            model=self.openai_embedding_deployment
        )
        return response.data[0].embedding

    async def search_clinical_guidelines(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Executes a vector similarity search against Azure AI Search to retrieve 
        grounded clinical evidence and medication guidelines.
        """
        if not self.search_endpoint:
            logger.warning("AZURE_SEARCH_ENDPOINT not set. Returning mock RAG search context.")
            return [{
                "id": "mock-doc-1",
                "title": "Standard Chest Pain Triage Protocol",
                "content": "Evaluate for acute coronary syndrome, obtain ECG within 10 minutes, assess Troponin levels.",
                "score": 0.95
            }]

        credential = DefaultAzureCredential()
        vector_query = VectorizedQuery(
            vector=await self._get_embedding(query_text),
            k_nearest_neighbors=top_k,
            fields="contentVector"
        )

        async with SearchClient(endpoint=self.search_endpoint, index_name=self.index_name, credential=credential) as client:
            results = await client.search(
                search_text=query_text,
                vector_queries=[vector_query],
                select=["id", "title", "content", "source"],
                top=top_k
            )
            
            documents = []
            async for result in results:
                documents.append({
                    "id": result.get("id"),
                    "title": result.get("title"),
                    "content": result.get("content"),
                    "source": result.get("source"),
                    "score": result.get("@search.score")
                })
            
            return documents
