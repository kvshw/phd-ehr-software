"""
Medical Evidence Database
Contains evidence-based citations, clinical guidelines, and research references
for AI-generated clinical suggestions.

This module provides PhD-level academic rigor to AI explanations by including:
- PubMed citations with DOIs
- Clinical guideline references (AHA, WHO, NICE, AAN, etc.)
- Evidence levels based on GRADE criteria
- Mechanism of action explanations
- Limitations and contraindications
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class EvidenceLevel(Enum):
    """GRADE evidence levels for clinical recommendations"""
    A = "High"        # Multiple well-designed RCTs or meta-analyses
    B = "Moderate"    # One RCT or multiple observational studies
    C = "Low"         # Observational studies, expert opinion
    D = "Very Low"    # Case reports, expert consensus


class RecommendationStrength(Enum):
    """Strength of clinical recommendation"""
    STRONG = "Strong"           # Benefits clearly outweigh risks
    MODERATE = "Moderate"       # Benefits probably outweigh risks
    WEAK = "Weak"              # Balance of benefits/risks unclear
    CONDITIONAL = "Conditional" # Depends on patient factors


@dataclass
class Citation:
    """Medical literature citation"""
    authors: str
    title: str
    journal: str
    year: int
    pmid: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    
    def to_apa(self) -> str:
        """Format citation in APA style"""
        return f"{self.authors} ({self.year}). {self.title}. {self.journal}."
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "authors": self.authors,
            "title": self.title,
            "journal": self.journal,
            "year": self.year,
            "pmid": self.pmid,
            "doi": self.doi,
            "url": self.url or (f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/" if self.pmid else None)
        }


@dataclass
class ClinicalGuideline:
    """Clinical practice guideline reference"""
    organization: str
    title: str
    year: int
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "organization": self.organization,
            "title": self.title,
            "year": self.year,
            "url": self.url
        }


@dataclass
class MedicalEvidence:
    """Complete evidence package for a clinical suggestion"""
    condition_key: str
    evidence_level: EvidenceLevel
    recommendation_strength: RecommendationStrength
    guidelines: List[ClinicalGuideline] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    mechanism: str = ""
    population_studied: str = ""
    limitations: List[str] = field(default_factory=list)
    clinical_pearl: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_level": self.evidence_level.value,
            "recommendation_strength": self.recommendation_strength.value,
            "guidelines": [g.to_dict() for g in self.guidelines],
            "citations": [c.to_dict() for c in self.citations],
            "mechanism": self.mechanism,
            "population_studied": self.population_studied,
            "limitations": self.limitations,
            "clinical_pearl": self.clinical_pearl
        }


# =============================================================================
# MEDICAL EVIDENCE DATABASE
# =============================================================================

EVIDENCE_DATABASE: Dict[str, MedicalEvidence] = {
    
    # =========================================================================
    # COGNITIVE DECLINE / DEMENTIA
    # =========================================================================
    
    "b12_cognitive": MedicalEvidence(
        condition_key="b12_cognitive",
        evidence_level=EvidenceLevel.A,
        recommendation_strength=RecommendationStrength.STRONG,
        guidelines=[
            ClinicalGuideline(
                organization="American Academy of Neurology (AAN)",
                title="Practice Parameter: Early Detection of Dementia",
                year=2001,
                url="https://www.aan.com/Guidelines/home/GuidelineDetail/44"
            ),
            ClinicalGuideline(
                organization="NICE",
                title="Dementia: assessment, management and support (NG97)",
                year=2018,
                url="https://www.nice.org.uk/guidance/ng97"
            ),
        ],
        citations=[
            Citation(
                authors="Selhub J, Bagley LC, Miller J, Rosenberg IH",
                title="B vitamins, homocysteine, and neurocognitive function in the elderly",
                journal="American Journal of Clinical Nutrition",
                year=2000,
                pmid="10799361",
                doi="10.1093/ajcn/71.2.614s"
            ),
            Citation(
                authors="Smith AD, Refsum H",
                title="Homocysteine, B Vitamins, and Cognitive Impairment",
                journal="Annual Review of Nutrition",
                year=2016,
                pmid="27431369",
                doi="10.1146/annurev-nutr-071715-050947"
            ),
            Citation(
                authors="Köbe T, Witte AV, Schnelle A, et al.",
                title="Vitamin B12 concentration, memory performance, and hippocampal structure in patients with mild cognitive impairment",
                journal="American Journal of Clinical Nutrition",
                year=2016,
                pmid="26984483",
                doi="10.3945/ajcn.115.116970"
            ),
        ],
        mechanism="Vitamin B12 is essential for myelin synthesis and neurotransmitter production. "
                  "Deficiency leads to elevated homocysteine levels, which causes oxidative stress, "
                  "DNA damage, and neuronal apoptosis. This results in white matter lesions and "
                  "hippocampal atrophy, manifesting as cognitive decline.",
        population_studied="Adults ≥65 years with cognitive complaints; meta-analyses include >10,000 participants",
        limitations=[
            "B12 supplementation may not reverse established cognitive impairment",
            "Normal serum B12 does not exclude functional deficiency; consider methylmalonic acid levels",
            "Other causes of cognitive decline must be evaluated concurrently"
        ],
        clinical_pearl="Consider checking methylmalonic acid (MMA) even if serum B12 is low-normal (200-350 pg/mL), "
                       "as functional deficiency can occur in this range."
    ),
    
    "folate_cognitive": MedicalEvidence(
        condition_key="folate_cognitive",
        evidence_level=EvidenceLevel.B,
        recommendation_strength=RecommendationStrength.MODERATE,
        guidelines=[
            ClinicalGuideline(
                organization="American Academy of Neurology (AAN)",
                title="Practice Parameter: Early Detection of Dementia",
                year=2001,
                url="https://www.aan.com/Guidelines/home/GuidelineDetail/44"
            ),
        ],
        citations=[
            Citation(
                authors="Reynolds EH",
                title="Folic acid, ageing, depression, and dementia",
                journal="BMJ",
                year=2002,
                pmid="12065267",
                doi="10.1136/bmj.324.7352.1512"
            ),
            Citation(
                authors="Morris MS, Jacques PF, Rosenberg IH, Selhub J",
                title="Folate and vitamin B-12 status in relation to anemia, macrocytosis, and cognitive impairment",
                journal="American Journal of Clinical Nutrition",
                year=2007,
                pmid="17209201",
                doi="10.1093/ajcn/85.1.193"
            ),
        ],
        mechanism="Folate is required for one-carbon metabolism and DNA methylation. "
                  "Deficiency impairs homocysteine metabolism (similar to B12), leading to "
                  "hyperhomocysteinemia and subsequent neurotoxicity. Folate also affects "
                  "neurotransmitter synthesis, particularly serotonin and dopamine.",
        population_studied="Community-dwelling elderly; observational studies",
        limitations=[
            "Association may be confounded by other nutritional deficiencies",
            "Supplementation trials have shown mixed results",
            "High-dose folate can mask B12 deficiency"
        ],
        clinical_pearl="Always check B12 before starting folate supplementation to avoid masking "
                       "B12 deficiency, which can progress to irreversible neurological damage."
    ),
    
    "tsh_cognitive": MedicalEvidence(
        condition_key="tsh_cognitive",
        evidence_level=EvidenceLevel.A,
        recommendation_strength=RecommendationStrength.STRONG,
        guidelines=[
            ClinicalGuideline(
                organization="American Thyroid Association (ATA)",
                title="Guidelines for the Treatment of Hypothyroidism",
                year=2014,
                url="https://www.thyroid.org/professionals/ata-professional-guidelines/"
            ),
            ClinicalGuideline(
                organization="American Association of Clinical Endocrinologists (AACE)",
                title="Clinical Practice Guidelines for Hypothyroidism",
                year=2012,
                url="https://www.aace.com/disease-state-resources/thyroid"
            ),
        ],
        citations=[
            Citation(
                authors="Samuels MH",
                title="Psychiatric and cognitive manifestations of hypothyroidism",
                journal="Current Opinion in Endocrinology, Diabetes and Obesity",
                year=2014,
                pmid="25122491",
                doi="10.1097/MED.0000000000000089"
            ),
            Citation(
                authors="Biondi B, Cooper DS",
                title="The clinical significance of subclinical thyroid dysfunction",
                journal="Endocrine Reviews",
                year=2008,
                pmid="18165311",
                doi="10.1210/er.2006-0043"
            ),
            Citation(
                authors="Joffe RT, Pearce EN, Hennessey JV, et al.",
                title="Subclinical hypothyroidism, mood, and cognition in the elderly",
                journal="Thyroid",
                year=2013,
                pmid="23259732",
                doi="10.1089/thy.2012.0309"
            ),
        ],
        mechanism="Thyroid hormones regulate brain glucose metabolism, neurotransmitter synthesis, "
                  "and synaptic plasticity. Hypothyroidism reduces cerebral blood flow and metabolism, "
                  "particularly affecting the frontal and temporal lobes, leading to executive dysfunction "
                  "and memory impairment.",
        population_studied="Adults with subclinical and overt hypothyroidism; multiple RCTs and observational studies",
        limitations=[
            "Cognitive effects of subclinical hypothyroidism may be subtle",
            "Treatment benefit varies by age and TSH level",
            "Other causes of cognitive decline should be excluded"
        ],
        clinical_pearl="In elderly patients, cognitive improvement with levothyroxine may take 3-6 months. "
                       "Target TSH in lower half of normal range (1-2.5 mU/L) for cognitive symptoms."
    ),
    
    # =========================================================================
    # HYPERTENSION / CARDIOVASCULAR
    # =========================================================================
    
    "hypertension_cognitive": MedicalEvidence(
        condition_key="hypertension_cognitive",
        evidence_level=EvidenceLevel.A,
        recommendation_strength=RecommendationStrength.STRONG,
        guidelines=[
            ClinicalGuideline(
                organization="American Heart Association (AHA)",
                title="2017 ACC/AHA Guideline for Prevention, Detection, Evaluation, and Management of High Blood Pressure",
                year=2017,
                url="https://www.ahajournals.org/doi/10.1161/HYP.0000000000000065"
            ),
            ClinicalGuideline(
                organization="European Society of Cardiology (ESC)",
                title="2018 ESC/ESH Guidelines for the management of arterial hypertension",
                year=2018,
                url="https://academic.oup.com/eurheartj/article/39/33/3021/5079119"
            ),
        ],
        citations=[
            Citation(
                authors="Iadecola C, Yaffe K, Bhatt DL, et al.",
                title="Impact of Hypertension on Cognitive Function: A Scientific Statement From the American Heart Association",
                journal="Hypertension",
                year=2016,
                pmid="27977393",
                doi="10.1161/HYP.0000000000000053"
            ),
            Citation(
                authors="Williamson JD, Pajewski NM, Auchus AP, et al. (SPRINT MIND)",
                title="Effect of Intensive vs Standard Blood Pressure Control on Probable Dementia",
                journal="JAMA",
                year=2019,
                pmid="30688979",
                doi="10.1001/jama.2019.10551"
            ),
            Citation(
                authors="Launer LJ, Ross GW, Petrovitch H, et al.",
                title="Midlife blood pressure and dementia: the Honolulu-Asia aging study",
                journal="Neurobiology of Aging",
                year=2000,
                pmid="10794848",
                doi="10.1016/S0197-4580(00)00096-8"
            ),
        ],
        mechanism="Chronic hypertension causes arterial stiffening, endothelial dysfunction, and "
                  "small vessel disease in the brain. This leads to white matter hyperintensities, "
                  "silent infarcts, and microbleeds, collectively contributing to vascular cognitive "
                  "impairment. Hypertension also accelerates amyloid deposition.",
        population_studied="SPRINT-MIND trial (N=9,361); Honolulu-Asia Aging Study; meta-analyses",
        limitations=[
            "Benefits of BP control may differ based on age of intervention",
            "Overly aggressive BP lowering in elderly may cause hypoperfusion",
            "Optimal BP targets for cognitive protection still debated"
        ],
        clinical_pearl="Midlife hypertension (age 40-65) is strongly associated with late-life dementia. "
                       "Early treatment provides the greatest cognitive protection. SPRINT-MIND showed "
                       "intensive BP control (SBP <120) reduced MCI risk by 19%."
    ),
    
    "diabetes_cognitive": MedicalEvidence(
        condition_key="diabetes_cognitive",
        evidence_level=EvidenceLevel.A,
        recommendation_strength=RecommendationStrength.STRONG,
        guidelines=[
            ClinicalGuideline(
                organization="American Diabetes Association (ADA)",
                title="Standards of Medical Care in Diabetes - Older Adults",
                year=2024,
                url="https://diabetesjournals.org/care/issue/47/Supplement_1"
            ),
        ],
        citations=[
            Citation(
                authors="Biessels GJ, Despa F",
                title="Cognitive decline and dementia in diabetes mellitus: mechanisms and clinical implications",
                journal="Nature Reviews Endocrinology",
                year=2018,
                pmid="29403470",
                doi="10.1038/nrendo.2018.13"
            ),
            Citation(
                authors="Crane PK, Walker R, Hubbard RA, et al.",
                title="Glucose levels and risk of dementia",
                journal="New England Journal of Medicine",
                year=2013,
                pmid="23924004",
                doi="10.1056/NEJMoa1215740"
            ),
        ],
        mechanism="Diabetes impairs cerebral glucose metabolism, promotes neuroinflammation, "
                  "and causes microvascular damage. Insulin resistance in the brain affects "
                  "amyloid clearance and tau phosphorylation, increasing Alzheimer's pathology. "
                  "Hypoglycemic episodes also cause direct neuronal injury.",
        population_studied="Multiple cohort studies; NEJM study included >2,000 participants over 7 years",
        limitations=[
            "Optimal glycemic targets for cognitive protection unclear",
            "Severe hypoglycemia may negate benefits of tight control",
            "Type 1 vs Type 2 diabetes may have different mechanisms"
        ],
        clinical_pearl="Even in non-diabetics, higher fasting glucose within normal range is associated "
                       "with increased dementia risk. Consider cognitive screening for all diabetic patients ≥65."
    ),
    
    # =========================================================================
    # REVERSIBLE CAUSES OF COGNITIVE IMPAIRMENT
    # =========================================================================
    
    "reversible_cognitive": MedicalEvidence(
        condition_key="reversible_cognitive",
        evidence_level=EvidenceLevel.B,
        recommendation_strength=RecommendationStrength.STRONG,
        guidelines=[
            ClinicalGuideline(
                organization="American Academy of Neurology (AAN)",
                title="Practice guideline update: Mild cognitive impairment",
                year=2018,
                url="https://www.aan.com/Guidelines/home/GuidelineDetail/881"
            ),
            ClinicalGuideline(
                organization="NICE",
                title="Dementia: assessment, management and support (NG97)",
                year=2018,
                url="https://www.nice.org.uk/guidance/ng97"
            ),
        ],
        citations=[
            Citation(
                authors="Clarfield AM",
                title="The decreasing prevalence of reversible dementias: an updated meta-analysis",
                journal="Archives of Internal Medicine",
                year=2003,
                pmid="12912808",
                doi="10.1001/archinte.163.18.2219"
            ),
            Citation(
                authors="Muangpaisan W, Petcharat C, Srinonprasert V",
                title="Prevalence of potentially reversible conditions in dementia and mild cognitive impairment",
                journal="Geriatrics & Gerontology International",
                year=2012,
                pmid="22469014",
                doi="10.1111/j.1447-0594.2012.00842.x"
            ),
        ],
        mechanism="Multiple conditions can cause cognitive symptoms that may improve with treatment: "
                  "nutritional deficiencies (B12, folate, thiamine), endocrine disorders (thyroid, cortisol), "
                  "infections, normal pressure hydrocephalus, medication effects, depression (pseudodementia), "
                  "and sleep disorders. Identifying these is critical as they may be fully reversible.",
        population_studied="Meta-analysis of 39 studies with >7,000 dementia patients",
        limitations=[
            "True reversal of dementia is rare (<5% of cases)",
            "Many 'reversible' causes may coexist with irreversible dementia",
            "Early intervention more likely to succeed"
        ],
        clinical_pearl="The standard 'dementia workup' should include: CBC, CMP, TSH, B12, folate, "
                       "and consider RPR/VDRL, HIV, and brain imaging. Depression screening is essential."
    ),
}


def get_evidence(condition_key: str) -> Optional[MedicalEvidence]:
    """Get medical evidence for a condition key"""
    return EVIDENCE_DATABASE.get(condition_key)


def get_evidence_dict(condition_key: str) -> Optional[Dict[str, Any]]:
    """Get medical evidence as a dictionary"""
    evidence = get_evidence(condition_key)
    if evidence:
        return evidence.to_dict()
    return None


def format_explanation_with_evidence(
    suggestion_text: str,
    condition_key: str,
    include_citations: bool = True,
    include_mechanism: bool = True
) -> str:
    """
    Format a suggestion with full evidence-based explanation
    
    Returns a rich explanation suitable for academic/clinical review
    """
    evidence = get_evidence(condition_key)
    if not evidence:
        return suggestion_text
    
    parts = [suggestion_text, ""]
    
    # Add evidence level
    parts.append(f"**Evidence Level:** {evidence.evidence_level.value} ({evidence.recommendation_strength.value} recommendation)")
    
    # Add mechanism
    if include_mechanism and evidence.mechanism:
        parts.append(f"\n**Mechanism:** {evidence.mechanism}")
    
    # Add guidelines
    if evidence.guidelines:
        parts.append("\n**Supporting Guidelines:**")
        for g in evidence.guidelines:
            parts.append(f"  • {g.organization} ({g.year}): {g.title}")
    
    # Add citations
    if include_citations and evidence.citations:
        parts.append("\n**Key References:**")
        for c in evidence.citations[:3]:  # Limit to top 3
            parts.append(f"  • {c.to_apa()}")
            if c.pmid:
                parts.append(f"    PMID: {c.pmid}")
    
    # Add clinical pearl
    if evidence.clinical_pearl:
        parts.append(f"\n**Clinical Pearl:** {evidence.clinical_pearl}")
    
    # Add limitations
    if evidence.limitations:
        parts.append("\n**Limitations:**")
        for limitation in evidence.limitations[:2]:  # Limit to top 2
            parts.append(f"  • {limitation}")
    
    return "\n".join(parts)


# Mapping from suggestion types to evidence keys
SUGGESTION_TO_EVIDENCE_MAP = {
    "b12": "b12_cognitive",
    "vitamin b12": "b12_cognitive",
    "folate": "folate_cognitive",
    "folic acid": "folate_cognitive",
    "tsh": "tsh_cognitive",
    "thyroid": "tsh_cognitive",
    "hypothyroidism": "tsh_cognitive",
    "blood pressure": "hypertension_cognitive",
    "hypertension": "hypertension_cognitive",
    "diabetes": "diabetes_cognitive",
    "glucose": "diabetes_cognitive",
    "hba1c": "diabetes_cognitive",
    "reversible": "reversible_cognitive",
    "cognitive impairment": "reversible_cognitive",
}


def find_evidence_for_suggestion(suggestion_text: str) -> Optional[str]:
    """Find the most relevant evidence key for a suggestion text"""
    text_lower = suggestion_text.lower()
    for keyword, evidence_key in SUGGESTION_TO_EVIDENCE_MAP.items():
        if keyword in text_lower:
            return evidence_key
    return None

