"""
Problem Service
Handles business logic for problem list
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from models.problem import Problem
from schemas.problem import ProblemCreate, ProblemUpdate


class ProblemService:
    """Service for managing problem list"""

    @staticmethod
    def create_problem(db: Session, problem_data: ProblemCreate) -> Problem:
        """Create a new problem"""
        problem = Problem(
            patient_id=problem_data.patient_id,
            problem_name=problem_data.problem_name,
            icd_code=problem_data.icd_code,
            status=problem_data.status,
            onset_date=problem_data.onset_date,
            resolved_date=problem_data.resolved_date,
            notes=problem_data.notes,
        )
        db.add(problem)
        db.commit()
        db.refresh(problem)
        return problem

    @staticmethod
    def get_problems_by_patient(
        db: Session,
        patient_id: UUID,
        status: Optional[str] = None
    ) -> List[Problem]:
        """Get problems for a patient, optionally filtered by status"""
        query = db.query(Problem).filter(Problem.patient_id == patient_id)
        if status:
            query = query.filter(Problem.status == status)
        return query.order_by(Problem.created_at.desc()).all()

    @staticmethod
    def get_problem_by_id(db: Session, problem_id: UUID) -> Optional[Problem]:
        """Get a problem by ID"""
        return db.query(Problem).filter(Problem.id == problem_id).first()

    @staticmethod
    def update_problem(
        db: Session,
        problem_id: UUID,
        problem_data: ProblemUpdate
    ) -> Optional[Problem]:
        """Update a problem"""
        problem = ProblemService.get_problem_by_id(db, problem_id)
        if not problem:
            return None

        update_data = problem_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(problem, field, value)

        db.commit()
        db.refresh(problem)
        return problem

    @staticmethod
    def delete_problem(db: Session, problem_id: UUID) -> bool:
        """Delete a problem"""
        problem = ProblemService.get_problem_by_id(db, problem_id)
        if not problem:
            return False

        db.delete(problem)
        db.commit()
        return True

