# 🩺 Doctors Copilot
**An Enterprise-Grade, Ambient AI Clinical Documentation & Coding Assistant**

[![Azure](https://img.shields.io/badge/Cloud-Azure%20Container%20Apps-0089D6?style=flat-square&logo=microsoftazure)](https://azure.microsoft.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014%20(App%20Router)-000000?style=flat-square&logo=next.dot.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20Async-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Security](https://img.shields.io/badge/Auth-Microsoft%20Entra%20ID%20(Zero--Trust)-0078D4?style=flat-square&logo=microsoft)](https://learn.microsoft.com/en-us/entra/)
[![Compliance](https://img.shields.io/badge/Compliance-HIPAA%20%7C%20GDPR%20%7C%20FHIR%20R4-107C10?style=flat-square)](https://www.hl7.org/fhir/)

---

## 📌 Executive Summary
**Doctors Copilot** is a HIPAA- and GDPR-compliant ambient AI scribe designed to eliminate physician burnout caused by Electronic Medical Record (EMR) data entry. By capturing patient-physician consultations in real time via browser audio, Doctors Copilot performs multi-speaker diarization, extracts clinical entities, and orchestrates specialized Large Language Model (LLM) agents to draft highly accurate SOAP notes, referral letters, and billing code recommendations (ICD-10/CPT).

Crucially, **Doctors Copilot operates under a strict "Clinician-in-the-Loop" safety model.** No clinical document or billing recommendation is ever finalized or committed to the EMR database without explicit physician review and cryptographic sign-off.

---

## 🏛️ System Architecture & Data Pipeline

```text
[WebRTC / Browser Audio Stream] 
               │ (Compressed WebM/Opus @ 25-30 kbps)
               ▼
[FastAPI Ingestion Gateway] ──(FFmpeg Subprocess Transcoder)──► [16kHz PCM s16le]
               │
               ▼
[Azure AI Speech Service] ──(Real-time Diarization)──► [Azure Blob Storage] (Encrypted Audio)
               │
               ▼ (Timestamped Speaker Turns: Doctor / Patient)
[Azure OpenAI Multi-Agent Orchestrator] (LangChain / LangGraph)
               ├──► 1. Medical NLP Engine (Text Analytics for Health) ──► FHIR R4 JSON
               ├──► 2. Documentation Agent (SOAP Notes, Referrals, Instructions)
               ├──► 3. Coding Agent (ICD-10-CM & CPT Procedure Recommendations)
               └──► 4. Validation Agent (Anti-Hallucination & Evidence Guardrails)
               │
               ▼
[React / Next.js Review UI] ──(Edit / Amend / Sign-off)──► [Azure Cosmos DB] (Immutable Ledger)

****

✨ Core Module Specifications
1. Acoustic Ingestion & Diarization Engine
Protocol: WebSocket streaming over TLS 1.3 with browser-native hardware acoustic echo cancellation (AEC) and active noise suppression.

Payload Optimization: Audio is streamed from the client as compressed WebM/Opus chunks and asynchronously piped through a headless FFmpeg subprocess in the backend, converting it to 16kHz PCM on the fly to reduce network bandwidth by 88%.

Speaker Attribution: Real-time acoustic fingerprinting maps conversational turns deterministically to Doctor and Patient roles.

2. Multi-Agent AI Clinical Pipeline
To prevent context bleed and hallucination, generative tasks are distributed across isolated Azure OpenAI (GPT-4o) agents:

Medical Extraction Agent: Transforms raw conversation turns into structured facts (symptoms, duration, severity, allergies, medications).

Documentation Agent: Drafts clinical artifacts (SOAP notes, progress notes, discharge summaries).

Coding Agent: Recommends primary/secondary ICD-10 and CPT billing codes with associated confidence intervals and clinical justifications.

Validation Guardrail: Cross-references every generated assertion against the verbal transcript; flags unsupported claims for doctor review.

3. Zero-Trust Security & Compliance (Microsoft Entra ID)
Authentication: Next.js uses Auth.js (v5) to authenticate clinicians via Microsoft Entra ID (Azure AD), acquiring OAuth 2.0 access tokens.

Authorization: FastAPI enforces stateless, in-memory RSA signature verification using PyJWT and dynamic JWKS key caching, ensuring strict Role-Based Access Control (RBAC).

Auditability: All modifications made duringarket clinician review phases are tracked in an immutable temporal ledger in Azure Cosmos DB—records are versioned, never overwritten.

📂 Repository Structure
Plaintext
doctors-copilot/
├── .github/
│   └── workflows/                # CI/CD pipelines (Terraform & DevSecOps Docker deployment)
├── backend/                      # Python 3.12, FastAPI, Azure SDKs, PyJWT
│   ├── app/
│   │   ├── api/                  # REST endpoints, health probes, & /v1/stream WebSocket router
│   │   ├── core/                 # Entra ID security, JWKS validation, config loaders
│   │   ├── models/               # Pydantic v2 validation schemas & DB temporal models
│   │   └── services/             # FFmpeg audio transcoder, NLP pipeline, Agent orchestrator
│   ├── Dockerfile                # Hardened 3-stage build (Non-root, Headless FFmpeg)
│   └── requirements.txt          # Pinned production dependencies
├── frontend/                     # Next.js 14 App Router, TypeScript, Tailwind CSS
│   ├── src/
│   │   ├── app/                  # Consultation dashboard & authentication routes
│   │   ├── components/scribe/    # AudioControls, TranscriptViewer, SOAPNoteEditor
│   │   ├── hooks/                # useAudioStreamer (WebRTC & WebSocket management)
│   │   └── types/                # Clinical domain interfaces & state models
└── infra/                        # Terraform Infrastructure-as-Code (VNet, Private Endpoints, Cosmos, ACA)

🚀 Getting Started (Local Development)
Prerequisites
Node.js 20+ and npm/pnpm
Python 3.12+ and Docker Desktop
An active Azure Subscription with deployed AI Speech and OpenAI resources.

1. Backend Setup
Bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Export local environment variables
export AZURE_SPEECH_KEY="your_speech_key"
export AZURE_SPEECH_REGION="eastus"
export ENTRA_TENANT_ID="your_entra_tenant_id"
export ENTRA_CLIENT_ID="your_api_client_id"

# Launch async Uvicorn server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
2. Frontend Setup
Bash
cd frontend
npm install

Check List:
Here is the complete checklist of the files

1. Backend Service Files (backend/)
backend/requirements.txt (Core dependencies)
backend/requirements-dev.txt (Testing dependencies: pytest, pytest-asyncio, httpx, pytest-mock)
backend/Dockerfile (Hardened 3-stage non-root container with static FFmpeg)
backend/app/main.py (FastAPI app entrypoint with OpenTelemetry instrumentation)
backend/app/services/service_bus_mesh.py (Azure Service Bus queue publisher/consumer)
backend/app/services/medical_rag.py (Azure AI Search vector RAG service for clinical guidelines)
backend/app/services/langgraph_orchestrator.py (Self-correcting LangGraph multi-agent loop: Extraction, SOAP, Coding, Validation)
backend/app/services/fhir_client.py (Azure Health Data Services FHIR R4 direct sync engine)
backend/app/services/edi_generator.py (ANSI X12 5010A1 837P professional claim generator)
backend/app/core/telemetry.py (OpenTelemetry & Azure Application Insights tracer configuration)
backend/tests/conftest.py (Pytest fixtures and test client setup)
backend/tests/test_websocket.py (WebSocket audio stream integration test)
backend/tests/test_ledger.py (Cosmos DB append-only ledger and versioning test)
backend/tests/test_langgraph.py (LangGraph multi-agent workflow test)
backend/tests/test_enterprise_ready.py (Enterprise EDI and system validation test)
2. Frontend Application Files (frontend/)
frontend/Dockerfile (Next.js standalone runner container configuration)
frontend/package.json & configuration files (Next.js 14 App Router, TypeScript, Tailwind CSS, Auth.js)
3. Infrastructure & DevOps Files (infra/ & .github/)
infra/main.tf & related Terraform scripts (Virtual Network, Private Endpoints, Cosmos DB, Key Vault, Azure AI Foundry, Container Apps)
infra/cosmosdb.tf (Cosmos DB NoSQL ledger and backup definitions)
.github/workflows/terraform.yml (Automated IaC provisioning via Azure OIDC)
.github/workflows/deploy-app.yml (DevSecOps build, Trivy CVE scan, and Container Apps zero-downtime deploy)
4. Local Orchestration (docker-compose.yml)
docker-compose.yml (Spins up the Next.js frontend, FastAPI backend with FFmpeg, and the local Linux Azure Cosmos DB Emulator)

# Configure environment variables in .env.local
# AUTH_MICROSOFT_ENTRA_ID_ID, AUTH_MICROSOFT_ENTRA_ID_SECRET, etc.

npm run dev
Navigate to http://localhost:3000 to access the clinician review workspace.
