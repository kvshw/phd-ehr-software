"""
Conversation API routes
Handles voice conversation sessions, transcripts, and analysis
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user, require_role
from services.conversation_service import ConversationService
from services.conversation_analysis_service import ConversationAnalysisService
from schemas.conversation import (
    ConversationSessionCreate,
    ConversationSessionResponse,
    ConversationTranscriptCreate,
    ConversationTranscriptResponse,
    ConversationAnalysisResponse,
    ConversationSessionWithAnalysis,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/sessions", response_model=ConversationSessionResponse)
async def create_session(
    session_data: ConversationSessionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["clinician", "admin"])),
):
    """Create a new conversation session"""
    try:
        session = ConversationService.create_session(
            db,
            session_data.patient_id,
            current_user.user_id
        )
        return ConversationSessionResponse.model_validate(session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=ConversationSessionWithAnalysis)
async def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get a conversation session with transcripts and analysis"""
    session = ConversationService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check access (clinician who created it or admin)
    if session.clinician_id != current_user.user_id and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )
    
    transcripts = ConversationService.get_session_transcripts(db, session_id)
    analysis = ConversationService.get_session_analysis(db, session_id)
    
    response = ConversationSessionWithAnalysis.model_validate(session)
    response.transcripts = [ConversationTranscriptResponse.model_validate(t) for t in transcripts]
    if analysis:
        response.analysis = ConversationAnalysisResponse.model_validate(analysis)
    
    return response


@router.get("/patients/{patient_id}/sessions", response_model=List[ConversationSessionResponse])
async def get_patient_sessions(
    patient_id: UUID,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get all conversation sessions for a patient"""
    sessions = ConversationService.get_patient_sessions(db, patient_id, limit)
    return [ConversationSessionResponse.model_validate(s) for s in sessions]


@router.post("/transcripts", response_model=ConversationTranscriptResponse)
async def add_transcript(
    transcript_data: ConversationTranscriptCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["clinician", "admin"])),
):
    """Add a transcript entry to a session"""
    # Verify session exists and belongs to user
    session = ConversationService.get_session(db, transcript_data.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.clinician_id != current_user.user_id and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add transcripts to this session"
        )
    
    transcript = ConversationService.add_transcript(db, transcript_data)
    return ConversationTranscriptResponse.model_validate(transcript)


@router.post("/sessions/{session_id}/complete", response_model=ConversationSessionResponse)
async def complete_session(
    session_id: UUID,
    duration_seconds: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["clinician", "admin"])),
):
    """Mark a conversation session as completed"""
    session = ConversationService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.clinician_id != current_user.user_id and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this session"
        )
    
    session = ConversationService.complete_session(db, session_id, duration_seconds)
    return ConversationSessionResponse.model_validate(session)


@router.post("/sessions/{session_id}/analyze", response_model=ConversationAnalysisResponse)
async def analyze_session(
    session_id: UUID,
    use_ai: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["clinician", "admin"])),
):
    """Analyze a conversation session and generate key points, summary, etc."""
    session = ConversationService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.clinician_id != current_user.user_id and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to analyze this session"
        )
    
    # Get all transcripts
    transcripts = ConversationService.get_session_transcripts(db, session_id)
    
    if not transcripts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transcripts found for this session"
        )
    
    # Build full transcript
    full_transcript = '\n'.join([
        f"[{t.speaker.title()}] {t.text}" for t in transcripts
    ])
    
    # Analyze conversation
    analysis_result = ConversationAnalysisService.analyze_conversation(
        full_transcript,
        use_ai=use_ai
    )
    
    # Save analysis
    analysis = ConversationService.save_analysis(
        db,
        session_id,
        full_transcript,
        key_points=analysis_result.get("key_points"),
        summary=analysis_result.get("summary"),
        medical_terms=analysis_result.get("medical_terms"),
        concerns_identified=analysis_result.get("concerns_identified"),
        recommendations=analysis_result.get("recommendations")
    )
    
    return ConversationAnalysisResponse.model_validate(analysis)

