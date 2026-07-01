"""
Tests for CodeMentor AI backend services.
Run with: pytest tests/ -v
"""
import pytest
from app.services.skill_service import SkillService, score_to_level  # type: ignore
from app.services.ai_service import PromptBuilder
from app.schemas.schemas import AIAnalysisResult, HintFeedback


# ─── Skill Service Tests ──────────────────────────────────────────────────────

def test_score_to_level():
    from app.services.ai_service import score_to_level
    assert score_to_level(5)   == "beginner"
    assert score_to_level(25)  == "novice"
    assert score_to_level(55)  == "intermediate"
    assert score_to_level(75)  == "advanced"
    assert score_to_level(95)  == "expert"


def test_ema_update():
    svc = SkillService()
    # Starting at 0, receive 50 → should be 0.3*50 + 0.7*0 = 15
    result = svc._ema_update(0.0, 50.0)
    assert abs(result - 15.0) < 0.01

    # Starting at 50, receive 80 → 0.3*80 + 0.7*50 = 24+35 = 59
    result = svc._ema_update(50.0, 80.0)
    assert abs(result - 59.0) < 0.01


# ─── PromptBuilder Tests ──────────────────────────────────────────────────────

def test_analysis_prompt_contains_level():
    prompt = PromptBuilder.analysis_prompt(
        "Two Sum", "Given array...", "python", "beginner", 15.0
    )
    assert "beginner" in prompt
    assert "Two Sum" in prompt
    assert "python" in prompt
    assert "JSON" in prompt


def test_hint_prompt_specificity():
    prompt1 = PromptBuilder.hint_prompt("Two Sum", "...", "python", "beginner", 1)
    prompt5 = PromptBuilder.hint_prompt("Two Sum", "...", "python", "beginner", 5)
    # Hint 1 should be vague, hint 5 concrete
    assert "vague" in prompt1.lower() or "general" in prompt1.lower()
    assert "concrete" in prompt5.lower()


def test_hint_prompt_hint_number():
    prompt = PromptBuilder.hint_prompt("Two Sum", "...", "python", "intermediate", 3)
    assert "3" in prompt


# ─── Schema Validation Tests ──────────────────────────────────────────────────

def test_ai_analysis_result_valid():
    result = AIAnalysisResult(
        score=75,
        verdict="Good solution with minor issues",
        errors=[
            HintFeedback(tag="tip", title="Use dict", body="A hash map would be faster."),
        ],
        skill_delta=8,
        patterns=[{"name": "Nested loops", "sev": "med"}],
        summary="Good work! Try the hash map approach next.",
        concepts_tested=["arrays", "hash map"],
    )
    assert result.score == 75
    assert result.skill_delta == 8
    assert len(result.errors) == 1
    assert result.errors[0].tag == "tip"


def test_ai_analysis_result_skill_delta_bounds():
    # skill_delta should be usable in -5 to +15 range
    result = AIAnalysisResult(
        score=90, verdict="Excellent", errors=[],
        skill_delta=15, patterns=[], summary="Great job!"
    )
    assert -5 <= result.skill_delta <= 15
