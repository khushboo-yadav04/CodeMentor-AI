"""
AI Service — the brain of CodeMentor AI.

Responsibilities:
  1. Build adaptive prompts based on skill level (PromptBuilder)
  2. Call Claude API via LangChain
  3. Parse structured JSON responses
  4. Update skill deltas
"""

import json
import re
from typing import List, Optional
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
from app.config import settings
from app.schemas.schemas import (
    AIAnalysisResult, HintFeedback, HintResponse, AskResponse, ChatMessage
)


# ─── Skill Level Thresholds ───────────────────────────────────────────────────

SKILL_LEVELS = [
    (20,  "beginner"),
    (40,  "novice"),
    (65,  "intermediate"),
    (85,  "advanced"),
    (101, "expert"),
]


def score_to_level(score: float) -> str:
    for threshold, label in SKILL_LEVELS:
        if score < threshold:
            return label
    return "expert"


# ─── PromptBuilder ────────────────────────────────────────────────────────────

class PromptBuilder:
    """
    Builds adaptive system prompts calibrated to the student's skill level.
    Higher levels get more technical depth; beginners get plain-language guidance.
    """

    LEVEL_INSTRUCTIONS = {
        "beginner": (
            "Use very simple language. Avoid jargon. Explain every technical term. "
            "Focus on logic and basic syntax. Give encouraging, step-by-step guidance. "
            "Never show more than 2 errors at once — it overwhelms beginners."
        ),
        "novice": (
            "Use plain language with light technical terms. Explain concepts with "
            "analogies. Point out logic errors and basic algorithmic patterns. "
            "Mention time complexity only if it is a key issue."
        ),
        "intermediate": (
            "Use technical language freely. Discuss algorithmic complexity (Big-O). "
            "Point out edge cases, off-by-one errors, and design pattern issues. "
            "Suggest more optimal approaches when applicable."
        ),
        "advanced": (
            "Be rigorous. Analyze time and space complexity deeply. Discuss trade-offs "
            "between approaches. Highlight subtle bugs, memory issues, and scalability "
            "concerns. Suggest alternative data structures or algorithms."
        ),
        "expert": (
            "Peer-level review. Be concise and precise. Focus on micro-optimisations, "
            "language-specific idioms, and production-readiness. Point out any anti-patterns "
            "and discuss their systemic implications."
        ),
    }

    @staticmethod
    def analysis_prompt(
        problem_title: str,
        problem_desc: str,
        language: str,
        skill_level: str,
        skill_score: float,
    ) -> str:
        level_instructions = PromptBuilder.LEVEL_INSTRUCTIONS.get(
            skill_level, PromptBuilder.LEVEL_INSTRUCTIONS["beginner"]
        )

        return f"""You are CodeMentor AI, a personalized adaptive coding tutor.

Student profile:
- Skill level: {skill_level} ({skill_score:.0f}/100)
- Language: {language}

Adaptation instructions for this student:
{level_instructions}

Problem: "{problem_title}"
Description: {problem_desc}

Analyze the student's code submission. Be Socratic — guide without spoiling the solution.

Respond ONLY with valid JSON (no markdown, no backticks, no explanation outside JSON):
{{
  "score": <integer 0–100, code quality>,
  "verdict": "<one sentence overall verdict>",
  "errors": [
    {{
      "tag": "<error|gap|tip|concept>",
      "title": "<short 4-word title>",
      "body": "<2-sentence explanation adapted to {skill_level} level>"
    }}
  ],
  "skill_delta": <integer -5 to +15, how much to adjust skill score>,
  "patterns": [
    {{"name": "<error pattern name>", "sev": "<high|med|low>", "concept": "<concept area>"}}
  ],
  "concepts_tested": ["<concept1>", "<concept2>"],
  "summary": "<2 encouraging sentences with a specific next step>"
}}

Rules:
- Maximum 4 items in errors array
- skill_delta: +12–15 for elegant/correct, +5–10 for mostly correct, 0–4 for partial, -2 to -5 for fundamentally wrong
- tag meanings: error=bug found, gap=missing knowledge, tip=improvement suggestion, concept=concept to study
- Always include at least one "tip" even for good code"""

    @staticmethod
    def hint_prompt(
        problem_title: str,
        problem_desc: str,
        language: str,
        skill_level: str,
        hint_number: int,
    ) -> str:
        specificity = {
            1: "Very vague — just point to the general approach. Don't name algorithms.",
            2: "Slightly more specific — mention the data structure category.",
            3: "Specific — name the algorithm/pattern but not how to implement it.",
            4: "Concrete — describe the key step without writing code.",
            5: "Very concrete — walk through the approach in plain English.",
        }.get(hint_number, "Very concrete — walk through the approach in plain English.")

        level_instructions = PromptBuilder.LEVEL_INSTRUCTIONS.get(
            skill_level, PromptBuilder.LEVEL_INSTRUCTIONS["beginner"]
        )

        return f"""You are a Socratic coding tutor. Never give away the answer directly.

Student profile: {skill_level}
Adaptation: {level_instructions}

Problem: "{problem_title}"
Hint #{hint_number} requested. Specificity for this hint: {specificity}

Respond ONLY with valid JSON (no markdown):
{{
  "hint": "<one focused hint at the described specificity level>",
  "question": "<one Socratic question to guide their thinking>",
  "concept": "<the concept being tested, e.g. Hash Map Lookup>"
}}"""

    @staticmethod
    def ask_prompt(
        problem_title: str,
        language: str,
        skill_level: str,
    ) -> str:
        level_instructions = PromptBuilder.LEVEL_INSTRUCTIONS.get(
            skill_level, PromptBuilder.LEVEL_INSTRUCTIONS["beginner"]
        )

        return f"""You are CodeMentor AI, answering student questions about their code.

Student profile: {skill_level} | Language: {language}
Adaptation: {level_instructions}

Problem context: "{problem_title}"

Answer the student's question concisely and Socratically. 
Do NOT write their code for them. Guide, don't spoil.

Respond ONLY with valid JSON (no markdown):
{{
  "answer": "<clear 2-3 sentence answer adapted to skill level>",
  "followup": "<one follow-up question to deepen their thinking>"
}}"""


# ─── AI Service ───────────────────────────────────────────────────────────────

class AIService:
    def __init__(self):
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set — cannot use real AI service.")
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=settings.anthropic_api_key,
            max_tokens=1024,
            temperature=0.3,
        )

    def _parse_json(self, raw: str) -> dict:
        """Strip markdown fences and parse JSON safely."""
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        return json.loads(cleaned)

    async def analyze_code(
        self,
        code: str,
        language: str,
        problem_title: str,
        problem_desc: str,
        skill_level: str,
        skill_score: float,
    ) -> AIAnalysisResult:
        system_prompt = PromptBuilder.analysis_prompt(
            problem_title, problem_desc, language, skill_level, skill_score
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"My {language} code:\n```{language}\n{code}\n```"
            ),
        ]

        response = await self.llm.ainvoke(messages)
        data = self._parse_json(response.content)

        errors = [
            HintFeedback(
                tag=e.get("tag", "tip"),
                title=e.get("title", ""),
                body=e.get("body", ""),
            )
            for e in data.get("errors", [])
        ]

        return AIAnalysisResult(
            score=int(data.get("score", 0)),
            verdict=data.get("verdict", ""),
            errors=errors,
            skill_delta=int(data.get("skill_delta", 0)),
            patterns=data.get("patterns", []),
            summary=data.get("summary", ""),
            concepts_tested=data.get("concepts_tested", []),
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
        system_prompt = PromptBuilder.hint_prompt(
            problem_title, problem_desc, language, skill_level, hint_number
        )

        context = (
            f"Problem description:\n{problem_desc}\n\n"
            f"Student's current code:\n```{language}\n{code}\n```"
            if code.strip()
            else f"Problem description:\n{problem_desc}\n\nStudent hasn't written code yet."
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=context),
        ]

        response = await self.llm.ainvoke(messages)
        data = self._parse_json(response.content)

        return HintResponse(
            hint=data.get("hint", ""),
            question=data.get("question", ""),
            concept=data.get("concept", ""),
            hint_number=hint_number,
        )

    async def answer_question(
        self,
        question: str,
        code: str,
        language: str,
        problem_title: str,
        skill_level: str,
        history: List[ChatMessage],
    ) -> AskResponse:
        system_prompt = PromptBuilder.ask_prompt(
            problem_title, language, skill_level
        )

        # Build conversation history for multi-turn context
        messages = [SystemMessage(content=system_prompt)]
        for msg in history[-6:]:  # Keep last 6 turns (3 pairs)
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                from langchain.schema import AIMessage
                messages.append(AIMessage(content=msg.content))

        user_content = (
            f"My code:\n```{language}\n{code}\n```\n\nQuestion: {question}"
            if code.strip()
            else f"Question: {question}"
        )
        messages.append(HumanMessage(content=user_content))

        response = await self.llm.ainvoke(messages)
        data = self._parse_json(response.content)

        return AskResponse(
            answer=data.get("answer", ""),
            followup=data.get("followup", ""),
        )


# Singleton — only created if real AI is actually requested elsewhere
ai_service = None
if not settings.use_mock_ai:
    ai_service = AIService()
