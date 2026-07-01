from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("SkillProfile", back_populates="user", uselist=False)
    submissions = relationship("Submission", back_populates="user")


class SkillProfile(Base):
    """Tracks adaptive skill level per concept area."""
    __tablename__ = "skill_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    overall_score = Column(Float, default=0.0)
    level = Column(String(20), default="beginner")  # beginner|novice|intermediate|advanced|expert

    # Concept-level skill scores (0–100 each)
    arrays = Column(Float, default=0.0)
    strings = Column(Float, default=0.0)
    hashmaps = Column(Float, default=0.0)
    recursion = Column(Float, default=0.0)
    dynamic_programming = Column(Float, default=0.0)
    trees = Column(Float, default=0.0)
    graphs = Column(Float, default=0.0)
    sorting = Column(Float, default=0.0)
    two_pointers = Column(Float, default=0.0)
    binary_search = Column(Float, default=0.0)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="profile")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(10), nullable=False)   # easy|medium|hard
    tags = Column(JSON, default=list)                 # ["arrays","hashmap"]
    starter_code = Column(JSON, default=dict)         # {"python":"...", "javascript":"..."}
    test_cases = Column(JSON, default=list)           # [{"input":"...","expected":"..."}]
    concepts = Column(JSON, default=list)             # concepts this problem trains

    submissions = relationship("Submission", back_populates="problem")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    language = Column(String(20), nullable=False)
    code = Column(Text, nullable=False)
    score = Column(Integer, default=0)               # 0–100 AI quality score
    verdict = Column(String(50), default="pending")  # pending|accepted|wrong|error
    execution_result = Column(JSON, default=dict)    # Judge0 output
    ai_feedback = Column(JSON, default=dict)         # Full AI analysis result
    error_patterns = Column(JSON, default=list)      # Detected recurring patterns
    hint_count = Column(Integer, default=0)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")


class ErrorPattern(Base):
    """Tracks recurring error patterns per user for adaptive learning."""
    __tablename__ = "error_patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pattern_name = Column(String(100), nullable=False)
    severity = Column(String(10), default="medium")   # high|medium|low
    occurrences = Column(Integer, default=1)
    concept_area = Column(String(50))
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved = Column(Integer, default=0)             # 0=active, 1=resolved
