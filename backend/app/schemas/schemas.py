from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── Auth Schemas ────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ─── Problem Schemas ──────────────────────────────────────────────────────────

class ProblemCreate(BaseModel):
    title: str
    description: str
    difficulty: str
    tags: List[str] = []
    starter_code: Dict[str, str] = {}
    test_cases: List[Dict[str, str]] = []
    concepts: List[str] = []


class ProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    tags: List[str]
    starter_code: Dict[str, str]
    concepts: List[str]

    class Config:
        from_attributes = True


# ─── Submission Schemas ───────────────────────────────────────────────────────

class SubmissionCreate(BaseModel):
    problem_id: int
    language: str
    code: str


class HintFeedback(BaseModel):
    tag: str              # error | gap | tip | concept
    title: str
    body: str


class AIAnalysisResult(BaseModel):
    score: int
    verdict: str
    errors: List[HintFeedback]
    skill_delta: int
    patterns: List[Dict[str, str]]
    summary: str
    concepts_tested: List[str] = []


class ExecutionResult(BaseModel):
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None
    status: str
    time: Optional[str] = None
    memory: Optional[int] = None
    passed: bool = False


class SubmissionResponse(BaseModel):
    id: int
    problem_id: int
    language: str
    code: str
    score: int
    verdict: str
    execution_result: Dict[str, Any]
    ai_feedback: Dict[str, Any]
    error_patterns: List[Dict[str, Any]]
    submitted_at: datetime

    class Config:
        from_attributes = True


# ─── Hint Schemas ─────────────────────────────────────────────────────────────

class HintRequest(BaseModel):
    problem_id: int
    language: str
    code: str
    hint_number: int = 1


class HintResponse(BaseModel):
    hint: str
    question: str
    concept: str
    hint_number: int


# ─── Chat / Q&A Schemas ───────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str   # user | assistant
    content: str


class AskRequest(BaseModel):
    problem_id: int
    language: str
    code: str
    question: str
    history: List[ChatMessage] = []


class AskResponse(BaseModel):
    answer: str
    followup: str


# ─── Skill Profile Schemas ────────────────────────────────────────────────────

class SkillProfileResponse(BaseModel):
    overall_score: float
    level: str
    arrays: float
    strings: float
    hashmaps: float
    recursion: float
    dynamic_programming: float
    trees: float
    graphs: float
    sorting: float
    two_pointers: float
    binary_search: float

    class Config:
        from_attributes = True


# ─── Error Pattern Schemas ────────────────────────────────────────────────────

class ErrorPatternResponse(BaseModel):
    id: int
    pattern_name: str
    severity: str
    occurrences: int
    concept_area: Optional[str]
    resolved: int

    class Config:
        from_attributes = True
