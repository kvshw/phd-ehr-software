# System Patterns & Architecture

## High-Level Architecture

```
┌─────────────────┐
│  Frontend       │  Next.js/React
│  (Clinician UI) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backend API    │  FastAPI
│  (Auth, CRUD)   │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┬─────────────┐
    ▼         ▼              ▼             ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Database│ │Adaptation│ │Vital     │ │Image     │
│Postgres│ │Engine    │ │Model     │ │Model     │
│        │ │(MAPE-K)  │ │Service   │ │Service   │
└────────┘ └──────────┘ └──────────┘ └──────────┘
```

## MAPE-K Adaptation Engine

### Monitor
- Navigation patterns
- Suggestion accept/ignore rates
- Patient risk changes
- Model outputs

### Analyze
- Rules-based analysis of user behavior
- Risk-based prioritization
- Suggestion relevance scoring

### Plan
- Generate layout plans (JSON)
- Adjust suggestion density
- Reorder UI components

### Execute
- Frontend applies layout changes
- Updates component priorities

### Knowledge Base
- Adaptation rules
- Safety thresholds
- Model versioning
- Explanation templates

## Key Design Patterns

### 1. Microservices Architecture
- Model services are independent Python services
- Backend API routes to appropriate service
- Services can be versioned independently

### 2. Safety-First Design
- All AI outputs labeled "Experimental"
- No autonomous actions
- Full audit trail
- Explainability required for all suggestions

### 3. Role-Based Access Control (RBAC)
- `clinician`: Access to patient dashboard
- `researcher`: Access to analytics dashboard
- `admin`: System controls and configuration

### 4. Synthetic Data Pattern
- All data is synthetic or anonymized
- No PHI in logs or storage
- Research-safe data generation

## Component Relationships

### Frontend Components
- `PatientList`: Displays prioritized patient list
- `PatientDetail`: Shows full patient information
- `ImagingViewer`: Image display with AI overlays
- `SuggestionsPanel`: AI-generated suggestions
- `VitalsChart`: Time-series vital signs visualization

### Backend Services
- `auth_service`: JWT authentication & RBAC
- `patient_service`: CRUD operations for patients
- `adaptation_service`: MAPE-K engine
- `logging_service`: Research logging

### Model Services
- `vital_risk_service`: Predicts risk from vitals
- `image_analysis_service`: Analyzes medical images
- `diagnosis_helper_service`: Rule-based + ML suggestions

