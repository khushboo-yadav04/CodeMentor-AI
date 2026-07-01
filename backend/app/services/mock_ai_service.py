"""
Mock AI Service — free, offline stand-in for ai_service.py.

Returns realistic, slightly randomized feedback so the full app
(skill bars, patterns, hints, chat) can be developed and demoed
without spending any Anthropic API credits.

To switch back to the real API: in app/routers/submissions.py,
change `from app.services.mock_ai_service import mock_ai_service as ai_service`
back to `from app.services.ai_service import ai_service`.
"""

import random
from app.schemas.schemas import (
    AIAnalysisResult, HintFeedback, HintResponse, AskResponse, ChatMessage
)


VERDICTS_GOOD = [
    "Solid approach — your logic correctly handles the core case.",
    "Nice work, this solution is close to optimal.",
    "Good instinct using the right data structure here.",
]
VERDICTS_PARTIAL = [
    "You're on the right track, but a few edge cases need attention.",
    "The core idea works, though there's room to tighten the logic.",
    "Decent first pass — let's refine a couple of details.",
]
VERDICTS_WEAK = [
    "This needs some rework — let's break down the problem again.",
    "There's a logic gap here that's worth revisiting from scratch.",
    "Let's step back and think through the approach together.",
]

TIP_POOL = [
    {"tag": "tip", "title": "Consider edge cases", "body": "What happens with an empty input or a single element? Make sure your solution handles these gracefully."},
    {"tag": "tip", "title": "Variable naming", "body": "Clear variable names make your code easier to debug and review later."},
    {"tag": "gap", "title": "Time complexity", "body": "Think about whether there's a way to solve this in fewer passes through the data."},
    {"tag": "concept", "title": "Hash maps for lookups", "body": "A hash map can often turn an O(n²) search into an O(n) one — worth considering here."},
    {"tag": "error", "title": "Off-by-one risk", "body": "Double check your loop bounds — it's easy to miss the last element or include one extra."},
    {"tag": "tip", "title": "Readability", "body": "Breaking this into smaller helper steps could make the logic easier to follow."},
]

PATTERN_POOL = [
    {"name": "Nested loop overuse", "sev": "med", "concept": "arrays"},
    {"name": "Missing edge case handling", "sev": "high", "concept": "arrays"},
    {"name": "Inefficient lookups", "sev": "med", "concept": "hash map"},
    {"name": "Off-by-one error", "sev": "low", "concept": "arrays"},
]

HINT_POOL = [
    {"hint": "Think about what information you need to remember as you scan through the input.", "question": "What if you could look up values you've already seen in O(1) time?", "concept": "Hash Map Lookup"},
    {"hint": "Consider tracking state as you iterate rather than re-scanning the array each time.", "question": "Could a single pass be enough if you remember the right thing?", "concept": "Single-Pass Iteration"},
    {"hint": "A stack-based approach often works well for matching or nested structures.", "question": "What data structure naturally handles 'last in, first out' matching?", "concept": "Stack-Based Matching"},
]


class MockAIService:
    """Drop-in replacement for AIService — same method signatures, no API calls."""

    async def analyze_code(
        self,
        code: str,
        language: str,
        problem_title: str,
        problem_desc: str,
        skill_level: str,
        skill_score: float,
    ) -> AIAnalysisResult:
        # Very rough heuristic just so feedback isn't totally disconnected from input
        has_logic = any(k in code for k in ["for", "while", "return", "=>"])
        is_stub = "pass" in code and len(code.strip().splitlines()) <= 3

        if is_stub:
            score = random.randint(5, 20)
            verdict = random.choice(VERDICTS_WEAK)
            skill_delta = -2
        elif has_logic:
            score = random.randint(60, 95)
            verdict = random.choice(VERDICTS_GOOD)
            skill_delta = random.randint(8, 15)
        else:
            score = random.randint(30, 55)
            verdict = random.choice(VERDICTS_PARTIAL)
            skill_delta = random.randint(2, 6)

        errors = [HintFeedback(**t) for t in random.sample(TIP_POOL, k=min(3, len(TIP_POOL)))]
        patterns = random.sample(PATTERN_POOL, k=random.randint(0, 2))

        return AIAnalysisResult(
            score=score,
            verdict=verdict,
            errors=errors,
            skill_delta=skill_delta,
            patterns=patterns,
            summary=f"[MOCK MODE] {random.choice(VERDICTS_GOOD)} Try the next problem to keep building momentum.",
            concepts_tested=["arrays", "hash map"],
        )

    async def get_hint(
        self,
        code: str,
        language: str,
        problem_title: str,
        problem_desc: str,
        skill_level: str,
        hint_number: int,
    ) -> HintResponse:
        pick = HINT_POOL[(hint_number - 1) % len(HINT_POOL)]
        return HintResponse(
            hint=f"[MOCK] {pick['hint']}",
            question=pick["question"],
            concept=pick["concept"],
            hint_number=hint_number,
        )

    async def answer_question(
        self,
        question: str,
        code: str,
        language: str,
        problem_title: str,
        skill_level: str,
        history: list,
    ) -> AskResponse:
        return AskResponse(
            answer=f"[MOCK MODE] That's a great question about '{problem_title}'. "
                   f"In real mode, Claude would give a tailored explanation here based on your code.",
            followup="What part of your current approach are you least confident about?",
        )


mock_ai_service = MockAIService()
