# Vital Risk Model Service

A FastAPI microservice that analyzes vital signs trends and produces risk assessments for patients.

## Overview

This service implements a rule-based risk assessment model that:
- Analyzes the most recent 12-hour vital signs trends
- Calculates a risk score (0.0-1.0)
- Determines risk level (routine, needs_attention, high_concern)
- Identifies top contributing features
- Provides human-readable explanations

## API Endpoints

### POST `/predict`

Predicts patient risk based on vital signs trends.

**Request Body:**
```json
{
  "patient_id": "uuid-string",
  "vitals": [
    {
      "timestamp": "2025-01-15T10:00:00Z",
      "hr": 95,
      "bp_sys": 120,
      "bp_dia": 80,
      "spo2": 98.0,
      "rr": 18,
      "temp": 36.5,
      "pain": 2
    }
  ]
}
```

**Response:**
```json
{
  "version": "1.0.0",
  "risk_level": "needs_attention",
  "score": 0.45,
  "top_features": ["heart_rate_abnormal", "bp_abnormal"],
  "explanation": "Heart rate abnormal (95 bpm) → Needs Attention risk."
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Risk Assessment Logic

The service uses rule-based logic to assess risk:

### Normal Ranges
- Heart Rate: 60-100 bpm
- Systolic BP: 90-140 mmHg
- Diastolic BP: 60-90 mmHg
- SpO2: 95-100%
- Respiratory Rate: 12-20 breaths/min
- Temperature: 36.1-37.2°C
- Pain: 0-3 (scale 0-10)

### Risk Levels
- **routine**: score < 0.4
- **needs_attention**: score 0.4-0.7
- **high_concern**: score ≥ 0.7

### Risk Factors
The model considers:
- Critical values outside normal ranges
- Abnormal values
- Trends (increasing/decreasing values)
- Multiple abnormal values

## Running the Service

### Local Development
```bash
cd app/model-services/vital-risk
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker
The service is configured in `docker-compose.yml`:
```bash
docker compose up vital-risk-service
```

## Model Version

Current version: **1.0.0**

All responses include the model version for tracking and research purposes.

## Logging

The service logs:
- Request details (patient ID, number of readings)
- Risk assessment results
- Errors and exceptions

## Notes

- This is a **research platform** - all outputs are experimental
- The model is rule-based and does not use machine learning
- Future versions may incorporate ML models for improved accuracy
- All outputs should be clearly labeled as "Experimental" in the UI

