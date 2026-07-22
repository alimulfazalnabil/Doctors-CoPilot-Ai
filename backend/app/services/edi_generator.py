from datetime import datetime
import logging
from typing import List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("uvicorn.error")

class ServiceLineItem(BaseModel):
    date_of_service: str
    place_of_service_code: str
    cpt_code: str
    modifiers: List[str] = []
    diagnosis_pointers: List[int] = [1]
    charge_amount: float
    units: int = 1

class ProfessionalClaimPayload(BaseModel):
    claim_id: str
    consultation_id: str
    patient_id: str
    billing_provider_npi: str
    rendering_provider_npi: str
    insurance_payer_id: str
    subscriber_policy_number: str
    diagnoses_icd10: List[str]
    service_lines: List[ServiceLineItem]
    total_billed_charge: float
    estimated_insurance_coverage: float
    estimated_patient_responsibility: float

class EDI837PGenerator:
    """Translates internal revenue cycle claims into ANSI X12 5010A1 837P standard format."""
    
    @staticmethod
    def generate_x12_837p(claim: ProfessionalClaimPayload) -> str:
        date_str = datetime.now().strftime("%Y%m%d")
        time_str = datetime.now().strftime("%H%M")
        interchange_control_num = claim.claim_id.replace("CLM-", "").zfill(9)

        segments = [
            f"ISA*00*          *00*          *ZZ*SUBMITTERID    *ZZ*CLEARINGHOUSE  *{date_str}*{time_str}*^*00501*{interchange_control_num}*0*P*:",
            f"GS*HC*SUBMITTERID*CLEARINGHOUSE*{date_str}*{time_str}*1*X*005010X222A1",
            f"ST*837*{interchange_control_num}*005010X222A1",
            f"BHT*0019*00*{claim.claim_id}*{date_str}*{time_str}*CH",
            f"NM1*41*2*DOCTORS COPILOT ENTERPRISE*****43*123456789",
            f"NM1*40*2*AVALITY CLEARINGHOUSE*****46*987654321",
            f"HL*1**20*1",
            f"NM1*85*2*ATTENDING CLINIC GROUP*****XX*{claim.billing_provider_npi}",
            f"HL*2*1*22*1",
            f"NM1*IL*1*PATIENT*JOHN***MI*{claim.subscriber_policy_number}",
        ]

        # Append Diagnosis Codes (HI segment)
        icd_pointers = "*".join([f"ABF:{diag}" for diag in claim.diagnoses_icd10])
        segments.append(f"HI*{icd_pointers}")

        # Append Service Lines (LX / SV1 segments)
        for idx, line in enumerate(claim.service_lines, start=1):
            segments.append(f"LX*{idx}")
            modifiers_str = ":".join(line.modifiers) if line.modifiers else ""
            cpt_field = f"HC:{line.cpt_code}" + (f":{modifiers_str}" if modifiers_str else "")
            diag_ptr_str = str(line.diagnosis_pointers[0]) if line.diagnosis_pointers else "1"
            segments.append(f"SV1*{cpt_field}*{line.charge_amount:.2f}*UN*{line.units}**{line.place_of_service_code}**{diag_ptr_str}")
            segments.append(f"DTP*472*RD8*{line.date_of_service.replace('-', '')}-{line.date_of_service.replace('-', '')}")

        # Trailer segments calculation
        total_segments_count = len(segments) + 3 # including SE, GE, IEA trailers
        segments.append(f"SE*{total_segments_count}*{interchange_control_num}")
        segments.append(f"GE*1*{interchange_control_num}")
        segments.append(f"IEA*1*{interchange_control_num}")

        # X12 standard delimiter is the tilde (~)
        return "~\n".join(segments) + "~"
