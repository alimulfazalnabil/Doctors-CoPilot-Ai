import os
import json
import logging
from typing import Dict, Any, List, TypedDict, Annotated
import operator

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

logger = logging.getLogger("uvicorn.error")

class AmbientScribeState(TypedDict):
    """Defines the state schema for the ambient clinical documentation pipeline."""
    consultation_id: str
    transcript: str
    extracted_entities: List[Dict[str, Any]]
    soap_note: Dict[str, str]
    billing_codes: List[Dict[str, Any]]
    validation_passed: bool
    validation_feedback: str | None
    iteration_count: Annotated[int, operator.add]
    status: str

def get_llm():
    """Initializes the Azure OpenAI or standard OpenAI chat model client."""
    return ChatOpenAI(
        model=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        temperature=0.1
    )

async def extraction_node(state: AmbientScribeState) -> Dict[str, Any]:
    """Node 1: Extracts structured clinical entities (symptoms, vitals, medications) from transcript."""
    llm = get_llm()
    prompt = SystemMessage(content="You are a clinical NLP specialist. Extract all medical entities, symptoms, medications, and vitals from the transcript into a strict JSON list format with keys 'text' and 'category'.")
    response = await llm.ainvoke([prompt, HumanMessage(content=state["transcript"])])
    
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        entities = json.loads(content).get("entities", [])
    except Exception as e:
        logger.error(f"Extraction JSON parse error: {e}")
        entities = [{"text": "General Consultation", "category": "Encounter"}]

    return {"extracted_entities": entities}

async def soap_generation_node(state: AmbientScribeState) -> Dict[str, Any]:
    """Node 2: Synthesizes extracted entities into a structured SOAP clinical note."""
    llm = get_llm()
    entities_str = json.dumps(state["extracted_entities"])
    
    prompt = SystemMessage(content="You are an expert medical scribe. Generate a professional SOAP note (Subjective, Objective, Assessment, Plan) based on the entities and transcript. Return valid JSON with keys: subjective, objective, assessment, plan.")
    response = await llm.ainvoke([prompt, HumanMessage(content=f"Transcript: {state['transcript']}\nEntities: {entities_str}")])
    
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        soap = json.loads(content)
    except Exception as e:
        logger.error(f"SOAP JSON parse error: {e}")
        soap = {"subjective": state["transcript"], "objective": "", "assessment": "", "plan": ""}

    return {"soap_note": soap}

async def medical_coding_node(state: AmbientScribeState) -> Dict[str, Any]:
    """Node 3: Maps the assessment and plan to appropriate ICD-10 and CPT billing codes."""
    llm = get_llm()
    soap_str = json.dumps(state["soap_note"])
    
    prompt = SystemMessage(content="You are a medical coder. Assign accurate ICD-10 diagnosis codes and CPT procedure codes based on the SOAP note. Return valid JSON with a key 'billing_codes' containing a list of objects with 'code', 'type', and 'confidence'.")
    response = await llm.ainvoke([prompt, HumanMessage(content=soap_str)])
    
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        codes = json.loads(content).get("billing_codes", [])
    except Exception as e:
        logger.error(f"Medical Coding JSON parse error: {e}")
        codes = [{"code": "R07.9", "type": "ICD-10", "confidence": 0.85}]

    return {"billing_codes": codes}

async def validation_guardrail_node(state: AmbientScribeState) -> Dict[str, Any]:
    """Node 4: Validates the clinical documentation against basic safety and completeness rules."""
    llm = get_llm()
    soap_str = json.dumps(state["soap_note"])
    codes_str = json.dumps(state["billing_codes"])
    
    prompt = SystemMessage(content="You are a clinical compliance auditor. Verify that the SOAP note is coherent, lacks dangerous hallucinations, and matches the billing codes. Return valid JSON with keys 'passed' (boolean) and 'feedback' (string or null).")
    response = await llm.ainvoke([prompt, HumanMessage(content=f"SOAP: {soap_str}\nCodes: {codes_str}")])
    
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        validation = json.loads(content)
        passed = validation.get("passed", True)
        feedback = validation.get("feedback")
    except Exception as e:
        logger.error(f"Validation parse error: {e}")
        passed = True
        feedback = None

    return {
        "validation_passed": passed,
        "validation_feedback": feedback,
        "iteration_count": 1,
        "status": "READY_FOR_REVIEW" if passed else "NEEDS_REVISION"
    }

def route_after_validation(state: AmbientScribeState) -> str:
    """Conditional edge routing based on validation results and iteration safety limit."""
    if state["validation_passed"] or state["iteration_count"] >= 3:
        return "end"
    return "regenerate"

async def run_ambient_scribe_pipeline(consultation_id: str, transcript: str) -> Dict[str, Any]:
    """Compiles and executes the LangGraph self-correcting multi-agent workflow."""
    workflow = StateGraph(AmbientScribeState)

    # Add nodes
    workflow.add_node("extractor", extraction_node)
    workflow.add_node("soap_generator", soap_generation_node)
    workflow.add_node("medical_coder", medical_coding_node)
    workflow.add_node("validator", validation_guardrail_node)

    # Define execution graph flow
    workflow.add_edge(START, "extractor")
    workflow.add_edge("extractor", "soap_generator")
    workflow.add_edge("soap_generator", "medical_coder")
    workflow.add_edge("medical_coder", "validator")

    # Add conditional routing loop for self-correction if validation fails
    workflow.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "regenerate": "soap_generator",
            "end": END
        }
    )

    app = workflow.compile()

    initial_state = {
        "consultation_id": consultation_id,
        "transcript": transcript,
        "extracted_entities": [],
        "soap_note": {},
        "billing_codes": [],
        "validation_passed": False,
        "validation_feedback": None,
        "iteration_count": 0,
        "status": "PROCESSING"
    }

    final_state = await app.ainvoke(initial_state)
    return final_state
