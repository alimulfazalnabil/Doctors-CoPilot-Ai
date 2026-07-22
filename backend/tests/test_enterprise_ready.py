import pytest
from app.services.edi_generator import EDI837PGenerator, ProfessionalClaimPayload, ServiceLineItem

def test_edi_837p_generation():
    """Tests the ANSI X12 5010A1 837P professional claim generator for enterprise billing."""
    service_line = ServiceLineItem(
        date_of_service="2026-07-22",
        place_of_service_code="11",
        cpt_code="99214",
        modifiers=["25"],
        diagnosis_pointers=[1],
        charge_amount=150.00,
        units=1
    )
    
    payload = ProfessionalClaimPayload(
        claim_id="CLM-2026-001",
        consultation_id="CONSULT-001",
        patient_id="PATIENT-123",
        billing_provider_npi="1234567890",
        rendering_provider_npi="0987654321",
        insurance_payer_id="PAYER-999",
        subscriber_policy_number="SUB-ABC-123",
        diagnoses_icd10=["R07.9"],
        service_lines=[service_line],
        total_billed_charge=150.00,
        estimated_insurance_coverage=120.00,
        estimated_patient_responsibility=30.00
    )

    edi_output = EDI837PGenerator.generate_x12_837p(payload)

    # Validate that standard ANSI X12 5010A1 interchange and transaction segments are present
    assert edi_output is not None
    assert "ISA*" in edi_output
    assert "GS*HC*" in edi_output
    assert "ST*837*" in edi_output
    assert "BHT*0019*" in edi_output
    assert "CLM-2026-001" in edi_output
    assert "HI*ABF:R07.9" in edi_output
    assert "SV1*HC:99214:25" in edi_output
    assert "SE*" in edi_output
    assert "GE*" in edi_output
    assert "IEA*" in edi_output
    assert edi_output.endswith("~")
