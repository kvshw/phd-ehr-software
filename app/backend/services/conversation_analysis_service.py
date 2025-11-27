"""
Conversation Analysis Service
Extracts key points, generates summaries, and identifies medical terms from conversations
"""
from typing import List, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

# Try to import OpenAI (optional dependency)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Conversation analysis will use rule-based fallback.")


class ConversationAnalysisService:
    """Service for analyzing conversation transcripts"""

    @staticmethod
    def analyze_conversation(
        full_transcript: str,
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a conversation transcript and extract:
        - Key points
        - Summary
        - Medical terms
        - Patient concerns
        - Recommendations
        """
        if use_ai and OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            return ConversationAnalysisService._analyze_with_ai(full_transcript)
        else:
            return ConversationAnalysisService._analyze_rule_based(full_transcript)

    @staticmethod
    def _analyze_with_ai(full_transcript: str) -> Dict[str, Any]:
        """Analyze conversation using OpenAI GPT-4"""
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Extract key points
            key_points_prompt = f"""
Analyze this doctor-patient conversation and extract the key medical points discussed.
Return a JSON array of key points (maximum 10 points).

Conversation:
{full_transcript}

Return only a JSON array, no other text:
"""
            
            key_points_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical assistant that extracts key points from doctor-patient conversations. Return only valid JSON arrays."},
                    {"role": "user", "content": key_points_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            key_points_text = key_points_response.choices[0].message.content.strip()
            # Try to parse JSON array
            import json
            try:
                key_points = json.loads(key_points_text)
                if not isinstance(key_points, list):
                    key_points = [key_points]
            except:
                # Fallback: split by lines
                key_points = [p.strip() for p in key_points_text.split('\n') if p.strip()][:10]
            
            # Generate summary
            summary_prompt = f"""
Create a concise clinical summary of this doctor-patient conversation in SOAP format.
Include: Chief complaint, History of present illness, Assessment, and Plan.

Conversation:
{full_transcript}

Format as a clinical note:
"""
            
            summary_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical assistant that creates clinical summaries from doctor-patient conversations."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            summary = summary_response.choices[0].message.content.strip()
            
            # Extract medical terms (simple extraction)
            medical_terms = ConversationAnalysisService._extract_medical_terms(full_transcript)
            
            # Identify concerns
            concerns_prompt = f"""
Identify patient concerns and symptoms mentioned in this conversation.
Return a JSON array of concerns.

Conversation:
{full_transcript}

Return only a JSON array:
"""
            
            concerns_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical assistant. Return only valid JSON arrays."},
                    {"role": "user", "content": concerns_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            concerns_text = concerns_response.choices[0].message.content.strip()
            try:
                concerns = json.loads(concerns_text)
                if not isinstance(concerns, list):
                    concerns = [concerns]
            except:
                concerns = [c.strip() for c in concerns_text.split('\n') if c.strip()]
            
            # Generate recommendations
            recommendations = f"Based on the conversation, follow up on identified concerns and continue monitoring patient progress."
            
            return {
                "key_points": key_points[:10],
                "summary": summary,
                "medical_terms": medical_terms,
                "concerns_identified": concerns[:10],
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            # Fallback to rule-based
            return ConversationAnalysisService._analyze_rule_based(full_transcript)

    @staticmethod
    def _analyze_rule_based(full_transcript: str) -> Dict[str, Any]:
        """Rule-based analysis fallback"""
        lines = full_transcript.split('\n')
        
        # Extract key points (simple: lines with [Doctor] or [Patient] that are substantial)
        key_points = []
        for line in lines:
            if len(line.strip()) > 30 and ('[Doctor]' in line or '[Patient]' in line):
                # Remove speaker labels
                text = line.replace('[Doctor]', '').replace('[Patient]', '').strip()
                if text:
                    key_points.append(text[:200])  # Limit length
        
        # Simple summary
        doctor_lines = [l.replace('[Doctor]', '').strip() for l in lines if '[Doctor]' in l]
        patient_lines = [l.replace('[Patient]', '').strip() for l in lines if '[Patient]' in l]
        
        summary = f"""
**Chief Complaint:** Patient concerns discussed in conversation.

**History:** {len(patient_lines)} patient statements recorded.

**Assessment:** {len(doctor_lines)} doctor observations and responses.

**Plan:** Continue monitoring and follow-up as discussed.
        """.strip()
        
        # Extract medical terms (simple keyword matching)
        medical_terms = ConversationAnalysisService._extract_medical_terms(full_transcript)
        
        # Simple concerns extraction
        concerns = []
        for line in patient_lines:
            if any(word in line.lower() for word in ['pain', 'hurt', 'problem', 'concern', 'worry', 'symptom']):
                concerns.append(line[:150])
        
        return {
            "key_points": key_points[:10],
            "summary": summary,
            "medical_terms": medical_terms,
            "concerns_identified": concerns[:10],
            "recommendations": "Review conversation transcript for detailed information. Follow up on patient concerns."
        }

    @staticmethod
    def _extract_medical_terms(text: str) -> List[str]:
        """Extract medical terms from text (simple keyword matching)"""
        # Common medical terms
        medical_keywords = [
            'headache', 'pain', 'fever', 'nausea', 'dizziness', 'fatigue',
            'depression', 'anxiety', 'memory', 'cognitive', 'mood', 'sleep',
            'medication', 'treatment', 'therapy', 'diagnosis', 'symptom',
            'blood pressure', 'heart rate', 'temperature', 'pulse'
        ]
        
        text_lower = text.lower()
        found_terms = []
        
        for term in medical_keywords:
            if term in text_lower:
                found_terms.append(term.title())
        
        return list(set(found_terms))  # Remove duplicates

