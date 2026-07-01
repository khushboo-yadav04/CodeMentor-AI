from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import SkillProfileResponse, ErrorPatternResponse
from app.services.skill_service import skill_service
from app.routers.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/skill", response_model=SkillProfileResponse)
def get_skill_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return skill_service.get_or_create_profile(db, current_user.id)


@router.get("/patterns", response_model=List[ErrorPatternResponse])
def get_error_patterns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return skill_service.get_patterns(db, current_user.id)


@router.get("/recommendations")
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return skill_service.get_recommendations(db, current_user.id)


@router.patch("/patterns/{pattern_id}/resolve")
def resolve_pattern(
    pattern_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.models import ErrorPattern
    pattern = db.query(ErrorPattern).filter(
        ErrorPattern.id == pattern_id,
        ErrorPattern.user_id == current_user.id,
    ).first()
    if pattern:
        pattern.resolved = 1
        db.commit()
    return {"message": "Pattern marked as resolved"}
