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
