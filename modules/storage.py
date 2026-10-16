"""Session state management, export generators, and privacy guarantees for SkillBridge AI.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st


class StorageManager:
    """Manages local state, privacy disclosures, and export formats."""

    @staticmethod
    def init_session_state() -> None:
        """Initializes default Streamlit session state keys if not already present."""
        defaults = {
            "student_name": "",
            "is_anonymous": False,
            "target_role": "",
            "experience_level": "",
            "student_skills": [],
            "profile_completed": False,
            "job_description": "",
            "analysis_results": None,
            "assessment_questions": [],
            "user_answers": {},
            "assessment_results": None,
            "roadmap_data": None,
            "completed_tasks": set(),
            "ollama_host": "http://localhost:11434",
            "ollama_model": "llama3.2",
            "ollama_timeout": 8,
            "active_tab": "🏠 Home / Dashboard",
        }

        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

    @staticmethod
    def generate_markdown_report(
        student_name: str,
        target_role: str,
        experience_level: str,
        gap_results: Optional[Dict[str, Any]],
        assessment_results: Optional[Dict[str, Any]],
        roadmap_data: Optional[Dict[str, Any]],
    ) -> str:
        """Compiles a complete, recruiter-ready Career Proof Dossier in Markdown format."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"# SkillBridge AI — Career Proof & Roadmap Dossier",
            f"**Candidate:** {student_name}  ",
            f"**Target Role:** {target_role}  ",
            f"**Experience Level:** {experience_level}  ",
            f"**Generated At:** {timestamp}  ",
            f"**Tagline:** *Don't just claim skills. Prove them.*  ",
            "",
            "---",
            "",
            "## 1. Skill Gap Analysis",
        ]

        if gap_results:
            lines.extend([
                f"- **Match Rate:** {gap_results.get('match_percentage', 0)}%",
                f"- **Total Required Skills:** {gap_results.get('total_required', 0)}",
                f"- **Matched Skills ({len(gap_results.get('matched_skills', []))}):** {', '.join(gap_results.get('matched_skills', [])) or 'None'}",
                f"- **Missing Skills ({len(gap_results.get('missing_skills', []))}):** {', '.join(gap_results.get('missing_skills', [])) or 'None'}",
                f"- **Self-Reported Additional Skills:** {', '.join(gap_results.get('additional_skills', [])) or 'None'}",
                "",
                f"> **Analysis Note:** {gap_results.get('summary', '')}",
            ])
        else:
            lines.append("No job description analysis recorded.")

        lines.extend([
            "",
            "---",
            "",
            "## 2. Proof-of-Skill Assessment Results",
        ])

        if assessment_results and assessment_results.get("total_answered", 0) > 0:
            lines.extend([
                f"- **Overall Assessment Score:** {assessment_results.get('overall_score_percent', 0)}%",
                f"- **Questions Completed:** {assessment_results.get('total_answered', 0)} ({assessment_results.get('total_correct', 0)} correct)",
                f"- **Verified Skills (Pass >= 70%):** {', '.join(assessment_results.get('verified_skills', [])) or 'None'}",
                f"- **Skills Needing Practice (< 70%):** {', '.join(assessment_results.get('needs_practice_skills', [])) or 'None'}",
                "",
                "### Detailed Skill Verification Breakdown",
                "| Skill | Score | Status | Questions |",
                "| :--- | :--- | :--- | :--- |",
            ])
            for skill, data in assessment_results.get("skill_breakdown", {}).items():
                status_icon = "PASS" if data.get("is_verified") else "NEEDS WORK"
                lines.append(
                    f"| {skill} | {data.get('score_percent')}% | {status_icon} | {data.get('correct_answers')}/{data.get('total_questions')} |"
                )
        else:
            lines.append("No practical skill assessment completed yet.")

        lines.extend([
            "",
            "---",
            "",
            "## 3. Personalized 7-Day Action Plan",
        ])

        if roadmap_data and roadmap_data.get("days"):
            lines.append(f"*Roadmap Engine: {roadmap_data.get('source', 'Standard')}*\n")
            for day in roadmap_data.get("days", []):
                lines.extend([
                    f"### Day {day.get('day')}: {day.get('title')}",
                    f"- **Skill Focus:** `{day.get('skill')}`",
                    f"- **Estimated Time:** {day.get('estimated_time')}",
                    f"- **Learning Objective:** {day.get('objective')}",
                    f"- **Practical Task:** {day.get('practical_task')}",
                    f"- **Evidence Required:** {day.get('expected_evidence')}",
                    "",
                ])

            portfolio = roadmap_data.get("portfolio_project")
            if portfolio:
                lines.extend([
                    "---",
                    "",
                    "## 4. Recommended Capstone Portfolio Project",
                    f"### 🏆 {portfolio.get('title')}",
                    f"**Problem Solved:** {portfolio.get('problem_statement')}\n",
                    f"**Solution Architecture:** {portfolio.get('solution_overview')}\n",
                    f"**Recommended Tech Stack:** {', '.join(portfolio.get('tech_stack', []))}\n",
                    "**Milestone Deliverables:**",
                ])
                for m in portfolio.get("milestones", []):
                    lines.append(f"- [ ] {m}")
                lines.extend([
                    "",
                    f"> **Portfolio Showcase Tip:** {portfolio.get('portfolio_tip', '')}",
                ])
        else:
            lines.append("No career roadmap generated yet.")

        lines.extend([
            "",
            "---",
            "",
            "## 5. Privacy & Verification Disclosure",
            "- All inputs and test outputs are retained locally in your browser's session memory.",
            "- Skill verification scores represent formative testing benchmarks, not accredited educational degrees.",
            "- Powered by SkillBridge AI — Open Source Career Intelligence.",
        ])

        return "\n".join(lines)

    @staticmethod
    def generate_csv_export(
        gap_results: Optional[Dict[str, Any]],
        assessment_results: Optional[Dict[str, Any]],
    ) -> str:
        """Exports tabular skill breakdown as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Skill",
            "Job Requirement Status",
            "Self-Reported",
            "Assessment Score (%)",
            "Verification Status",
        ])

        req_set = set(gap_results.get("required_skills", [])) if gap_results else set()
        stu_set = set(gap_results.get("student_skills", [])) if gap_results else set()
        skill_scores = assessment_results.get("skill_breakdown", {}) if assessment_results else {}

        all_skills = sorted(list(req_set.union(stu_set).union(set(skill_scores.keys()))))

        for s in all_skills:
            req_status = "Required" if s in req_set else "Not Explicitly Required"
            self_rep = "Yes" if s in stu_set else "No"
            if s in skill_scores:
                score = f"{skill_scores[s].get('score_percent', 0)}%"
                verif = "Verified (Pass)" if skill_scores[s].get("is_verified") else "Needs Practice"
            else:
                score = "Untested"
                verif = "Unverified"

            writer.writerow([s, req_status, self_rep, score, verif])

        return output.getvalue()

    @staticmethod
    def get_privacy_statement() -> str:
        """Returns the official SkillBridge AI privacy commitment."""
        return """
### 🔒 SkillBridge AI — Privacy & Security Architecture

SkillBridge AI was engineered from the ground up for strict candidate privacy:

1. **Local-First Data Execution:**
   - Your name, resume text, job postings, and quiz answers are maintained solely within your local session memory.
   - We do not store your data in external cloud databases.
   - We never request government IDs, credit cards, or personal addresses.

2. **No Data Snooping or Cloud Telemetry:**
   - When using local Ollama integration, all prompt evaluations occur on your machine (`localhost:11434`).
   - Zero telemetry, analytics beacons, or third-party trackers are bundled.

3. **Transparent Evaluation:**
   - Skill assessments use deterministic, auditable scoring logic stored in open JSON files.
   - We never label untested skills as verified.
        """
