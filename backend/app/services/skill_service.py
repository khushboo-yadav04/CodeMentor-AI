"""
Skill Service — Adaptive profiling engine.

Tracks concept-level skill scores independently.
Uses Exponential Moving Average (EMA) for smooth updates.
Detects and stores recurring error patterns.
"""

from sqlalchemy.orm import Session
from app.models.models import SkillProfile, ErrorPattern, User
from app.schemas.schemas import AIAnalysisResult


# Concept → profile column mapping
CONCEPT_COLUMNS = {
    "arrays":               "arrays",
    "array":                "arrays",
    "strings":              "strings",
    "string":               "strings",
    "hash map":             "hashmaps",
    "hashmap":              "hashmaps",
    "dictionary":           "hashmaps",
    "recursion":            "recursion",
    "dynamic programming":  "dynamic_programming",
    "dp":                   "dynamic_programming",
    "trees":                "trees",
    "binary tree":          "trees",
    "bst":                  "trees",
    "graphs":               "graphs",
    "graph":                "graphs",
    "bfs":                  "graphs",
    "dfs":                  "graphs",
    "sorting":              "sorting",
    "sort":                 "sorting",
    "two pointers":         "two_pointers",
    "binary search":        "binary_search",
}

# EMA smoothing factor — higher = faster response to new submissions
EMA_ALPHA = 0.3


class SkillService:

    @staticmethod
    def get_or_create_profile(db: Session, user_id: int) -> SkillProfile:
        profile = db.query(SkillProfile).filter(
            SkillProfile.user_id == user_id
        ).first()
        if not profile:
            profile = SkillProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    @staticmethod
    def _ema_update(current: float, new_value: float) -> float:
        """Exponential Moving Average: smooth skill score update."""
        return round(EMA_ALPHA * new_value + (1 - EMA_ALPHA) * current, 2)

    @staticmethod
    def _score_to_level(score: float) -> str:
        thresholds = [(20, "beginner"), (40, "novice"), (65, "intermediate"),
                      (85, "advanced"), (101, "expert")]
        for t, label in thresholds:
            if score < t:
                return label
        return "expert"

    def update_from_analysis(
        self,
        db: Session,
        user_id: int,
        analysis: AIAnalysisResult,
        concepts_tested: list,
    ) -> SkillProfile:
        profile = self.get_or_create_profile(db, user_id)

        # Update overall score using EMA
        # Convert skill_delta (-5 to +15) to an absolute score contribution
        raw_new = min(100.0, max(0.0, profile.overall_score + analysis.skill_delta))
        profile.overall_score = self._ema_update(profile.overall_score, raw_new)
        profile.level = self._score_to_level(profile.overall_score)

        # Update concept-specific scores
        for concept in concepts_tested:
            col = CONCEPT_COLUMNS.get(concept.lower().strip())
            if col and hasattr(profile, col):
                current = getattr(profile, col) or 0.0
                # Apply skill_delta proportionally to concept score
                new_val = min(100.0, max(0.0, current + analysis.skill_delta * 0.8))
                setattr(profile, col, self._ema_update(current, new_val))

        db.commit()
        db.refresh(profile)
        return profile

    def record_patterns(
        self,
        db: Session,
        user_id: int,
        patterns: list,
    ) -> None:
        """Record or increment recurring error patterns."""
        for p in patterns:
            name = p.get("name", "")
            if not name:
                continue

            existing = db.query(ErrorPattern).filter(
                ErrorPattern.user_id == user_id,
                ErrorPattern.pattern_name == name,
                ErrorPattern.resolved == 0,
            ).first()

            if existing:
                existing.occurrences += 1
            else:
                pattern = ErrorPattern(
                    user_id=user_id,
                    pattern_name=name,
                    severity=p.get("sev", "medium"),
                    concept_area=p.get("concept", ""),
                    occurrences=1,
                )
                db.add(pattern)

        db.commit()

    def get_patterns(self, db: Session, user_id: int) -> list:
        return (
            db.query(ErrorPattern)
            .filter(ErrorPattern.user_id == user_id, ErrorPattern.resolved == 0)
            .order_by(ErrorPattern.occurrences.desc())
            .all()
        )

    def get_recommendations(self, db: Session, user_id: int) -> list:
        """Return practice topic recommendations based on lowest skill areas."""
        profile = self.get_or_create_profile(db, user_id)

        concept_scores = {
            "Arrays":               profile.arrays,
            "Strings":              profile.strings,
            "Hash Maps":            profile.hashmaps,
            "Recursion":            profile.recursion,
            "Dynamic Programming":  profile.dynamic_programming,
            "Trees":                profile.trees,
            "Graphs":               profile.graphs,
            "Sorting":              profile.sorting,
            "Two Pointers":         profile.two_pointers,
            "Binary Search":        profile.binary_search,
        }

        # Sort by score ascending — weakest areas first
        sorted_concepts = sorted(concept_scores.items(), key=lambda x: x[1])

        recommendations = []
        for concept, score in sorted_concepts[:4]:
            difficulty = (
                "easy" if score < 30
                else "medium" if score < 60
                else "hard"
            )
            recommendations.append({
                "concept": concept,
                "score": score,
                "difficulty": difficulty,
                "reason": f"Your {concept} score is {score:.0f}/100 — practice will help.",
            })

        return recommendations


skill_service = SkillService()
