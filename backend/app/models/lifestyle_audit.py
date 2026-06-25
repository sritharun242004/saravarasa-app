from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Boolean
from datetime import datetime
from app.database import Base


class LifestyleAuditQuestion(Base):
    __tablename__ = "lifestyle_audit_questions"

    id = Column(String, primary_key=True)
    section = Column(String)  # A, B, C, D, E, F
    question_number = Column(Integer)  # 1-35
    question_text = Column(String)
    input_type = Column(String)  # "text", "number", "select", "scale"
    options = Column(JSON)  # [{label: "A", value: "A", text: "..."}, ...]
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class LifestyleAuditResponse(Base):
    __tablename__ = "lifestyle_audit_responses"

    id = Column(String, primary_key=True)
    client_id = Column(String)
    section_a = Column(JSON)  # name, age, occupation, work_type, sitting_hours, marital_status
    section_b = Column(JSON)  # q7-q12 scores, raw, weighted, flags
    section_c = Column(JSON)  # q13-q20 scores, raw, weighted, flags
    section_d = Column(JSON)  # q21-q25 scores, raw, weighted, flags
    section_e = Column(JSON)  # q26-q30 scores/text, raw, weighted, flags
    section_f = Column(JSON)  # q31-q35 scores, raw, weighted, flags
    total_score = Column(Float)
    zone = Column(String)  # Green, Yellow, Orange, Red
    lowest_domain = Column(String)
    highest_domain = Column(String)
    critical_flags = Column(JSON)  # Array of flag combinations
    bnys_review_required = Column(Boolean, default=False)
    baseline_labs_required = Column(Boolean, default=False)
    priority_intervention = Column(String)
    mental_model_indicator = Column(String)
    completed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
