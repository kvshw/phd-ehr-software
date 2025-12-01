# Self-Adaptive AI-Assisted EHR Platform

A research platform implementing MAPE-K architecture for self-adaptive Electronic Health Record interfaces with AI-assisted clinical workflows.

![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![License](https://img.shields.io/badge/License-Research-orange)

## Overview

This platform demonstrates a novel approach to EHR personalization using:

- **MAPE-K Architecture**: Monitor-Analyze-Plan-Execute-Knowledge loop for self-adaptation
- **Thompson Sampling**: Multi-armed bandit algorithm for UI personalization
- **AI-Assisted Triage**: Human-in-the-loop clinical decision support
- **Role-Based Interfaces**: Adaptive dashboards for Doctors, Nurses, and Admins
- **Privacy-Preserving**: Federated learning and data anonymization

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Next.js 14)                  │
│   Adaptive Dashboard │ Role-Based UI │ Research Analytics│
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────┐
│                   Backend (FastAPI)                      │
│   MAPE-K Services │ AI Models │ Privacy │ Research       │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────┐
│                Database (PostgreSQL/Supabase)            │
│   Clinical Data │ Bandit State │ User Actions │ Research │
└─────────────────────────────────────────────────────────┘
```

## Live Demo

- **Frontend**: [Coming Soon](https://your-app.vercel.app)
- **API Docs**: [Coming Soon](https://your-backend.com/docs)

<!-- ### Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Doctor | clinician@demo.com | demo123 |
| Nurse | nurse@demo.com | demo123 |
| Admin | admin@demo.com | demo123 | -->

## Key Features

### Self-Adaptive Dashboard
- Automatically learns user preferences
- Adapts feature visibility and sizing
- Specialty-based initial configurations

### AI-Assisted Triage
- Analyzes patient symptoms and history
- Suggests specialty and priority
- Human override capability

### Role-Based Workflows
- **Doctor**: Adaptive clinical dashboard, incoming referrals
- **Nurse**: Triage queue, patient routing, AI suggestions
- **Admin**: Anonymized analytics, system monitoring

### Research Infrastructure
- Regret analysis for bandit performance
- Fairness metrics across user groups
- A/B testing framework

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Zustand (State Management)

### Backend
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- Pydantic Validation
- JWT Authentication

### Database
- PostgreSQL (via Supabase)

## Local Development

### Prerequisites
- Node.js 20+
- Python 3.11+
- PostgreSQL or Supabase account

### Frontend Setup

```bash
cd app/frontend
npm install
cp .env.example .env.local
# Edit .env.local with your API URL
npm run dev
```

### Backend Setup

```bash
cd app/backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database URL
uvicorn main:app --reload
```

### Docker Setup

```bash
cd devops
docker-compose up -d
```

## Deployment

### Frontend (Vercel)

1. Connect GitHub repo to Vercel
2. Set root directory: `app/frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your backend URL

### Backend (Railway/Render/Fly.io)

1. Deploy from `app/backend` directory
2. Set environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: JWT secret
   - `CORS_ORIGINS`: Frontend URL

## API Documentation

When running locally, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Research

This platform supports PhD research in self-adaptive systems for healthcare. Key research areas:

1. **UI Personalization**: Thompson Sampling bandit optimization
2. **Human-AI Collaboration**: Trust and override behavior
3. **Privacy-Preserving ML**: Federated learning patterns

## License

This is a research project. Please contact the authors for usage permissions.

## Authors

- Kavishwa Wendakoon - PhD Candidate
- Nirnaya Tripathi - Supervisor

## Acknowledgments

- University of Oulu and M3S Unit
