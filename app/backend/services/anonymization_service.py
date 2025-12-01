"""
Anonymization/De-identification Service
Anonymizes patient data for non-clinician roles (admin, researcher)
Clinicians see full data for patient care
"""
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime, date
import hashlib
import secrets


class AnonymizationService:
    """Service for anonymizing patient data based on user role"""
    
    # Salt for hashing (should be stored in config in production)
    _HASH_SALT = "ehr_research_salt_change_in_production"
    
    @staticmethod
    def should_anonymize(role: str) -> bool:
        """
        Determine if data should be anonymized based on user role
        
        Args:
            role: User role (clinician, researcher, admin)
            
        Returns:
            True if data should be anonymized, False otherwise
        """
        # Clinicians (doctors, nurses) see full data for patient care
        # Researchers and admins see anonymized data
        return role in ["researcher", "admin"]
    
    @staticmethod
    def anonymize_patient(patient_data: Dict[str, Any], role: str) -> Dict[str, Any]:
        """
        Anonymize patient data for non-clinician roles
        
        Args:
            patient_data: Patient data dictionary
            role: User role
            
        Returns:
            Anonymized patient data
        """
        if not AnonymizationService.should_anonymize(role):
            # Clinicians see full data
            return patient_data
        
        anonymized = patient_data.copy()
        
        # Direct identifiers (remove or hash)
        if "name" in anonymized and anonymized["name"]:
            # Use patient ID for identification instead of name
            patient_id = str(anonymized.get("id", "unknown"))
            anonymized["name"] = f"Patient {patient_id[:8]}"
        
        # Finnish personal ID (henkilötunnus) - remove
        anonymized["henkilotunnus"] = None
        
        # Kela card number - remove
        anonymized["kela_card_number"] = None
        
        # Date of birth - keep only year for age calculation, or remove
        if "date_of_birth" in anonymized and anonymized["date_of_birth"]:
            if isinstance(anonymized["date_of_birth"], (datetime, date)):
                # Keep only year
                year = anonymized["date_of_birth"].year if hasattr(anonymized["date_of_birth"], 'year') else None
                anonymized["date_of_birth"] = f"{year}-01-01" if year else None
            else:
                # String format, extract year
                try:
                    year = str(anonymized["date_of_birth"])[:4]
                    anonymized["date_of_birth"] = f"{year}-01-01"
                except:
                    anonymized["date_of_birth"] = None
        
        # Contact information - remove or generalize
        anonymized["phone"] = None
        anonymized["email"] = None
        
        # Address - keep only city (generalized location)
        if "address" in anonymized:
            anonymized["address"] = None
        if "postal_code" in anonymized:
            anonymized["postal_code"] = None
        # Keep city for research purposes (generalized location)
        # anonymized["city"] = anonymized.get("city")  # Keep city
        
        # Emergency contact - remove all
        anonymized["emergency_contact_name"] = None
        anonymized["emergency_contact_phone"] = None
        anonymized["emergency_contact_relation"] = None
        
        # Insurance IDs - remove
        anonymized["insurance_id"] = None
        # Keep insurance_provider as category (generalized)
        
        # EHIC number - remove
        anonymized["ehic_number"] = None
        # Keep country code for research (generalized)
        
        # Add anonymization metadata
        anonymized["is_anonymized"] = True
        anonymized["anonymization_note"] = "Data anonymized for research purposes. Direct identifiers removed."
        
        return anonymized
    
    @staticmethod
    def anonymize_patient_list(patients: List[Dict[str, Any]], role: str) -> List[Dict[str, Any]]:
        """
        Anonymize a list of patients
        
        Args:
            patients: List of patient data dictionaries
            role: User role
            
        Returns:
            List of anonymized patient data
        """
        if not AnonymizationService.should_anonymize(role):
            return patients
        
        return [AnonymizationService.anonymize_patient(patient, role) for patient in patients]
    
    @staticmethod
    def anonymize_clinical_note(note_data: Dict[str, Any], role: str) -> Dict[str, Any]:
        """
        Anonymize clinical note data
        
        Args:
            note_data: Clinical note data dictionary
            role: User role
            
        Returns:
            Anonymized clinical note data
        """
        if not AnonymizationService.should_anonymize(role):
            return note_data
        
        anonymized = note_data.copy()
        
        # Remove user_id (identifies author/clinician)
        if "user_id" in anonymized:
            anonymized["user_id"] = None
        
        # Remove author name if present (replace with role)
        if "author_name" in anonymized:
            anonymized["author_name"] = "Clinician"
        if "author_id" in anonymized:
            anonymized["author_id"] = None
        
        # Note content might contain patient names or other identifiers
        # For research, we keep content but add warnings
        # In production, you might want NLP-based name entity recognition and removal
        anonymized["content_anonymized"] = True
        anonymized["anonymization_note"] = (
            "Note content may contain identifiers. "
            "Author information removed. "
            "Review content before publication."
        )
        
        anonymized["is_anonymized"] = True
        
        return anonymized
    
    @staticmethod
    def anonymize_visit(visit_data: Dict[str, Any], role: str) -> Dict[str, Any]:
        """
        Anonymize visit data
        
        Args:
            visit_data: Visit data dictionary
            role: User role
            
        Returns:
            Anonymized visit data
        """
        if not AnonymizationService.should_anonymize(role):
            return visit_data
        
        anonymized = visit_data.copy()
        
        # Remove provider/user IDs (identifies clinician)
        if "user_id" in anonymized:
            anonymized["user_id"] = None
        if "provider_name" in anonymized:
            anonymized["provider_name"] = None
        if "provider_id" in anonymized:
            anonymized["provider_id"] = None
        if "heti_number" in anonymized:
            anonymized["heti_number"] = None  # HETI number identifies healthcare professional
        
        # Remove referral names (may identify other clinicians)
        if "referral_from" in anonymized:
            anonymized["referral_from"] = None
        if "referral_to" in anonymized:
            anonymized["referral_to"] = None
        
        # Keep location generalized (department level, not specific room)
        if "location" in anonymized and anonymized["location"]:
            # Could generalize to department only
            pass
        
        anonymized["is_anonymized"] = True
        anonymized["anonymization_note"] = "Provider identifiers removed for research purposes."
        
        return anonymized
    
    @staticmethod
    def anonymize_clinical_note_list(notes: List[Dict[str, Any]], role: str) -> List[Dict[str, Any]]:
        """
        Anonymize a list of clinical notes
        
        Args:
            notes: List of clinical note data dictionaries
            role: User role
            
        Returns:
            List of anonymized clinical note data
        """
        if not AnonymizationService.should_anonymize(role):
            return notes
        
        return [AnonymizationService.anonymize_clinical_note(note, role) for note in notes]
    
    @staticmethod
    def anonymize_visit_list(visits: List[Dict[str, Any]], role: str) -> List[Dict[str, Any]]:
        """
        Anonymize a list of visits
        
        Args:
            visits: List of visit data dictionaries
            role: User role
            
        Returns:
            List of anonymized visit data
        """
        if not AnonymizationService.should_anonymize(role):
            return visits
        
        return [AnonymizationService.anonymize_visit(visit, role) for visit in visits]
    
    @staticmethod
    def hash_identifier(value: str, salt: Optional[str] = None) -> str:
        """
        Hash an identifier for consistent anonymization
        
        Args:
            value: Value to hash
            salt: Optional salt (uses default if not provided)
            
        Returns:
            Hashed value (first 16 characters)
        """
        if not value:
            return ""
        
        salt_to_use = salt or AnonymizationService._HASH_SALT
        hash_obj = hashlib.sha256(f"{salt_to_use}{value}".encode())
        return hash_obj.hexdigest()[:16]
    
    @staticmethod
    def generalize_age(age: int) -> str:
        """
        Generalize age into age ranges for additional privacy
        
        Args:
            age: Patient age
            
        Returns:
            Age range string (e.g., "20-29", "30-39")
        """
        if age < 10:
            return "0-9"
        elif age < 20:
            return "10-19"
        elif age < 30:
            return "20-29"
        elif age < 40:
            return "30-39"
        elif age < 50:
            return "40-49"
        elif age < 60:
            return "50-59"
        elif age < 70:
            return "60-69"
        elif age < 80:
            return "70-79"
        else:
            return "80+"
    
    @staticmethod
    def anonymize_medication(medication_data: Dict[str, Any], role: str) -> Dict[str, Any]:
        """
        Anonymize medication data
        
        Args:
            medication_data: Medication data dictionary
            role: User role
            
        Returns:
            Anonymized medication data
        """
        if not AnonymizationService.should_anonymize(role):
            return medication_data
        
        anonymized = medication_data.copy()
        
        # Remove prescriber_id (identifies clinician who prescribed)
        if "prescriber_id" in anonymized:
            anonymized["prescriber_id"] = None
        
        anonymized["is_anonymized"] = True
        anonymized["anonymization_note"] = "Prescriber identifier removed for research purposes."
        
        return anonymized
    
    @staticmethod
    def anonymize_medication_list(medications: List[Dict[str, Any]], role: str) -> List[Dict[str, Any]]:
        """
        Anonymize a list of medications
        
        Args:
            medications: List of medication data dictionaries
            role: User role
            
        Returns:
            List of anonymized medication data
        """
        if not AnonymizationService.should_anonymize(role):
            return medications
        
        return [AnonymizationService.anonymize_medication(med, role) for med in medications]
    
    @staticmethod
    def create_anonymized_id(patient_id: UUID) -> str:
        """
        Create a consistent anonymized ID for a patient
        
        Args:
            patient_id: Patient UUID
            
        Returns:
            Anonymized ID string
        """
        return f"PAT-{AnonymizationService.hash_identifier(str(patient_id))}"

