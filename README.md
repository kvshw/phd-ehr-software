# Self-Adaptive AI-Assisted EHR Research Platform

A research platform for studying AI-assisted Electronic Health Record (EHR) systems with adaptive interfaces, explainable AI, and comprehensive logging for research purposes.

## 🎯 Project Overview

This platform serves as a research testbed for studying:
- Cognitive load reduction in clinical workflows
- Trust & interpretability of AI-assisted medical systems
- Bias, fairness, and risk management in medical AI
- Self-adaptive system behaviors in healthcare contexts

## ⚠️ Important Disclaimers

- **Research Platform Only**: This is NOT a production medical device
- **Synthetic Data Only**: All data is synthetic or anonymized - no PHI
- **Experimental AI**: All AI outputs are labeled as "Experimental"
- **No Clinical Actions**: System does not perform autonomous clinical actions

## 🏗️ Architecture

```
┌─────────────────┐
│  Frontend       │  Next.js/React/TypeScript
│  (Clinician UI) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backend API    │  FastAPI (Python)
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

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Docker & Docker Compose

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd "Medical EHR Software"
```

2. **Start services with Docker**
```bash
docker-compose up -d
```

3. **Run database migrations**
```bash
cd app/backend
alembic upgrade head
```

4. **Start backend**
```bash
cd app/backend
uvicorn main:app --reload
```

5. **Start frontend**
```bash
cd app/frontend
npm install
npm run dev
```

## 📁 Project Structure

```
/app
  /frontend          # Next.js frontend application
  /backend           # FastAPI backend application
  /model-services    # AI model microservices
  /database          # Database schemas and migrations
  /devops            # Docker and deployment configs
/scripts             # Utility scripts
/memory-bank         # Project documentation
/tasks               # Task management files
```

## 🔐 Authentication

Default roles:
- **clinician**: Access to patient dashboard
- **researcher**: Access to analytics dashboard
- **admin**: System controls and configuration

## 📊 Features

### For Clinicians
- Prioritized patient list
- Patient detail view with vitals, labs, imaging
- AI-generated suggestions with explanations
- Adaptive UI that responds to context

### For Researchers
- Analytics dashboard
- Comprehensive logging
- Model performance metrics
- Fairness indicators

### For Admins
- User management
- System configuration
- Synthetic data generation
- Model versioning

## 🧪 Development

### Running Tests
```bash
# Backend tests
cd app/backend
pytest

# Frontend tests
cd app/frontend
npm test
```

### Code Style
- Backend: Black, isort, flake8
- Frontend: ESLint, Prettier

## 📝 License

MIT License or Apache 2.0 (TBD)

## 🤝 Contributing

This is a research project. Please refer to the PRD and implementation plan for contribution guidelines.

## 📚 Documentation

- [Product Requirements Document](scripts/prd.txt)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- [Memory Bank](memory-bank/)
