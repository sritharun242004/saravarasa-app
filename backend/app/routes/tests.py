from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel
from app.database import AsyncSessionLocal
from app.models.client import Client
from app.models.test_attempt import TestAttempt, TestType, TestStatus, Question
from app.models.report import ComplianceScore

router = APIRouter(prefix="/tests", tags=["tests"])


class QuestionResponse(BaseModel):
    id: str
    question_text: str
    options: dict = None
    test_type: str

    class Config:
        from_attributes = True


class SubmitAnswerRequest(BaseModel):
    answers: dict


class TestStatusResponse(BaseModel):
    mcq_unlocked: bool
    descriptive_unlocked: bool
    mcq_completed: bool = False
    descriptive_completed: bool = False
    mcq_score: Optional[float] = None
    descriptive_score: Optional[float] = None
    compliance_pct: float


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/{client_id}/status", response_model=TestStatusResponse)
async def get_test_status(client_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    result = await db.execute(select(ComplianceScore).where(ComplianceScore.client_id == client_id))
    compliance = result.scalar_one_or_none()
    
    compliance_pct = compliance.compliance_pct if compliance else 0

    result = await db.execute(
        select(TestAttempt).where(
            TestAttempt.client_id == client_id,
            TestAttempt.test_type == "MCQ",
            TestAttempt.status.in_(["COMPLETED", "IN_PROGRESS"])
        )
    )
    mcq_attempt = result.scalar_one_or_none()

    result = await db.execute(
        select(TestAttempt).where(
            TestAttempt.client_id == client_id,
            TestAttempt.test_type == "DESCRIPTIVE",
            TestAttempt.status.in_(["COMPLETED", "IN_PROGRESS"])
        )
    )
    descriptive_attempt = result.scalar_one_or_none()

    mcq_done = bool(mcq_attempt and mcq_attempt.status == "COMPLETED")
    descriptive_done = bool(descriptive_attempt and descriptive_attempt.status == "COMPLETED")
    return {
        "mcq_unlocked": compliance_pct >= 85,
        "descriptive_unlocked": mcq_done,
        "mcq_completed": mcq_done,
        "descriptive_completed": descriptive_done,
        "mcq_score": mcq_attempt.score if mcq_attempt else None,
        "descriptive_score": descriptive_attempt.score if descriptive_attempt else None,
        "compliance_pct": compliance_pct,
    }


@router.get("/{client_id}/questions")
async def get_test_questions(
    client_id: str,
    test_type: str = "MCQ",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Question).where(
            Question.test_type == test_type,
            Question.is_active == True
        ).order_by(Question.order)
    )
    questions = result.scalars().all()
    return [{"id": q.id, "question_text": q.question_text, "options": q.options, "test_type": q.test_type} for q in questions]


@router.post("/{client_id}/mcq/submit")
async def submit_mcq(
    client_id: str,
    request: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    correct_count = 0
    result = await db.execute(select(Question).where(Question.test_type == "MCQ", Question.is_active == True))
    questions = result.scalars().all()

    for question in questions:
        if request.answers.get(question.id) == question.correct_answer:
            correct_count += 1

    score = (correct_count / len(questions) * 100) if questions else 0

    result = await db.execute(
        select(TestAttempt).where(
            TestAttempt.client_id == client_id,
            TestAttempt.test_type == "MCQ",
            TestAttempt.challenge_cycle == client.challenge_cycle
        )
    )
    attempt = result.scalar_one_or_none()

    if not attempt:
        attempt = TestAttempt(
            client_id=client_id,
            test_type="MCQ",
            challenge_cycle=client.challenge_cycle,
            status=TestStatus.COMPLETED,
        )

    attempt.score = score
    attempt.answers = request.answers
    attempt.submitted_at = datetime.utcnow()
    attempt.status = TestStatus.COMPLETED

    db.add(attempt)
    await db.commit()

    return {"score": score, "passed": score >= 70}


@router.post("/{client_id}/descriptive/submit")
async def submit_descriptive(
    client_id: str,
    request: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    result = await db.execute(
        select(TestAttempt).where(
            TestAttempt.client_id == client_id,
            TestAttempt.test_type == "DESCRIPTIVE",
            TestAttempt.challenge_cycle == client.challenge_cycle
        )
    )
    attempt = result.scalar_one_or_none()

    if not attempt:
        attempt = TestAttempt(
            client_id=client_id,
            test_type="DESCRIPTIVE",
            challenge_cycle=client.challenge_cycle,
            status=TestStatus.COMPLETED,
        )

    attempt.answers = request.answers
    attempt.submitted_at = datetime.utcnow()
    attempt.status = TestStatus.COMPLETED

    db.add(attempt)
    await db.commit()

    return {"status": "success", "message": "Descriptive test submitted"}
