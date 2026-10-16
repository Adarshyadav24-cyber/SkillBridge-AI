"""Unit tests for AssessmentManager.
"""

import unittest

from modules.assessment import AssessmentManager
from modules.skill_analyzer import SkillAnalyzer


class TestAssessmentManager(unittest.TestCase):
    """Test suite for question bank, deterministic grading, and verification logic."""

    def setUp(self):
        self.analyzer = SkillAnalyzer()
        self.assessment = AssessmentManager(skill_analyzer=self.analyzer)

    def test_question_bank_sufficiency(self):
        """Verify that all core skill categories have at least 3 practical questions."""
        skills = self.analyzer.get_skill_names()
        for skill in skills:
            questions = self.assessment.get_questions_for_skills([skill], limit_per_skill=10)
            self.assertGreaterEqual(
                len(questions),
                3,
                f"Skill '{skill}' must have at least 3 questions in question bank.",
            )

    def test_client_question_masking(self):
        """Ensure answers and explanations are omitted from questions served to users."""
        questions = self.assessment.get_questions_for_skills(["Python"], limit_per_skill=2)
        self.assertGreaterEqual(len(questions), 1)
        for q in questions:
            self.assertNotIn("correct_answer_index", q, "Secret answer must not leak to client")
            self.assertNotIn("explanation", q, "Explanation must not leak before evaluation")
            self.assertEqual(len(q["options"]), 4, "Each question must have 4 multiple-choice options")

    def test_deterministic_scoring_perfect(self):
        """Test scoring when all answers are correct."""
        py_questions = self.assessment.get_questions_for_skills(["Python"], limit_per_skill=3)
        user_answers = {}
        for q in py_questions:
            raw_q = self.assessment.get_question_by_id(q["id"])
            user_answers[q["id"]] = raw_q["correct_answer_index"]

        results = self.assessment.evaluate_answers(user_answers)
        self.assertEqual(results["total_answered"], 3)
        self.assertEqual(results["total_correct"], 3)
        self.assertEqual(results["overall_score_percent"], 100.0)
        self.assertIn("Python", results["verified_skills"])
        self.assertNotIn("Python", results["needs_practice_skills"])

    def test_deterministic_scoring_failing_threshold(self):
        """Test scoring when answers fall below the 70% passing threshold."""
        py_questions = self.assessment.get_questions_for_skills(["Python"], limit_per_skill=4)
        user_answers = {}
        # Make only 1 answer correct out of 4 (25%)
        for i, q in enumerate(py_questions):
            raw_q = self.assessment.get_question_by_id(q["id"])
            correct = raw_q["correct_answer_index"]
            user_answers[q["id"]] = correct if i == 0 else (correct + 1) % 4

        results = self.assessment.evaluate_answers(user_answers)
        self.assertEqual(results["total_answered"], 4)
        self.assertEqual(results["total_correct"], 1)
        self.assertEqual(results["overall_score_percent"], 25.0)
        self.assertIn("Python", results["needs_practice_skills"])
        self.assertNotIn("Python", results["verified_skills"])
        self.assertFalse(results["skill_breakdown"]["Python"]["is_verified"])

    def test_empty_or_invalid_answers_handling(self):
        """Test edge cases with empty submissions or out-of-range selection indexes."""
        # Empty submission
        empty_res = self.assessment.evaluate_answers({})
        self.assertEqual(empty_res["total_answered"], 0)
        self.assertEqual(empty_res["overall_score_percent"], 0.0)
        self.assertEqual(empty_res["verified_skills"], [])

        # Out-of-bounds selection index
        py_questions = self.assessment.get_questions_for_skills(["Python"], limit_per_skill=1)
        q_id = py_questions[0]["id"]
        invalid_res = self.assessment.evaluate_answers({q_id: 999})
        self.assertEqual(invalid_res["total_answered"], 1)
        self.assertEqual(invalid_res["total_correct"], 0)
        self.assertFalse(invalid_res["detailed_results"][0]["is_correct"])

    def test_untested_skills_never_labeled_verified(self):
        """Ensure untested skills are never included in verified_skills."""
        # Test only Python
        py_questions = self.assessment.get_questions_for_skills(["Python"], limit_per_skill=2)
        user_answers = {q["id"]: self.assessment.get_question_by_id(q["id"])["correct_answer_index"] for q in py_questions}
        results = self.assessment.evaluate_answers(user_answers)

        self.assertIn("Python", results["verified_skills"])
        self.assertNotIn("SQL", results["verified_skills"])
        self.assertNotIn("Java", results["verified_skills"])
        self.assertNotIn("Machine Learning", results["verified_skills"])


if __name__ == "__main__":
    unittest.main()
