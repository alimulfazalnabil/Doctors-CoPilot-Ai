import pytest
from unittest.mock import AsyncMock, patch
from app.services.langgraph_orchestrator import run_ambient_scribe_pipeline

@pytest.mark.asyncio
@patch("app.services.langgraph_orchestrator.ChatOpenAI")
async def test_langgraph_ambient_scribe_pipeline(mock_chat_openai):
    """Tests the LangGraph multi-agent workflow loop with mocked Azure OpenAI LLM responses."""
    mock_llm_instance = AsyncMock()
    
    # Mock sequential LLM responses for each graph node (Extractor -> SOAP -> Coder -> Validator)
    mock_llm_instance.ainvoke.side_effect = [
        # Node 1: Extraction response
        AsyncMock(content='```json\n{"entities": [{"text": "chest pain", "category": "symptom"}]}\n```'),
        # Node 2: SOAP note generation response
        AsyncMock(content='```json\n{"subjective": "Patient reports sharp chest pain.", "objective": "BP 120/80, HR 72.", "assessment": "Atypical chest pain.", "plan": "Order 12-lead ECG and Troponin."}\n```'),
        # Node 3: Medical coding response
        AsyncMock(content='```json\n{"billing_codes": [{"code": "R07.9", "type": "ICD-10", "confidence": 0.95}, {"code": "99214", "type": "CPT", "confidence": 0.90}]}\n```'),
        # Node 4: Validation guardrail response
        AsyncMock(content='```json\n{"passed": true, "feedback": null}\n```')
    ]
    
    mock_chat_openai.return_value = mock_llm_instance

    consultation_id = "CONSULT-LANGGRAPH-TEST"
    transcript = "Doctor: What seems to be the problem? Patient: I've been having sharp chest pain since yesterday."

    result = await run_ambient_scribe_pipeline(consultation_id, transcript)

    assert result["consultation_id"] == consultation_id
    assert "soap_note" in result
    assert result["soap_note"]["subjective"] == "Patient reports sharp chest pain."
    assert len(result["billing_codes"]) == 2
    assert result["validation_passed"] is True
    assert result["status"] == "READY_FOR_REVIEW"
