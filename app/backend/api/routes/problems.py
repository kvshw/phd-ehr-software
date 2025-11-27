"""
Problem List API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user, require_clinician
from services.problem_service import ProblemService
from schemas.problem import ProblemCreate, ProblemUpdate, ProblemResponse

router = APIRouter(prefix="/problems", tags=["problems"])


@router.post("", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem_data: ProblemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Create a new problem"""
    problem = ProblemService.create_problem(db, problem_data)
    return ProblemResponse.model_validate(problem)


@router.get("/patient/{patient_id}", response_model=List[ProblemResponse])
async def get_patient_problems(
    patient_id: UUID,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all problems for a patient"""
    problems = ProblemService.get_problems_by_patient(db, patient_id, status_filter)
    return [ProblemResponse.model_validate(problem) for problem in problems]


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a problem by ID"""
    problem = ProblemService.get_problem_by_id(db, problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )
    return ProblemResponse.model_validate(problem)


@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: UUID,
    problem_data: ProblemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Update a problem"""
    problem = ProblemService.update_problem(db, problem_id, problem_data)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )
    return ProblemResponse.model_validate(problem)


@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Delete a problem"""
    success = ProblemService.delete_problem(db, problem_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )
    return None

