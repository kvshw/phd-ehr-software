# Project Brief: Self-Adaptive AI-Assisted EHR Research Platform

## Project Overview
A self-adaptive, AI-assisted Electronic Health Record (EHR) research platform designed to:
- Reduce clinician cognitive load
- Provide context-aware suggestions using rules + AI models
- Integrate image analysis models
- Integrate vital & diagnosis prediction models
- Provide full explainability, safety, transparency
- Use synthetic or anonymized data only
- Serve as a research platform, not a production medical device

## Core Requirements
- Clinician-facing EHR interface with prioritized patient list
- Patient detail page with imaging viewer and AI annotations
- Suggestions panel with plain-language explanations
- Adaptive behaviors using MAPE-K architecture
- Safe, transparent model integration
- Detailed logs for research purposes

## Technology Stack
- **Frontend**: Next.js 14+, TypeScript, TailwindCSS, Zustand/Context API
- **Backend**: FastAPI (Python), JWT authentication, RBAC
- **Database**: PostgreSQL
- **Storage**: MinIO/S3 for imaging files
- **Model Services**: Python microservices for vitals, imaging, diagnosis
- **Architecture**: MAPE-K (Monitor, Analyze, Plan, Execute, Knowledge)

## Key Constraints
- Synthetic/anonymized data only (no PHI)
- No integration with real hospital databases
- No autonomous ordering/diagnosis actions
- Desktop only (no mobile)
- Research platform, not production medical device

## Release Phases
1. Phase 1 – Core EHR + Basic Suggestion Rules
2. Phase 2 – Vital Model Integration
3. Phase 3 – Image Model Integration
4. Phase 4 – MAPE-K Adaptivity
5. Phase 5 – Researcher Dashboard + Fairness Tools
6. Phase 6 – Pilot Testing & Iteration

## License
MIT License or Apache 2.0 recommended

