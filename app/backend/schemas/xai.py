"""
XAI (Explainable AI) schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class FeatureImportance(BaseModel):
    """Individual feature importance from SHAP analysis"""
    feature: str = Field(..., description="Name of the clinical feature")
    value: Any = Field(..., description="Current value of the feature")
    unit: str = Field(default="", description="Unit of measurement")
    importance: float = Field(..., description="Importance score (-1 to 1)")
    direction: str = Field(..., description="positive, negative, or neutral contribution")
    normal_range: str = Field(default="", description="Normal reference range")
    explanation: str = Field(..., description="Human-readable explanation")
    adjusted_importance: Optional[float] = Field(None, description="Adjusted importance score")


class LocalExplanationFactor(BaseModel):
    """Key factor in LIME-style local explanation"""
    condition: str = Field(..., description="Clinical condition identified")
    rule: str = Field(..., description="Decision rule applied")
    weight: float = Field(..., description="Weight in the local model")
    met: bool = Field(..., description="Whether the condition was met")


class LocalExplanation(BaseModel):
    """LIME-style local interpretable explanation"""
    model_type: str = Field(..., description="Type of local model used")
    local_accuracy: float = Field(..., description="Accuracy of local approximation")
    key_factors: List[LocalExplanationFactor] = Field(default_factory=list)
    interpretation: str = Field(..., description="Human-readable interpretation")
    simplification_note: str = Field(..., description="Note about simplification")


class CounterfactualChange(BaseModel):
    """Single change in counterfactual explanation"""
    feature: str = Field(..., description="Feature to change")
    current_value: Any = Field(..., description="Current value")
    target_value: Any = Field(..., description="Target value for different outcome")
    unit: str = Field(default="", description="Unit of measurement")
    change_needed: float = Field(..., description="Magnitude of change needed")
    intervention: str = Field(..., description="Suggested intervention")
    timeline: str = Field(..., description="Expected timeline for change")


class CounterfactualExplanation(BaseModel):
    """Counterfactual explanation - what would need to change"""
    scenario: str = Field(..., description="Scenario being explained")
    changes_needed: List[CounterfactualChange] = Field(default_factory=list)
    minimum_changes: int = Field(..., description="Minimum number of changes needed")
    feasibility: str = Field(..., description="Feasibility assessment")
    clinical_note: str = Field(..., description="Clinical context note")


class ContrastiveAlternative(BaseModel):
    """Alternative considered in contrastive explanation"""
    alternative: str = Field(..., description="Alternative suggestion")
    why_not_chosen: str = Field(..., description="Why this wasn't chosen")
    key_difference: str = Field(..., description="Key differentiating factor")


class ContrastiveExplanation(BaseModel):
    """Contrastive explanation - why this and not that"""
    question: str = Field(..., description="Question being answered")
    alternatives_considered: List[ContrastiveAlternative] = Field(default_factory=list)
    distinguishing_factors: List[Dict[str, str]] = Field(default_factory=list)


class DecisionStep(BaseModel):
    """Single step in the decision path"""
    step: int = Field(..., description="Step number")
    action: str = Field(..., description="Action taken")
    description: str = Field(..., description="Description of the step")
    outcome: str = Field(..., description="Outcome of this step")
    data_used: Optional[List[str]] = Field(None, description="Data used in this step")
    features_extracted: Optional[int] = Field(None, description="Number of features extracted")
    risk_factors_found: Optional[List[str]] = Field(None, description="Risk factors identified")
    top_contributors: Optional[List[str]] = Field(None, description="Top contributing features")
    thresholds_exceeded: Optional[int] = Field(None, description="Number of thresholds exceeded")
    suggestion: Optional[str] = Field(None, description="Generated suggestion text")


class ConfidenceComponent(BaseModel):
    """Component of confidence calculation"""
    feature: str = Field(..., description="Feature name")
    contribution: float = Field(..., description="Contribution to confidence")
    percentage: float = Field(..., description="Percentage of total confidence")


class ConfidenceBreakdown(BaseModel):
    """Breakdown of confidence calculation"""
    base_confidence: float = Field(..., description="Base confidence before features")
    total_confidence: float = Field(..., description="Final confidence score")
    components: List[ConfidenceComponent] = Field(default_factory=list)
    calculation_method: str = Field(..., description="Method used for calculation")
    formula: str = Field(..., description="Formula used")


class XAIExplanationResponse(BaseModel):
    """Complete XAI explanation response"""
    suggestion_id: str = Field(..., description="ID of the suggestion being explained")
    patient_id: str = Field(..., description="Patient ID")
    generated_at: str = Field(..., description="When explanation was generated")
    
    # SHAP-style feature importance
    feature_importance: List[FeatureImportance] = Field(
        default_factory=list,
        description="SHAP-style feature importance values"
    )
    
    # LIME-style local explanation
    local_explanation: LocalExplanation = Field(
        ...,
        description="LIME-style local interpretable explanation"
    )
    
    # Counterfactual explanation
    counterfactual: CounterfactualExplanation = Field(
        ...,
        description="What would need to change for different outcome"
    )
    
    # Contrastive explanation
    contrastive: ContrastiveExplanation = Field(
        ...,
        description="Why this suggestion and not alternatives"
    )
    
    # Decision path
    decision_path: List[DecisionStep] = Field(
        default_factory=list,
        description="Step-by-step reasoning path"
    )
    
    # Confidence breakdown
    confidence_breakdown: ConfidenceBreakdown = Field(
        ...,
        description="How confidence was calculated"
    )
    
    # Natural language summary
    summary: str = Field(
        ...,
        description="Human-readable summary of the explanation"
    )


class XAIExplanationRequest(BaseModel):
    """Request for XAI explanation"""
    suggestion_id: UUID = Field(..., description="ID of suggestion to explain")
    patient_id: UUID = Field(..., description="Patient ID for context")
    include_counterfactual: bool = Field(default=True, description="Include counterfactual")
    include_contrastive: bool = Field(default=True, description="Include contrastive")
    include_decision_path: bool = Field(default=True, description="Include decision path")


class QuickXAIResponse(BaseModel):
    """Quick XAI summary for inline display"""
    suggestion_id: str
    top_features: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Top 3 contributing features"
    )
    key_insight: str = Field(..., description="Key insight in one sentence")
    confidence_explanation: str = Field(..., description="Brief confidence explanation")
    action_rationale: str = Field(..., description="Why this action is recommended")

