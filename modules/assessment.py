"""Assessment engine for SkillBridge AI.

Handles deterministic proof-of-skill quizzes, answer masking,
score computation, and per-skill mastery verification.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import PASSING_SCORE_PERCENT, QUESTIONS_FILE, QUESTIONS_PER_SKILL
from modules.skill_analyzer import SkillAnalyzer


class AssessmentManager:
    """Manages question retrieval, test administration, and deterministic grading."""

    def __init__(
        self,
        questions_path: Optional[Path] = None,
        skill_analyzer: Optional[SkillAnalyzer] = None,
    ):
        self.questions_path = questions_path or QUESTIONS_FILE
        self.skill_analyzer = skill_analyzer or SkillAnalyzer()
        self.questions: List[Dict[str, Any]] = []
        self._questions_by_id: Dict[str, Dict[str, Any]] = {}
        self.load_questions()

    def load_questions(self) -> None:
        """Loads questions from JSON store."""
        if self.questions_path.exists():
            try:
                with open(self.questions_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.questions = data.get("questions", [])
            except Exception:
                self.questions = []
        else:
            self.questions = []

        self._questions_by_id = {q["id"]: q for q in self.questions}

    def get_question_by_id(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Returns the complete question record including correct answer."""
        return self._questions_by_id.get(question_id)

    def get_questions_for_skills(
        self, skill_names: List[str], limit_per_skill: int = QUESTIONS_PER_SKILL
    ) -> List[Dict[str, Any]]:
        """Retrieves questions matching given skill names.

        NOTE: Omits correct_answer_index and explanation to prevent client-side answer leaking.
        """
        selected_questions: List[Dict[str, Any]] = []

        # Map skill names to skill_ids
        skill_id_map: Dict[str, str] = {}
        for name in skill_names:
            skill = self.skill_analyzer.get_skill_by_name(name)
            if skill:
                skill_id_map[skill["id"]] = skill["name"]
            else:
                # Direct match fallback
                skill_id_map[name.lower().replace(" ", "_")] = name

        for skill_id, skill_name in skill_id_map.items():
            matching = [q for q in self.questions if q.get("skill_id") == skill_id]
            for q in matching[:limit_per_skill]:
                # Safe client copy without revealing solution
                safe_q = {
                    "id": q["id"],
                    "skill_id": q["skill_id"],
                    "skill_name": skill_name,
                    "question": q["question"],
                    "options": list(q["options"]),
                    "difficulty": q.get("difficulty", "Intermediate"),
                }
                selected_questions.append(safe_q)

        return selected_questions

    def evaluate_answers(self, user_answers: Dict[str, int]) -> Dict[str, Any]:
        """Evaluates submitted answers deterministically.

        user_answers: dict mapping question_id -> chosen option index (0..3).
        Returns comprehensive breakdown with per-skill evidence and explanations.
        """
        if not user_answers:
            return {
                "total_answered": 0,
                "total_correct": 0,
                "overall_score_percent": 0.0,
                "skill_breakdown": {},
                "detailed_results": [],
                "summary": "No questions answered.",
                "verified_skills": [],
                "needs_practice_skills": [],
            }

        detailed_results: List[Dict[str, Any]] = []
        skill_stats: Dict[str, Dict[str, int]] = {}

        for q_id, chosen_idx in user_answers.items():
            raw_q = self._questions_by_id.get(q_id)
            if not raw_q:
                continue

            skill_id = raw_q.get("skill_id", "general")
            # Resolve canonical skill name
            skill_info = self.skill_analyzer.get_skill_by_id(skill_id)
            skill_name = skill_info["name"] if skill_info else skill_id.replace("_", " ").title()

            if skill_name not in skill_stats:
                skill_stats[skill_name] = {"total": 0, "correct": 0}

            skill_stats[skill_name]["total"] += 1

            correct_idx = raw_q.get("correct_answer_index", -1)
            is_correct = chosen_idx == correct_idx

            if is_correct:
                skill_stats[skill_name]["correct"] += 1

            options = raw_q.get("options", [])
            user_choice_text = (
                options[chosen_idx]
                if 0 <= chosen_idx < len(options)
                else "Invalid Selection / Skipped"
            )
            correct_choice_text = (
                options[correct_idx]
                if 0 <= correct_idx < len(options)
                else "Unknown"
            )

            detailed_results.append(
                {
                    "question_id": q_id,
                    "skill_name": skill_name,
                    "question_text": raw_q.get("question", ""),
                    "options": options,
                    "user_selected_index": chosen_idx,
                    "user_selected_text": user_choice_text,
                    "correct_index": correct_idx,
                    "correct_text": correct_choice_text,
                    "is_correct": is_correct,
                    "explanation": raw_q.get("explanation", "No explanation available."),
                }
            )

        total_answered = len(detailed_results)
        total_correct = sum(1 for r in detailed_results if r["is_correct"])
        overall_score = (
            round((total_correct / total_answered * 100), 1) if total_answered > 0 else 0.0
        )

        skill_breakdown: Dict[str, Dict[str, Any]] = {}
        verified_skills: List[str] = []
        needs_practice_skills: List[str] = []

        for skill, stats in skill_stats.items():
            tot = stats["total"]
            corr = stats["correct"]
            pct = round((corr / tot * 100), 1) if tot > 0 else 0.0
            is_verified = pct >= PASSING_SCORE_PERCENT

            skill_breakdown[skill] = {
                "total_questions": tot,
                "correct_answers": corr,
                "score_percent": pct,
                "is_verified": is_verified,
                "status": "Verified (Pass)" if is_verified else "Needs Practice",
            }

            if is_verified:
                verified_skills.append(skill)
            else:
                needs_practice_skills.append(skill)

        summary = (
            f"Completed {total_answered} question(s) across {len(skill_stats)} skill(s). "
            f"Overall score: {overall_score}% ({total_correct}/{total_answered} correct). "
            f"Verified {len(verified_skills)} skill(s); {len(needs_practice_skills)} skill(s) need further review."
        )

        return {
            "total_answered": total_answered,
            "total_correct": total_correct,
            "overall_score_percent": overall_score,
            "skill_breakdown": skill_breakdown,
            "detailed_results": detailed_results,
            "summary": summary,
            "verified_skills": sorted(verified_skills),
            "needs_practice_skills": sorted(needs_practice_skills),
        }
