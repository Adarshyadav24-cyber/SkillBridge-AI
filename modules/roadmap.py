"""Personalized 7-day Career Roadmap generator for SkillBridge AI.

Generates structured, practical daily micro-tasks, evidence requirements,
and portfolio project blueprints using either local Ollama AI or robust fallback templates.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from modules.ai_provider import OllamaProvider


class RoadmapGenerator:
    """Generates personalized 7-day learning roadmaps and portfolio project ideas."""

    def __init__(self, ai_provider: Optional[OllamaProvider] = None):
        self.ai_provider = ai_provider or OllamaProvider()

    def generate_roadmap(
        self,
        target_role: str,
        experience_level: str,
        missing_skills: List[str],
        skills_needing_practice: List[str],
        verified_skills: List[str],
        use_ai: bool = True,
    ) -> Dict[str, Any]:
        """Generates a complete 7-day roadmap with daily practical tasks and evidence.

        Attempts AI generation via local Ollama if requested, otherwise uses fallback generator.
        """
        priority_skills = list(dict.fromkeys(missing_skills + skills_needing_practice))
        if not priority_skills:
            # If no gaps, deepen existing role skills
            priority_skills = verified_skills[:3] or ["Data Analysis", "Problem Solving", "Git and GitHub"]

        # Attempt AI generation if enabled
        if use_ai:
            ai_available, _, _ = self.ai_provider.check_availability()
            if ai_available:
                ai_roadmap = self._generate_with_ai(
                    target_role=target_role,
                    experience_level=experience_level,
                    priority_skills=priority_skills,
                    verified_skills=verified_skills,
                )
                if ai_roadmap:
                    return ai_roadmap

        # Fallback generator
        return self._generate_fallback_roadmap(
            target_role=target_role,
            experience_level=experience_level,
            priority_skills=priority_skills,
            verified_skills=verified_skills,
        )

    def _generate_fallback_roadmap(
        self,
        target_role: str,
        experience_level: str,
        priority_skills: List[str],
        verified_skills: List[str],
    ) -> Dict[str, Any]:
        """Deterministic, battle-tested 7-day roadmap generation."""
        # Curated skill-to-task catalog
        skill_task_library: Dict[str, List[Dict[str, str]]] = {
            "Python": [
                {
                    "title": "Python Data Structures & List Comprehensions",
                    "objective": "Master writing idiomatic Python for data transformation and memory efficiency.",
                    "task": "Build a CLI script that parses a multi-line CSV string, cleans column whitespace, and outputs a summarized dict.",
                    "time": "45 mins",
                    "evidence": "A clean `.py` script on GitHub with type annotations and docstrings.",
                },
                {
                    "title": "Python Error Handling & Modular Scripting",
                    "objective": "Implement robust exception handling and unit tests for edge cases.",
                    "task": "Refactor a script to handle `KeyError`, `ValueError`, and missing file paths gracefully.",
                    "time": "60 mins",
                    "evidence": "A script featuring `try/except` blocks paired with 3 passing pytest test functions.",
                },
            ],
            "SQL": [
                {
                    "title": "SQL Multi-Table Aggregation & JOINs",
                    "objective": "Master filtering with WHERE vs HAVING and joining relational entities.",
                    "task": "Write an SQLite or PostgreSQL script joining `customers` and `orders` to find top 5 buyers by total spend.",
                    "time": "50 mins",
                    "evidence": "An `.sql` script containing commented query explanations and query execution output.",
                },
                {
                    "title": "SQL Window Functions & Ranking",
                    "objective": "Compute running totals, moving averages, and ranks with `DENSE_RANK()` and `OVER()`.",
                    "task": "Create a monthly revenue report showing rank of each product category within its region.",
                    "time": "60 mins",
                    "evidence": "A documented SQL query showing before/after results on a mock dataset.",
                },
            ],
            "Data Analysis": [
                {
                    "title": "Exploratory Data Analysis (EDA) with Pandas",
                    "objective": "Identify distributions, null rates, and correlations in messy tabular data.",
                    "task": "Load an open dataset (e.g. Kaggle sales/housing), impute missing values, and print summary statistics.",
                    "time": "60 mins",
                    "evidence": "A Jupyter Notebook (`.ipynb`) with markdown cell interpretations of 3 key business findings.",
                },
                {
                    "title": "Data Visualization & Outlier Detection",
                    "objective": "Create informative box plots, histograms, and scatter plots that reveal trends.",
                    "task": "Generate a multi-panel Matplotlib/Seaborn visual showing outlier boundaries via 1.5 * IQR.",
                    "time": "45 mins",
                    "evidence": "Exported PNG visualization chart with clear titles, labels, and an executive caption.",
                },
            ],
            "Statistics": [
                {
                    "title": "Descriptive Statistics & Skewness",
                    "objective": "Distinguish mean, median, mode, and variance in skewed distributions.",
                    "task": "Calculate and compare mean vs median across positive-skew sample data to explain outlier sensitivity.",
                    "time": "40 mins",
                    "evidence": "A short markdown note detailing when median is preferred over mean with numeric proof.",
                },
                {
                    "title": "A/B Testing & Hypothesis Testing",
                    "objective": "Formulate null/alternative hypotheses and interpret p-values and confidence intervals.",
                    "task": "Simulate a two-sample t-test comparing conversion rates of two website button variants.",
                    "time": "55 mins",
                    "evidence": "Python snippet running `scipy.stats.ttest_ind` with a written non-technical conclusion.",
                },
            ],
            "Machine Learning": [
                {
                    "title": "Train-Test Split & Baseline Classifier",
                    "objective": "Prevent data leakage and build a disciplined scikit-learn baseline model.",
                    "task": "Fit a Logistic Regression or Decision Tree model using a pipeline with proper feature scaling.",
                    "time": "60 mins",
                    "evidence": "Code snippet demonstrating `Pipeline` and `train_test_split` with zero leakage.",
                },
                {
                    "title": "Classification Metrics & Error Analysis",
                    "objective": "Evaluate models using Precision, Recall, F1-Score, and Confusion Matrix.",
                    "task": "Plot a confusion matrix and calculate F1-score on an imbalanced binary target dataset.",
                    "time": "60 mins",
                    "evidence": "A markdown report explaining why raw accuracy failed and how recall was optimized.",
                },
            ],
            "Git and GitHub": [
                {
                    "title": "Git Branching, Rebasing & Clean Commits",
                    "objective": "Follow professional Git workflows with feature branches and atomic commits.",
                    "task": "Initialize a local git repo, create a `feature/data-pipeline` branch, make 3 atomic commits, and merge.",
                    "time": "30 mins",
                    "evidence": "Screenshot of terminal output showing `git log --oneline --graph`.",
                },
                {
                    "title": "Writing Industry-Standard Pull Requests",
                    "objective": "Document code changes with clear problem-solution context for reviewers.",
                    "task": "Push a project to GitHub, open a PR with a description template, problem statement, and test checklist.",
                    "time": "40 mins",
                    "evidence": "Public GitHub Pull Request URL with descriptive markdown summary.",
                },
            ],
            "Excel": [
                {
                    "title": "Advanced XLOOKUP & Dynamic Formulas",
                    "objective": "Replace fragile VLOOKUPs with two-way XLOOKUP and dynamic array formulas.",
                    "task": "Build a dynamic pricing lookup model matching product codes across disparate sheets.",
                    "time": "40 mins",
                    "evidence": "An Excel sheet (`.xlsx`) demonstrating XLOOKUP with `#N/A` handling.",
                },
                {
                    "title": "Interactive Pivot Tables & KPI Slicers",
                    "objective": "Build automated executive summary summaries with pivot tables.",
                    "task": "Aggregate monthly sales by region and product line, adding interactive slicers for quick filtering.",
                    "time": "45 mins",
                    "evidence": "Interactive spreadsheet dashboard with drill-down capability.",
                },
            ],
            "Java": [
                {
                    "title": "Java Object-Oriented Principles & Interfaces",
                    "objective": "Implement encapsulation, abstraction, and interfaces in Java.",
                    "task": "Write an interface `PaymentGateway` and implement `CreditCardPayment` and `StripePayment` classes.",
                    "time": "60 mins",
                    "evidence": "Compilable `.java` source files with unit tests verifying polymorphism.",
                },
            ],
            "Problem Solving": [
                {
                    "title": "Algorithmic Complexity & Big-O Optimization",
                    "objective": "Analyze time and space complexity and eliminate nested O(N^2) loops.",
                    "task": "Refactor a duplicate-finding algorithm from O(N^2) nested scan to O(N) hash set lookup.",
                    "time": "45 mins",
                    "evidence": "Before/after benchmark showing execution time reduction on 50,000 items.",
                },
            ],
            "Communication": [
                {
                    "title": "Translating Technical Metrics to Business Value",
                    "objective": "Communicate complex analytical findings to non-technical stakeholders.",
                    "task": "Write a 1-page executive summary memo explaining an analytical model's ROI and operational impact.",
                    "time": "45 mins",
                    "evidence": "A clean 1-page PDF or Markdown executive briefing memo.",
                },
            ],
        }

        # Build 7 distinct days
        days: List[Dict[str, Any]] = []
        clean_priority = priority_skills or ["Data Analysis", "Python", "SQL", "Git and GitHub"]

        for day_num in range(1, 8):
            skill = clean_priority[(day_num - 1) % len(clean_priority)]
            task_options = skill_task_library.get(skill)

            if task_options:
                chosen_task = task_options[(day_num - 1) % len(task_options)]
                title = f"{skill}: {chosen_task['title']}"
                objective = chosen_task["objective"]
                task = chosen_task["task"]
                est_time = chosen_task["time"]
                evidence = chosen_task["evidence"]
            else:
                title = f"{skill}: Core Competency Deep Dive"
                objective = f"Solidify fundamental conceptual and applied knowledge in {skill}."
                task = f"Complete 2 hands-on implementation exercises applying {skill} to a realistic scenario."
                est_time = "60 mins"
                evidence = f"Code snippet or documentation summarizing {skill} implementation and learnings."

            days.append(
                {
                    "day": day_num,
                    "title": title,
                    "skill": skill,
                    "objective": objective,
                    "practical_task": task,
                    "estimated_time": est_time,
                    "expected_evidence": evidence,
                    "is_completed": False,
                }
            )

        # Portfolio Project tailored to target role
        portfolio_project = self._get_fallback_portfolio_project(target_role, priority_skills)

        return {
            "target_role": target_role,
            "experience_level": experience_level,
            "priority_skills": priority_skills,
            "days": days,
            "portfolio_project": portfolio_project,
            "source": "Deterministic Fallback Engine",
            "generation_note": (
                "Generated via SkillBridge's curated, role-aligned pedagogical engine. "
                "Deterministic and reliable with no cloud latency."
            ),
        }

    def _get_fallback_portfolio_project(
        self, target_role: str, priority_skills: List[str]
    ) -> Dict[str, Any]:
        """Provides a complete portfolio project blueprint aligned with target role."""
        role_lower = target_role.lower()

        if "data analyst" in role_lower or "bi" in role_lower:
            return {
                "title": "E-Commerce Customer Retention & Churn Analytics Dashboard",
                "problem_statement": (
                    "Retail companies struggle to identify which customers are at risk of churning "
                    "before they leave, leading to lost revenue."
                ),
                "solution_overview": (
                    "Perform end-to-end cohort analysis and RFM (Recency, Frequency, Monetary) segmentation "
                    "on public retail transactions, generating executive dashboards with actionable retention plays."
                ),
                "tech_stack": ["Python (Pandas, Matplotlib)", "SQL (PostgreSQL/SQLite)", "Streamlit or Tableau", "Git"],
                "milestones": [
                    "Milestone 1: Clean raw transactions and calculate RFM customer scores using SQL queries.",
                    "Milestone 2: Build cohort retention curves in Python to isolate month-over-month dropoff.",
                    "Milestone 3: Package insights into an interactive Streamlit dashboard with KPI filters.",
                    "Milestone 4: Write a recruiter-friendly README with architecture diagram, key insights, and live demo link.",
                ],
                "portfolio_tip": (
                    "Recruiters love business outcomes: Lead your project description with 'Identified $45K potential "
                    "churn risk across 1,200 dormant accounts' rather than just 'I used Pandas'."
                ),
            }
        elif "machine learning" in role_lower:
            return {
                "title": "Credit Risk Default Prediction Pipeline with Explainability",
                "problem_statement": (
                    "Financial lenders need transparent, auditable machine learning systems to score loan default risks "
                    "while avoiding demographic bias and data leakage."
                ),
                "solution_overview": (
                    "Design a production-ready credit scoring pipeline using scikit-learn, featuring calibrated probabilities "
                    "and SHAP feature importance for regulatory explainability."
                ),
                "tech_stack": ["Python", "scikit-learn", "Pandas", "SHAP", "FastAPI or Streamlit", "GitHub Actions"],
                "milestones": [
                    "Milestone 1: Exploratory analysis on LendingClub or German Credit dataset with out-of-fold cross validation.",
                    "Milestone 2: Feature engineering pipeline (handling missing data, target encoding, class weights).",
                    "Milestone 3: Model benchmarking (Logistic Regression vs LightGBM/RandomForest) with PR-AUC evaluation.",
                    "Milestone 4: Model interpretability layer generating individual loan approval rationale reports.",
                ],
                "portfolio_tip": (
                    "Highlight production robustness: Show that your model handles missing fields gracefully without crashing."
                ),
            }
        else:
            # Python Developer or general
            return {
                "title": "Automated Job Market Intelligence & Skill Scraper API",
                "problem_statement": (
                    "Job seekers and bootcamps lack real-time visibility into shifting industry technology demands."
                ),
                "solution_overview": (
                    "A modular backend service that ingests tech job listings, extracts skill requirements using regex "
                    "and NLP, and provides a REST API with aggregated trends."
                ),
                "tech_stack": ["Python 3.11", "SQLite / PostgreSQL", "FastAPI / Requests", "Pytest", "Docker / GitHub"],
                "milestones": [
                    "Milestone 1: Build robust parsing module with error handling, rate limiting, and schema validation.",
                    "Milestone 2: Relational database schema storing normalized skills, companies, and postings.",
                    "Milestone 3: RESTful endpoints returning skill frequency trends by seniority level.",
                    "Milestone 4: Automated CI/CD pipeline running pytest unit tests on every pull request.",
                ],
                "portfolio_tip": (
                    "Include an ASCII architecture diagram in your GitHub README showing request flow and database schema."
                ),
            }

    def _generate_with_ai(
        self,
        target_role: str,
        experience_level: str,
        priority_skills: List[str],
        verified_skills: List[str],
    ) -> Optional[Dict[str, Any]]:
        """Invokes local Ollama AI to generate an enriched roadmap."""
        prompt = f"""
You are a senior tech career coach. Create a practical 7-day learning roadmap for a student aiming for the role: "{target_role}".
Experience Level: {experience_level}
Target Skills needing work: {', '.join(priority_skills)}
Already Verified Skills: {', '.join(verified_skills) if verified_skills else 'None yet'}

Respond ONLY with valid JSON in this exact structure:
{{
  "days": [
    {{
      "day": 1,
      "title": "Title here",
      "skill": "{priority_skills[0] if priority_skills else 'Core Skill'}",
      "objective": "Clear learning objective",
      "practical_task": "Actionable task taking 45-60 mins",
      "estimated_time": "50 mins",
      "expected_evidence": "Concrete proof artifact like a github gist or script"
    }}
  ],
  "portfolio_project": {{
    "title": "Project Title",
    "problem_statement": "Real world problem solved",
    "solution_overview": "How the solution is built",
    "tech_stack": ["Skill 1", "Skill 2"],
    "milestones": ["Milestone 1", "Milestone 2", "Milestone 3", "Milestone 4"],
    "portfolio_tip": "High impact advice for showcasing on resume"
  }}
}}
Make sure there are exactly 7 days.
"""
        success, response_text, source_name = self.ai_provider.generate_completion(
            prompt=prompt,
            system_prompt="You are an expert AI software mentor. Output strictly valid JSON without preamble.",
        )

        if not success or not response_text:
            return None

        try:
            # Clean possible markdown wrapping ```json ... ```
            clean_json = response_text.strip()
            if clean_json.startswith("```"):
                lines = clean_json.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_json = "\n".join(lines).strip()

            parsed = json.loads(clean_json)
            days = parsed.get("days", [])
            portfolio = parsed.get("portfolio_project", {})

            if len(days) >= 7 and portfolio:
                # Add completion flag
                for d in days:
                    d["is_completed"] = False
                return {
                    "target_role": target_role,
                    "experience_level": experience_level,
                    "priority_skills": priority_skills,
                    "days": days[:7],
                    "portfolio_project": portfolio,
                    "source": source_name,
                    "generation_note": f"Personalized learning plan generated in real-time by {source_name}.",
                }
        except Exception:
            # Fallback if AI JSON parse failed
            pass

        return None
