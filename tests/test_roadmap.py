"""Unit tests for RoadmapGenerator and AI provider fallback resilience.
"""

import unittest
from unittest.mock import MagicMock

from modules.ai_provider import OllamaProvider
from modules.roadmap import RoadmapGenerator


class TestRoadmapGenerator(unittest.TestCase):
    """Test suite for 7-day roadmap generation, fallback logic, and AI decoupling."""

    def setUp(self):
        # AI provider with simulated unreachable host
        self.mock_offline_ai = OllamaProvider(host="http://localhost:99999", timeout=1)
        self.generator = RoadmapGenerator(ai_provider=self.mock_offline_ai)

    def test_fallback_roadmap_structure(self):
        """Verify fallback roadmap generates a complete 7-day plan with required keys."""
        roadmap = self.generator.generate_roadmap(
            target_role="Junior Data Analyst",
            experience_level="Beginner / Student",
            missing_skills=["SQL", "Data Analysis"],
            skills_needing_practice=["Python"],
            verified_skills=["Communication"],
            use_ai=False,
        )

        self.assertEqual(len(roadmap["days"]), 7, "Must contain exactly 7 days")
        self.assertEqual(roadmap["source"], "Deterministic Fallback Engine")

        for day in roadmap["days"]:
            self.assertIn("day", day)
            self.assertIn("title", day)
            self.assertIn("objective", day)
            self.assertIn("practical_task", day)
            self.assertIn("estimated_time", day)
            self.assertIn("expected_evidence", day)
            self.assertFalse(day["is_completed"])

    def test_portfolio_project_tailoring(self):
        """Test portfolio project blueprint generation for Data Analyst vs ML role."""
        da_roadmap = self.generator.generate_roadmap(
            target_role="Junior Data Analyst",
            experience_level="Beginner",
            missing_skills=["SQL"],
            skills_needing_practice=[],
            verified_skills=[],
            use_ai=False,
        )
        da_project = da_roadmap.get("portfolio_project")
        self.assertIsNotNone(da_project)
        self.assertIn("Analytics", da_project["title"])
        self.assertGreaterEqual(len(da_project["milestones"]), 3)

        ml_roadmap = self.generator.generate_roadmap(
            target_role="Machine Learning Intern",
            experience_level="Student",
            missing_skills=["Machine Learning"],
            skills_needing_practice=[],
            verified_skills=[],
            use_ai=False,
        )
        ml_project = ml_roadmap.get("portfolio_project")
        self.assertIsNotNone(ml_project)
        self.assertIn("Pipeline", ml_project["title"])

    def test_ai_unavailable_graceful_fallback(self):
        """Ensure when Ollama is offline or unavailable, fallback activates seamlessly."""
        # use_ai is True, but Ollama server is offline
        roadmap = self.generator.generate_roadmap(
            target_role="Python Developer",
            experience_level="Self-Taught",
            missing_skills=["Python", "Git and GitHub"],
            skills_needing_practice=[],
            verified_skills=[],
            use_ai=True,
        )

        # Must not raise error, must return 7 days, and must tag source honestly as Fallback
        self.assertEqual(len(roadmap["days"]), 7)
        self.assertEqual(roadmap["source"], "Deterministic Fallback Engine")
        self.assertIn("Deterministic and reliable", roadmap["generation_note"])

    def test_mock_successful_ai_response(self):
        """Verify successful AI generation response parsing and provenance tagging."""
        mock_ai = MagicMock(spec=OllamaProvider)
        mock_ai.check_availability.return_value = (True, "Ollama online", ["llama3.2"])

        fake_ai_json = """
        {
          "days": [
            {"day": 1, "title": "Day 1 AI", "skill": "Python", "objective": "Obj 1", "practical_task": "Task 1", "estimated_time": "45m", "expected_evidence": "Gist"},
            {"day": 2, "title": "Day 2 AI", "skill": "Python", "objective": "Obj 2", "practical_task": "Task 2", "estimated_time": "45m", "expected_evidence": "Gist"},
            {"day": 3, "title": "Day 3 AI", "skill": "SQL", "objective": "Obj 3", "practical_task": "Task 3", "estimated_time": "45m", "expected_evidence": "Gist"},
            {"day": 4, "title": "Day 4 AI", "skill": "SQL", "objective": "Obj 4", "practical_task": "Task 4", "estimated_time": "45m", "expected_evidence": "Gist"},
            {"day": 5, "title": "Day 5 AI", "skill": "Git", "objective": "Obj 5", "practical_task": "Task 5", "estimated_time": "45m", "expected_evidence": "Gist"},
            {"day": 6, "title": "Day 6 AI", "skill": "Git", "objective": "Obj 6", "practical_task": "Task 6", "estimated_time": "45m", "expected_evidence": "Gist"},
            {"day": 7, "title": "Day 7 AI", "skill": "Project", "objective": "Obj 7", "practical_task": "Task 7", "estimated_time": "45m", "expected_evidence": "Gist"}
          ],
          "portfolio_project": {
            "title": "AI Driven Microservice",
            "problem_statement": "Real time latency",
            "solution_overview": "FastAPI + Redis",
            "tech_stack": ["Python", "FastAPI"],
            "milestones": ["M1", "M2", "M3"],
            "portfolio_tip": "Benchmark RPS"
          }
        }
        """
        mock_ai.generate_completion.return_value = (True, fake_ai_json, "Local Ollama AI (llama3.2)")

        ai_generator = RoadmapGenerator(ai_provider=mock_ai)
        roadmap = ai_generator.generate_roadmap(
            target_role="Python Developer",
            experience_level="Junior",
            missing_skills=["Python"],
            skills_needing_practice=[],
            verified_skills=[],
            use_ai=True,
        )

        self.assertEqual(len(roadmap["days"]), 7)
        self.assertEqual(roadmap["source"], "Local Ollama AI (llama3.2)")
        self.assertEqual(roadmap["days"][0]["title"], "Day 1 AI")


if __name__ == "__main__":
    unittest.main()
