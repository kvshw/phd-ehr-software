"""
Pydantic schemas for Diagnosis Helper Service

Enhanced with evidence-based medicine fields for PhD-level academic rigor.
Includes citations, clinical guidelines, and evidence levels.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class VitalReading(BaseModel):
    """Single vital reading"""
    timestamp: datetime
    hr: Optional[int] = Field(None, ge=0, le=300)
    bp_sys: Optional[int] = Field(None, ge=0, le=300)
    bp_dia: Optional[int] = Field(None, ge=0, le=200)
    spo2: Optional[float] = Field(None, ge=0.0, le=100.0)
    rr: Optional[int] = Field(None, ge=0, le=100)
    temp: Optional[float] = Field(None, ge=25.0, le=45.0)
    pain: Optional[int] = Field(None, ge=0, le=10)


class LabResult(BaseModel):
    """Single lab result"""
    timestamp: datetime
    lab_type: str
    value: Optional[float] = None
    normal_range: Optional[str] = None


class DiagnosisSuggestionRequest(BaseModel):
    """Request schema for diagnosis suggestions"""
    patient_id: str = Field(..., description="Patient ID")
    age: Optional[int] = Field(None, ge=0, le=150, description="Patient age")
    sex: Optional[str] = Field(None, description="Patient sex")
    primary_diagnosis: Optional[str] = Field(None, description="Primary diagnosis")
    vitals: List[VitalReading] = Field(default_factory=list, description="Recent vital signs")
    labs: List[LabResult] = Field(default_factory=list, description="Recent lab results")
    diagnoses: List[str] = Field(default_factory=list, description="Existing diagnoses")


class Citation(BaseModel):
    """Medical literature citation"""
    authors: str = Field(..., description="Author names")
    title: str = Field(..., description="Paper/article title")
    journal: str = Field(..., description="Journal name")
    year: int = Field(..., description="Publication year")
    pmid: Optional[str] = Field(None, description="PubMed ID")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    url: Optional[str] = Field(None, description="URL to access the paper")


class ClinicalGuideline(BaseModel):
    """Clinical practice guideline reference"""
    organization: str = Field(..., description="Issuing organization (e.g., AHA, WHO, NICE)")
    title: str = Field(..., description="Guideline title")
    year: int = Field(..., description="Publication/update year")
    url: Optional[str] = Field(None, description="URL to access the guideline")


class MedicalEvidence(BaseModel):
    """Evidence package for a clinical suggestion"""
    evidence_level: str = Field(..., description="GRADE evidence level (High/Moderate/Low/Very Low)")
    recommendation_strength: str = Field(..., description="Strength of recommendation (Strong/Moderate/Weak)")
    guidelines: List[ClinicalGuideline] = Field(default_factory=list, description="Supporting clinical guidelines")
    citations: List[Citation] = Field(default_factory=list, description="Key medical literature citations")
    mechanism: Optional[str] = Field(None, description="Pathophysiological mechanism explanation")
    population_studied: Optional[str] = Field(None, description="Target population from research")
    limitations: List[str] = Field(default_factory=list, description="Important limitations to consider")
    clinical_pearl: Optional[str] = Field(None, description="Practical clinical tip")


class Suggestion(BaseModel):
    """Single diagnosis suggestion with evidence-based explanation"""
    id: str = Field(..., description="Unique suggestion ID")
    text: str = Field(..., description="Suggestion text (non-prescriptive)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    source: str = Field(..., description="Source: 'rules', 'ai_model', 'hybrid'")
    explanation: str = Field(..., description="Human-readable explanation")
    
    # Enhanced evidence-based fields (PhD-level)
    evidence_level: Optional[str] = Field(None, description="GRADE evidence level")
    recommendation_strength: Optional[str] = Field(None, description="Recommendation strength")
    guidelines: Optional[List[Dict[str, Any]]] = Field(None, description="Supporting guidelines")
    citations: Optional[List[Dict[str, Any]]] = Field(None, description="Key citations")
    mechanism: Optional[str] = Field(None, description="Pathophysiological mechanism")
    clinical_pearl: Optional[str] = Field(None, description="Practical clinical tip")
    limitations: Optional[List[str]] = Field(None, description="Important limitations")


class DiagnosisSuggestionResponse(BaseModel):
    """Response schema for diagnosis suggestions"""
    version: str = Field(..., description="Model version")
    suggestions: List[Suggestion] = Field(..., description="List of diagnosis suggestions")
    
    # Metadata for research
    total_rules_triggered: Optional[int] = Field(None, description="Number of rule-based suggestions")
    total_ai_generated: Optional[int] = Field(None, description="Number of AI-generated suggestions")
    evidence_coverage: Optional[float] = Field(None, description="Percentage of suggestions with evidence")

