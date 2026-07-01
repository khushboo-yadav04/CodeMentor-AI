from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import User, Submission, Problem
from app.schemas.schemas import (
    SubmissionCreate, SubmissionResponse,
    HintRequest, HintResponse,
    AskRequest, AskResponse,
)
from app.config import settings
if settings.use_mock_ai:
    from app.services.mock_ai_service import mock_ai_service as ai_service
else:
    from app.services.ai_service import ai_service
from app.services.judge_service import judge0_service
from app.services.skill_service import skill_service
from app.routers.auth import get_current_user

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/analyze", response_model=SubmissionResponse)
async def analyze_submission(
    data: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    problem = db.query(Problem).filter(Problem.id == data.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    profile = skill_service.get_or_create_profile(db, current_user.id)

    # 1. Run code through Judge0
    exec_result = await judge0_service.run_test_cases(
        code=data.code,
        language=data.language,
        test_cases=problem.test_cases or [],
    )

    # 2. AI analysis
    analysis = await ai_service.analyze_code(
        code=data.code,
        language=data.language,
        problem_title=problem.title,
        problem_desc=problem.description,
        skill_level=profile.level,
        skill_score=profile.overall_score,
    )

    # 3. Update skill profile
    skill_service.update_from_analysis(
        db, current_user.id, analysis, analysis.concepts_tested
    )

    # 4. Record error patterns
    skill_service.record_patterns(db, current_user.id, analysis.patterns)

    # 5. Determine verdict
    if exec_result.get("passed", 0) == exec_result.get("total", 0) and exec_result["total"] > 0:
        verdict = "accepted"
    elif exec_result.get("passed", 0) > 0:
        verdict = "partial"
    else:
        verdict = "wrong_answer"

    # 6. Save submission
    submission = Submission(
        user_id=current_user.id,
        problem_id=data.problem_id,
        language=data.language,
        code=data.code,
        score=analysis.score,
        verdict=verdict,
        execution_result=exec_result,
        ai_feedback=analysis.model_dump(),
        error_patterns=analysis.patterns,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission


@router.post("/hint", response_model=HintResponse)
async def get_hint(
    data: HintRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    problem = db.query(Problem).filter(Problem.id == data.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    profile = skill_service.get_or_create_profile(db, current_user.id)

    return await ai_service.get_hint(
        code=data.code,
        language=data.language,
        problem_title=problem.title,
        problem_desc=problem.description,
        skill_level=profile.level,
        hint_number=data.hint_number,
    )


@router.post("/ask", response_model=AskResponse)
async def ask_question(
    data: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    problem = db.query(Problem).filter(Problem.id == data.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    profile = skill_service.get_or_create_profile(db, current_user.id)

    return await ai_service.answer_question(
        question=data.question,
        code=data.code,
        language=data.language,
        problem_title=problem.title,
        skill_level=profile.level,
        history=data.history,
    )


@router.get("/history", response_model=List[SubmissionResponse])
def get_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Submission)
        .filter(Submission.user_id == current_user.id)
        .order_by(Submission.submitted_at.desc())
        .limit(limit)
        .all()
    )
