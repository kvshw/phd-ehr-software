"""
User model
Enhanced with Finnish healthcare fields and role extensions
"""
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from core.database import Base


class User(Base):
    """
    User model for authentication and healthcare professionals
    
    Enhanced with:
    - Finnish healthcare fields (HETI number, specialty, workplace)
    - Extended role support (doctor, nurse, etc.)
    - User preferences for MAPE-K adaptations
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True)  # clinician, researcher, admin, doctor, nurse, etc.
    
    # Finnish healthcare professional fields
    heti_number = Column(String(20), unique=True, nullable=True, index=True)  # Healthcare professional HETI number
    license_number = Column(String(50), nullable=True)  # Professional license number
    workplace_municipality = Column(String(10), nullable=True)  # Municipality of workplace
    primary_workplace = Column(String(255), nullable=True)  # Primary workplace name
    
    # Extended user information
    specialty = Column(String(100), nullable=True, index=True)  # Medical specialty (cardiology, orthopedics, etc.)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    title = Column(String(50), nullable=True)  # Dr., RN, NP, PA, etc.
    department = Column(String(100), nullable=True)
    
    # User preferences for MAPE-K adaptations and UI customization
    preferences = Column(JSONB, nullable=True, default=dict)  # Store user preferences as JSON

