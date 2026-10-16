"""Unit tests for SkillAnalyzer.
"""

import unittest
from pathlib import Path

from modules.skill_analyzer import SkillAnalyzer


class TestSkillAnalyzer(unittest.TestCase):
    """Test suite for skill extraction and gap analysis."""

    def setUp(self):
        self.analyzer = SkillAnalyzer()

    def test_taxonomy_loaded_properly(self):
        """Ensure core taxonomy is loaded with required skills."""
        skills = self.analyzer.get_all_skills()
        self.assertGreaterEqual(len(skills), 10)
        names = self.analyzer.get_skill_names()
        for required in ["Python", "SQL", "Statistics", "Data Analysis", "Git and GitHub"]:
            self.assertIn(required, names)

    def test_extract_skills_simple(self):
        """Test basic extraction with canonical names."""
        text = "We are seeking a Python developer with solid SQL and Excel skills."
        result = self.analyzer.extract_skills_from_text(text)
        self.assertEqual(result["status"], "success")
        self.assertIn("Python", result["detected_skills"])
        self.assertIn("SQL", result["detected_skills"])
        self.assertIn("Excel", result["detected_skills"])
        self.assertNotIn("Java", result["detected_skills"])

    def test_extract_skills_synonyms_and_casing(self):
        """Test extraction via synonyms and case insensitivity."""
        text = "Experience with POSTGRES, scikit-learn, exploratory data analysis, and github workflows."
        result = self.analyzer.extract_skills_from_text(text)
        self.assertIn("SQL", result["detected_skills"])  # via postgres
        self.assertIn("Machine Learning", result["detected_skills"])  # via scikit-learn
        self.assertIn("Data Analysis", result["detected_skills"])  # via exploratory data analysis
        self.assertIn("Git and GitHub", result["detected_skills"])  # via github

    def test_empty_or_whitespace_job_description(self):
        """Test graceful handling of empty or blank strings."""
        for empty_val in ["", "   ", "\n\t", None]:
            res = self.analyzer.extract_skills_from_text(empty_val)
            self.assertEqual(res["status"], "empty_input")
            self.assertEqual(res["match_count"], 0)
            self.assertEqual(res["detected_skills"], [])

    def test_no_matching_skills_in_text(self):
        """Test text containing arbitrary content with no taxonomy matches."""
        text = "Looking for a sous chef with experience in pastry and wine pairing."
        res = self.analyzer.extract_skills_from_text(text)
        self.assertEqual(res["status"], "no_matches")
        self.assertEqual(res["match_count"], 0)
        self.assertEqual(res["detected_skills"], [])

    def test_duplicate_skills_handling(self):
        """Ensure duplicate mentions in text don't produce duplicate skill outputs."""
        text = "Python Python PYTHON python3 python scripting with python"
        res = self.analyzer.extract_skills_from_text(text)
        self.assertEqual(res["detected_skills"], ["Python"])
        self.assertEqual(len(res["detected_skills"]), 1)

    def test_skill_gap_analysis_calculations(self):
        """Test matched, missing, and match percentage calculations."""
        required = ["Python", "SQL", "Statistics", "Machine Learning"]
        student = ["Python", "SQL", "Communication", "Excel"]

        gap = self.analyzer.analyze_skill_gap(required, student)

        self.assertEqual(gap["total_required"], 4)
        self.assertEqual(gap["match_count"], 2)
        self.assertEqual(gap["matched_skills"], ["Python", "SQL"])
        self.assertEqual(gap["missing_skills"], ["Machine Learning", "Statistics"])
        self.assertEqual(gap["additional_skills"], ["Communication", "Excel"])
        self.assertEqual(gap["match_percentage"], 50.0)

    def test_skill_gap_with_duplicates_and_empty_inputs(self):
        """Ensure gap analysis cleans duplicates and handles empty sets."""
        required = ["Python", "python", "Python", "SQL"]
        student = ["SQL", "sql"]

        gap = self.analyzer.analyze_skill_gap(required, student)
        self.assertEqual(gap["total_required"], 2)  # Python, SQL
        self.assertEqual(gap["matched_skills"], ["SQL"])
        self.assertEqual(gap["missing_skills"], ["Python"])
        self.assertEqual(gap["match_percentage"], 50.0)

        # Empty required skills
        empty_gap = self.analyzer.analyze_skill_gap([], ["Python"])
        self.assertEqual(empty_gap["total_required"], 0)
        self.assertEqual(empty_gap["match_percentage"], 0.0)


if __name__ == "__main__":
    unittest.main()
