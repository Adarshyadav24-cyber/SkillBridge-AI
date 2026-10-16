"""SkillBridge AI — Streamlit Web Application.

Tagline: "Don't just claim skills. Prove them."
A privacy-first, open-source AI platform for skill gap analysis,
evidence-based assessments, and personalized career roadmaps.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from config import (
    APP_ICON,
    APP_NAME,
    APP_TAGLINE,
    APP_VERSION,
    DEFAULT_OLLAMA_HOST,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_ROLES,
    EXPERIENCE_LEVELS,
    PASSING_SCORE_PERCENT,
    POPULAR_OLLAMA_MODELS,
)
from modules.ai_provider import OllamaProvider
from modules.assessment import AssessmentManager
from modules.roadmap import RoadmapGenerator
from modules.skill_analyzer import SkillAnalyzer
from modules.storage import StorageManager

# -----------------------------------------------------------------------------
# Streamlit Page Config & Design Aesthetics
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{APP_NAME} — Skill Gap & Proof Engine",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom SaaS Styling (Curated Dark Slate / High Contrast Palette)
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Header & Accent Accents */
.hero-tagline {
    font-size: 1.15rem;
    font-weight: 500;
    color: #94A3B8;
    margin-bottom: 1.5rem;
}

/* Custom Cards */
.metric-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    margin-bottom: 1rem;
}
.metric-card-title {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94A3B8;
    margin-bottom: 0.5rem;
}
.metric-card-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #F8FAFC;
}

/* Status Badges */
.badge-verified {
    background-color: #064E3B;
    color: #6EE7B7;
    border: 1px solid #059669;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    display: inline-block;
}
.badge-practice {
    background-color: #78350F;
    color: #FCD34D;
    border: 1px solid #D97706;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    display: inline-block;
}
.badge-neutral {
    background-color: #334155;
    color: #CBD5E1;
    border: 1px solid #475569;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
}

/* Roadmap Day Card */
.day-card {
    background: #0F172A;
    border: 1px solid #1E293B;
    border-left: 4px solid #6366F1;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}

/* Provenance Banner */
.provenance-ai {
    background: #1E1B4B;
    border: 1px solid #6366F1;
    color: #C7D2FE;
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 1rem;
}
.provenance-fallback {
    background: #1C1917;
    border: 1px solid #78716C;
    color: #E7E5E4;
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 1rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Module Singletons
# -----------------------------------------------------------------------------
@st.cache_resource
def get_analyzer() -> SkillAnalyzer:
    return SkillAnalyzer()


@st.cache_resource
def get_assessment_manager() -> AssessmentManager:
    return AssessmentManager(skill_analyzer=get_analyzer())


analyzer = get_analyzer()
assessment_mgr = get_assessment_manager()
StorageManager.init_session_state()

# -----------------------------------------------------------------------------
# Sidebar Navigation & AI Runtime Status
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title(f"{APP_ICON} {APP_NAME}")
    st.caption(f"v{APP_VERSION} • {APP_TAGLINE}")
    st.divider()

    # Navigation menu
    PAGES = [
        "🏠 Home / Dashboard",
        "👤 Student Profile",
        "🔍 Job Description Analysis",
        "🎯 Proof-of-Skill Assessment",
        "🗺️ Career Roadmap",
        "📊 Progress & Export",
        "ℹ️ About & Architecture",
    ]

    selected_page = st.radio(
        "Navigation",
        PAGES,
        index=PAGES.index(st.session_state.get("active_tab", PAGES[0]))
        if st.session_state.get("active_tab") in PAGES
        else 0,
        label_visibility="collapsed",
    )
    st.session_state["active_tab"] = selected_page

    st.divider()

    # Local AI Configuration (Ollama)
    st.subheader("🤖 Local AI Engine")
    use_local_ai = st.toggle("Enable Local AI (Ollama)", value=False, help="Requires Ollama running locally.")

    host_input = st.text_input(
        "Ollama Host",
        value=st.session_state.get("ollama_host", DEFAULT_OLLAMA_HOST),
        help="Default is http://localhost:11434",
    )
    st.session_state["ollama_host"] = host_input

    model_input = st.selectbox(
        "Target Model",
        POPULAR_OLLAMA_MODELS,
        index=0,
        help="Open-weight model installed locally in Ollama.",
    )
    st.session_state["ollama_model"] = model_input

    if st.button("🔌 Test Ollama Connection", use_container_width=True):
        with st.spinner("Testing local Ollama connection..."):
            test_provider = OllamaProvider(host=host_input, model=model_input, timeout=4)
            online, msg, models = test_provider.check_availability()
            if online:
                st.success(f"Online: {msg}")
                if models:
                    st.caption(f"Installed: {', '.join(models[:5])}")
            else:
                st.warning(f"Offline: {msg}")

    st.divider()
    st.caption("🔒 100% Local Execution • Zero Cloud Telemetry")


# -----------------------------------------------------------------------------
# Sample Job Description Preloader Helper
# -----------------------------------------------------------------------------
def load_sample_profile(role_name: str) -> None:
    """Preloads realistic candidate profile and job description for quick testing."""
    if role_name == "Junior Data Analyst":
        st.session_state["student_name"] = "Alex Morgan"
        st.session_state["is_anonymous"] = False
        st.session_state["target_role"] = "Junior Data Analyst"
        st.session_state["experience_level"] = "Beginner / Student (No commercial experience)"
        st.session_state["student_skills"] = ["Python", "SQL", "Excel"]
        st.session_state["job_description"] = """
We are looking for a Junior Data Analyst to join our Growth Analytics team.
Requirements:
- Strong proficiency in SQL for aggregating relational databases and generating reports.
- Working knowledge of Python (pandas, numpy) for data cleaning and exploratory data analysis.
- Experience with Excel (pivot tables, XLOOKUP) for business summaries.
- Solid grounding in Statistics (hypothesis testing, distributions, A/B testing).
- Familiarity with Git and GitHub for collaborative script version control.
- Good verbal and written Communication skills to present insights to stakeholders.
- Analytical Problem Solving mindset.
"""
    elif role_name == "Python Developer":
        st.session_state["student_name"] = "Jordan Reed"
        st.session_state["is_anonymous"] = False
        st.session_state["target_role"] = "Python Developer"
        st.session_state["experience_level"] = "Junior (0 - 1 years experience)"
        st.session_state["student_skills"] = ["Python", "Git and GitHub", "Problem Solving"]
        st.session_state["job_description"] = """
Seeking an early-career Python Developer to build backend microservices and automation workflows.
Key Responsibilities:
- Develop modular Python backend services with clean exception handling and unit tests.
- Query and optimize relational databases using SQL (PostgreSQL).
- Collaborate using Git and GitHub via feature branches and pull requests.
- Solve algorithmic logic puzzles and optimize computational complexity.
- Clear written communication for documentation and technical proposals.
"""
    elif role_name == "Machine Learning Intern":
        st.session_state["student_name"] = "Priya Sharma"
        st.session_state["is_anonymous"] = False
        st.session_state["target_role"] = "Machine Learning Intern"
        st.session_state["experience_level"] = "Beginner / Student (No commercial experience)"
        st.session_state["student_skills"] = ["Python", "Statistics", "Problem Solving"]
        st.session_state["job_description"] = """
Summer Machine Learning Intern position.
You will assist research engineers in training and evaluating predictive models.
Qualifications:
- Solid Python programming foundation with scikit-learn.
- Strong mathematical background in Statistics and probability theory.
- Hands-on experience with Machine Learning model training, cross-validation, and metrics (Precision/Recall).
- Experience performing exploratory Data Analysis and data visualization.
- Version control proficiency with Git and GitHub.
"""
    # Trigger instant analysis
    res = analyzer.extract_skills_from_text(st.session_state["job_description"])
    gap = analyzer.analyze_skill_gap(res["detected_skills"], st.session_state["student_skills"])
    st.session_state["analysis_results"] = gap
    st.session_state["user_answers"] = {}
    st.session_state["assessment_results"] = None
    st.session_state["roadmap_data"] = None


# -----------------------------------------------------------------------------
# PAGE 1: 🏠 Home / Dashboard
# -----------------------------------------------------------------------------
if selected_page == "🏠 Home / Dashboard":
    st.title("SkillBridge AI")
    st.markdown(
        f'<div class="hero-tagline">{APP_TAGLINE}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
SkillBridge AI bridges the credibility gap between self-reported resumes and verified technical capability.
Analyze real job descriptions, evaluate your practical skills via transparent deterministic quizzes,
and execute a personalized 7-day learning roadmap tailored to your target career role.
"""
    )

    # Top KPI Metrics Cards
    gap = st.session_state.get("analysis_results")
    assessment_res = st.session_state.get("assessment_results")
    roadmap = st.session_state.get("roadmap_data")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-card-title">Required Skills</div>
            <div class="metric-card-value">{gap.get('total_required', 0) if gap else 0}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-card-title">Matched Skills</div>
            <div class="metric-card-value" style="color:#6EE7B7;">{gap.get('match_count', 0) if gap else 0}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-card-title">Skill Gaps (Missing)</div>
            <div class="metric-card-value" style="color:#FCD34D;">{gap.get('missing_count', 0) if gap else 0}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with c4:
        verified_count = len(assessment_res.get("verified_skills", [])) if assessment_res else 0
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-card-title">Verified Skills</div>
            <div class="metric-card-value" style="color:#818CF8;">{verified_count}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("### ⚡ Quick Demo Launchers")
    st.write("Test the end-to-end workflow instantly with curated benchmark job postings:")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("📊 Load Junior Data Analyst Demo", use_container_width=True):
            load_sample_profile("Junior Data Analyst")
            st.session_state["active_tab"] = "🔍 Job Description Analysis"
            st.rerun()
    with col_b:
        if st.button("🐍 Load Python Developer Demo", use_container_width=True):
            load_sample_profile("Python Developer")
            st.session_state["active_tab"] = "🔍 Job Description Analysis"
            st.rerun()
    with col_c:
        if st.button("🤖 Load ML Intern Demo", use_container_width=True):
            load_sample_profile("Machine Learning Intern")
            st.session_state["active_tab"] = "🔍 Job Description Analysis"
            st.rerun()

    st.divider()

    # User Journey Steps
    st.markdown("### 🗺️ The SkillBridge Journey")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown("#### 1. Profile")
        st.caption("Declare your target role, experience level, and current self-reported skill set.")
    with s2:
        st.markdown("#### 2. Analyze")
        st.caption("Paste a job posting. Transparent taxonomy matching identifies exact missing skill gaps.")
    with s3:
        st.markdown("#### 3. Prove")
        st.caption("Take practical multiple-choice quizzes to verify competency with deterministic scoring.")
    with s4:
        st.markdown("#### 4. Accelerate")
        st.caption("Execute a structured 7-day action plan with daily micro-tasks and a capstone portfolio project.")


# -----------------------------------------------------------------------------
# PAGE 2: 👤 Student Profile
# -----------------------------------------------------------------------------
elif selected_page == "👤 Student Profile":
    st.title("👤 Student Skill Profile")
    st.markdown(
        '<div class="hero-tagline">Define your background, target role, and self-reported competencies.</div>',
        unsafe_allow_html=True,
    )

    with st.form("student_profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            anon_toggle = st.checkbox(
                "Use app anonymously (no personal name saved)",
                value=st.session_state.get("is_anonymous", True),
            )
            name_val = st.session_state.get("student_name", "Anonymous Learner")
            if anon_toggle:
                student_name = "Anonymous Learner"
                st.text_input("Candidate Name", value=student_name, disabled=True)
            else:
                student_name = st.text_input(
                    "Candidate Name",
                    value=name_val if name_val != "Anonymous Learner" else "Alex Morgan",
                )

            current_role = st.session_state.get("target_role", DEFAULT_ROLES[0])
            role_options = DEFAULT_ROLES + ["Other / Custom Role"]
            role_idx = role_options.index(current_role) if current_role in role_options else len(role_options) - 1

            selected_role = st.selectbox("Target Career Role", role_options, index=role_idx)
            if selected_role == "Other / Custom Role":
                target_role = st.text_input("Specify Target Role", value="Software Engineer")
            else:
                target_role = selected_role

        with col2:
            current_exp = st.session_state.get("experience_level", EXPERIENCE_LEVELS[0])
            exp_idx = (
                EXPERIENCE_LEVELS.index(current_exp)
                if current_exp in EXPERIENCE_LEVELS
                else 0
            )
            experience_level = st.selectbox(
                "Experience Level",
                EXPERIENCE_LEVELS,
                index=exp_idx,
            )

            all_skill_names = analyzer.get_skill_names()
            selected_skills = st.multiselect(
                "Self-Reported Skills (Select what you know)",
                options=all_skill_names,
                default=[s for s in st.session_state.get("student_skills", ["Python", "SQL"]) if s in all_skill_names],
                help="These represent self-reported claims. They will not be marked 'Verified' until you take an assessment.",
            )

        submit_profile = st.form_submit_button("💾 Save Profile Changes", use_container_width=True)

        if submit_profile:
            st.session_state["student_name"] = student_name
            st.session_state["is_anonymous"] = anon_toggle
            st.session_state["target_role"] = target_role
            st.session_state["experience_level"] = experience_level
            st.session_state["student_skills"] = selected_skills

            # Re-run gap analysis if job description is present
            if st.session_state.get("job_description"):
                res = analyzer.extract_skills_from_text(st.session_state["job_description"])
                st.session_state["analysis_results"] = analyzer.analyze_skill_gap(
                    res["detected_skills"], selected_skills
                )
            st.success("Profile saved successfully!")

    # Summary Card
    st.markdown("### Profile Summary")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.write(f"**Candidate:** `{st.session_state.get('student_name')}`")
        st.write(f"**Target Role:** `{st.session_state.get('target_role')}`")
    with sc2:
        st.write(f"**Experience Level:** `{st.session_state.get('experience_level')}`")
    with sc3:
        st.write(f"**Self-Reported Skills ({len(st.session_state.get('student_skills', []))}):**")
        pills = " ".join([f"`{s}`" for s in st.session_state.get("student_skills", [])])
        st.markdown(pills or "*None selected yet*")


# -----------------------------------------------------------------------------
# PAGE 3: 🔍 Job Description Analysis
# -----------------------------------------------------------------------------
elif selected_page == "🔍 Job Description Analysis":
    st.title("🔍 Job Description Skill Gap Analyzer")
    st.markdown(
        '<div class="hero-tagline">Paste an actual job posting to identify required skills vs your current competencies.</div>',
        unsafe_allow_html=True,
    )

    # Sample Buttons
    st.caption("Quickly insert benchmark descriptions:")
    pb1, pb2, pb3 = st.columns(3)
    if pb1.button("📋 Sample: Junior Data Analyst"):
        load_sample_profile("Junior Data Analyst")
        st.rerun()
    if pb2.button("📋 Sample: Python Developer"):
        load_sample_profile("Python Developer")
        st.rerun()
    if pb3.button("📋 Sample: ML Intern"):
        load_sample_profile("Machine Learning Intern")
        st.rerun()

    job_text = st.text_area(
        "Job Description Text",
        value=st.session_state.get("job_description", ""),
        height=220,
        placeholder="Paste full job posting text here (e.g., responsibilities, requirements, qualifications)...",
    )

    if st.button("🔎 Analyze Job Description", type="primary", use_container_width=True):
        st.session_state["job_description"] = job_text
        extraction = analyzer.extract_skills_from_text(job_text)

        if extraction["status"] == "empty_input":
            st.warning("Please paste a non-empty job description.")
            st.session_state["analysis_results"] = None
        elif extraction["status"] == "no_matches":
            st.info("No supported skills were recognized from this text. Check our taxonomy under About.")
            st.session_state["analysis_results"] = None
        else:
            gap = analyzer.analyze_skill_gap(
                extraction["detected_skills"], st.session_state.get("student_skills", [])
            )
            st.session_state["analysis_results"] = gap
            st.success(f"Successfully extracted {len(extraction['detected_skills'])} relevant skill(s)!")

    # Display Analysis Results
    gap_data = st.session_state.get("analysis_results")
    if gap_data:
        st.divider()
        st.subheader("Analysis Breakdown")

        # Match Progress Bar
        pct = gap_data["match_percentage"]
        st.markdown(f"**Role Readiness Match Rate:** `{pct}%`")
        st.progress(pct / 100.0)

        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(f"#### Required Skills ({gap_data['total_required']})")
            for s in gap_data["required_skills"]:
                st.markdown(f"- **{s}**")
        with r2:
            st.markdown(f"#### Matched Skills ({len(gap_data['matched_skills'])})")
            if gap_data["matched_skills"]:
                for s in gap_data["matched_skills"]:
                    st.markdown(f"- ✅ <span class='badge-verified'>{s}</span>", unsafe_allow_html=True)
            else:
                st.markdown("*No overlapping skills yet.*")
        with r3:
            st.markdown(f"#### Missing Skill Gaps ({len(gap_data['missing_skills'])})")
            if gap_data["missing_skills"]:
                for s in gap_data["missing_skills"]:
                    st.markdown(f"- ⚠️ <span class='badge-practice'>{s}</span>", unsafe_allow_html=True)
            else:
                st.markdown("🎉 *Zero missing skills! You meet all listed requirements.*")

        st.info(f"💡 **Transparent Matching Note:** {gap_data['summary']}")

        col_next1, col_next2 = st.columns(2)
        with col_next1:
            if st.button("🎯 Proceed to Proof-of-Skill Assessment →", use_container_width=True):
                st.session_state["active_tab"] = "🎯 Proof-of-Skill Assessment"
                st.rerun()
        with col_next2:
            if st.button("🗺️ Jump to Career Roadmap →", use_container_width=True):
                st.session_state["active_tab"] = "🗺️ Career Roadmap"
                st.rerun()


# -----------------------------------------------------------------------------
# PAGE 4: 🎯 Proof-of-Skill Assessment
# -----------------------------------------------------------------------------
elif selected_page == "🎯 Proof-of-Skill Assessment":
    st.title("🎯 Proof-of-Skill Assessment Engine")
    st.markdown(
        '<div class="hero-tagline">“Don\'t just claim skills. Prove them.” Complete deterministic quizzes to benchmark mastery.</div>',
        unsafe_allow_html=True,
    )

    # Determine skills to test
    gap_data = st.session_state.get("analysis_results")
    default_test_skills = []
    if gap_data:
        # Prioritize missing skills, then matched skills
        default_test_skills = gap_data.get("missing_skills", []) or gap_data.get("matched_skills", [])

    if not default_test_skills:
        default_test_skills = st.session_state.get("student_skills", ["Python", "SQL"])

    all_taxonomy_names = analyzer.get_skill_names()

    with st.expander("⚙️ Configure Assessment Parameters", expanded=not bool(st.session_state.get("assessment_questions"))):
        test_skills_chosen = st.multiselect(
            "Select Skills to Evaluate",
            options=all_taxonomy_names,
            default=[s for s in default_test_skills if s in all_taxonomy_names][:3] or ["Python"],
        )
        questions_per_skill = st.slider("Questions per Skill", min_value=1, max_value=4, value=2)

        if st.button("🚀 Start / Generate Quiz", type="primary", use_container_width=True):
            if not test_skills_chosen:
                st.warning("Please choose at least one skill to evaluate.")
            else:
                loaded_questions = assessment_mgr.get_questions_for_skills(
                    test_skills_chosen, limit_per_skill=questions_per_skill
                )
                st.session_state["assessment_questions"] = loaded_questions
                st.session_state["user_answers"] = {}
                st.session_state["assessment_results"] = None
                st.rerun()

    active_questions = st.session_state.get("assessment_questions", [])

    if not active_questions:
        st.info("No active quiz loaded. Select skills above and click **Start / Generate Quiz**.")
    else:
        st.write(f"**Quiz Progress:** {len(active_questions)} question(s) loaded.")

        # If not evaluated yet, show the quiz form
        if not st.session_state.get("assessment_results"):
            with st.form("assessment_quiz_form"):
                answers_in_form = {}

                for idx, q in enumerate(active_questions, start=1):
                    st.markdown(f"#### Question {idx} • `{q['skill_name']}` ({q['difficulty']})")
                    st.markdown(q["question"])

                    selected_opt = st.radio(
                        f"Choose your answer for Question {idx}:",
                        options=list(range(len(q["options"]))),
                        format_func=lambda i, opts=q["options"]: opts[i],
                        key=f"q_radio_{q['id']}",
                    )
                    answers_in_form[q["id"]] = selected_opt
                    st.divider()

                submit_quiz = st.form_submit_button("🏁 Submit Assessment for Deterministic Grading", type="primary", use_container_width=True)

                if submit_quiz:
                    eval_results = assessment_mgr.evaluate_answers(answers_in_form)
                    st.session_state["user_answers"] = answers_in_form
                    st.session_state["assessment_results"] = eval_results
                    st.rerun()

        # If evaluated, show comprehensive scorecard and explanations
        else:
            eval_results = st.session_state["assessment_results"]
            st.subheader("📊 Assessment Scorecard")

            score = eval_results["overall_score_percent"]
            pass_status = score >= PASSING_SCORE_PERCENT

            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("Overall Score", f"{score}%", delta=f"{eval_results['total_correct']}/{eval_results['total_answered']} Correct")
            with col_s2:
                status_label = "✅ Benchmark Met" if pass_status else "⚠️ Needs Review"
                st.metric("Benchmark Status", status_label, help=f"Passing threshold is {PASSING_SCORE_PERCENT}%.")
            with col_s3:
                st.metric("Skills Verified", len(eval_results["verified_skills"]))

            # Skill breakdown table
            st.markdown("### Per-Skill Verification Breakdown")
            breakdown_rows = []
            for sk, data in eval_results["skill_breakdown"].items():
                breakdown_rows.append({
                    "Skill": sk,
                    "Score (%)": f"{data['score_percent']}%",
                    "Score Ratio": f"{data['correct_answers']} / {data['total_questions']}",
                    "Evidence Status": "Verified (Pass)" if data["is_verified"] else "Needs Practice",
                })
            df_breakdown = pd.DataFrame(breakdown_rows)
            st.dataframe(df_breakdown, use_container_width=True, hide_index=True)

            # Detailed explanations for each question
            st.markdown("### 📝 Detailed Answer Explanations")
            for idx, r in enumerate(eval_results["detailed_results"], start=1):
                icon = "✅" if r["is_correct"] else "❌"
                with st.expander(f"{icon} Question {idx}: {r['skill_name']} — {'Correct' if r['is_correct'] else 'Incorrect'}", expanded=not r["is_correct"]):
                    st.markdown(r["question_text"])
                    st.write(f"**Your Answer:** {r['user_selected_text']}")
                    if not r["is_correct"]:
                        st.write(f"**Correct Answer:** {r['correct_text']}")
                    st.info(f"**Explanation:** {r['explanation']}")

            col_r1, col_r2 = st.columns(2)
            with col_r1:
                if st.button("🔄 Retake Quiz", use_container_width=True):
                    st.session_state["user_answers"] = {}
                    st.session_state["assessment_results"] = None
                    st.rerun()
            with col_r2:
                if st.button("🗺️ Generate Custom 7-Day Roadmap →", type="primary", use_container_width=True):
                    st.session_state["active_tab"] = "🗺️ Career Roadmap"
                    st.rerun()


# -----------------------------------------------------------------------------
# PAGE 5: 🗺️ Career Roadmap
# -----------------------------------------------------------------------------
elif selected_page == "🗺️ Career Roadmap":
    st.title("🗺️ Personalized 7-Day Career Roadmap")
    st.markdown(
        '<div class="hero-tagline">Actionable micro-tasks, time estimations, and concrete evidence deliverables to bridge your skill gap.</div>',
        unsafe_allow_html=True,
    )

    gap_data = st.session_state.get("analysis_results") or {}
    assessment_data = st.session_state.get("assessment_results") or {}

    missing = gap_data.get("missing_skills", [])
    needs_practice = assessment_data.get("needs_practice_skills", [])
    verified = assessment_data.get("verified_skills", [])

    target_role = st.session_state.get("target_role", "Junior Data Analyst")
    experience = st.session_state.get("experience_level", "Beginner / Student")

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        if st.button("⚡ Generate / Regenerate 7-Day Roadmap", type="primary", use_container_width=True):
            with st.spinner("Compiling pedagogical roadmap with practical tasks and evidence requirements..."):
                ai_prov = OllamaProvider(
                    host=st.session_state.get("ollama_host", DEFAULT_OLLAMA_HOST),
                    model=st.session_state.get("ollama_model", DEFAULT_OLLAMA_MODEL),
                    timeout=st.session_state.get("ollama_timeout", 8),
                )
                roadmap_gen = RoadmapGenerator(ai_provider=ai_prov)
                roadmap_result = roadmap_gen.generate_roadmap(
                    target_role=target_role,
                    experience_level=experience,
                    missing_skills=missing,
                    skills_needing_practice=needs_practice,
                    verified_skills=verified,
                    use_ai=use_local_ai,
                )
                st.session_state["roadmap_data"] = roadmap_result
                st.session_state["completed_tasks"] = set()
                st.success("7-Day Roadmap generated!")

    roadmap = st.session_state.get("roadmap_data")

    if not roadmap:
        st.info("Click **Generate / Regenerate 7-Day Roadmap** above to create your structured learning plan.")
    else:
        # Provenance Banner (Strict Hackathon Requirement: Transparent attribution)
        source = roadmap.get("source", "Fallback Engine")
        if "Ollama" in source:
            st.markdown(
                f'<div class="provenance-ai">🤖 <b>AI Provider Active:</b> {source} — {roadmap.get("generation_note", "")}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="provenance-fallback">⚙️ <b>Engine Active:</b> {source} — {roadmap.get("generation_note", "")}</div>',
                unsafe_allow_html=True,
            )

        # Roadmap Metadata
        m1, m2, m3 = st.columns(3)
        with m1:
            st.write(f"**Target Role:** `{roadmap.get('target_role')}`")
        with m2:
            st.write(f"**Experience Level:** `{roadmap.get('experience_level')}`")
        with m3:
            p_skills = ", ".join(roadmap.get("priority_skills", [])) or "Role Core Fundamentals"
            st.write(f"**Priority Focus:** `{p_skills}`")

        st.divider()

        # Interactive 7 Days
        st.subheader("📅 7-Day Action Plan")
        completed_set = st.session_state.get("completed_tasks", set())

        for d in roadmap.get("days", []):
            day_num = d["day"]
            is_done = day_num in completed_set

            with st.container():
                st.markdown(
                    f"""
                <div class="day-card" style="border-left-color: {'#10B981' if is_done else '#6366F1'};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#F8FAFC;">Day {day_num}: {d['title']}</h4>
                        <span class="badge-neutral">⏱️ {d['estimated_time']}</span>
                    </div>
                    <p style="margin-top:0.5rem; color:#CBD5E1;"><b>🎯 Objective:</b> {d['objective']}</p>
                    <p style="color:#CBD5E1;"><b>🛠️ Practical Task:</b> {d['practical_task']}</p>
                    <p style="color:#94A3B8; font-size:0.9rem;"><b>📦 Expected Output / Evidence:</b> <code>{d['expected_evidence']}</code></p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                check_done = st.checkbox(
                    f"Mark Day {day_num} as Completed",
                    value=is_done,
                    key=f"check_day_{day_num}",
                )
                if check_done and day_num not in completed_set:
                    completed_set.add(day_num)
                    st.session_state["completed_tasks"] = completed_set
                    st.rerun()
                elif not check_done and day_num in completed_set:
                    completed_set.remove(day_num)
                    st.session_state["completed_tasks"] = completed_set
                    st.rerun()

        # Portfolio Project Blueprint
        portfolio = roadmap.get("portfolio_project")
        if portfolio:
            st.divider()
            st.subheader("🏆 Recommended Capstone Portfolio Project")
            st.markdown(f"### {portfolio.get('title')}")
            st.write(f"**Problem Solved:** {portfolio.get('problem_statement')}")
            st.write(f"**Solution Architecture:** {portfolio.get('solution_overview')}")

            st.write("**Tech Stack:**")
            tech_badges = " ".join([f"`{t}`" for t in portfolio.get("tech_stack", [])])
            st.markdown(tech_badges)

            st.write("**Implementation Milestones:**")
            for m in portfolio.get("milestones", []):
                st.markdown(f"- 📌 {m}")

            st.info(f"💡 **Recruiter Portfolio Tip:** {portfolio.get('portfolio_tip', '')}")


# -----------------------------------------------------------------------------
# PAGE 6: 📊 Progress & Export
# -----------------------------------------------------------------------------
elif selected_page == "📊 Progress & Export":
    st.title("📊 Progress Dashboard & Privacy Export")
    st.markdown(
        '<div class="hero-tagline">Track completed learning milestones and export your local Career Proof Dossier.</div>',
        unsafe_allow_html=True,
    )

    gap_data = st.session_state.get("analysis_results")
    assessment_data = st.session_state.get("assessment_results")
    roadmap_data = st.session_state.get("roadmap_data")
    completed_set = st.session_state.get("completed_tasks", set())

    # Roadmap Progress
    total_days = len(roadmap_data.get("days", [])) if roadmap_data else 7
    done_count = len(completed_set)
    done_pct = round((done_count / total_days * 100), 1) if total_days > 0 else 0.0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Roadmap Completion", f"{done_pct}%", f"{done_count}/{total_days} Days Completed")
    with c2:
        verified_cnt = len(assessment_data.get("verified_skills", [])) if assessment_data else 0
        st.metric("Assessed & Verified Skills", verified_cnt)
    with c3:
        needs_work_cnt = len(assessment_data.get("needs_practice_skills", [])) if assessment_data else 0
        st.metric("Skills Needing Practice", needs_work_cnt)

    st.progress(done_pct / 100.0)
    st.divider()

    # Evidence vs Claim Comparison Matrix
    st.subheader("📋 Evidence vs Claim Verification Matrix")
    st.caption("Distinguishes unverified self-reported skills from evidence-tested skills.")

    all_reported = st.session_state.get("student_skills", [])
    verified_skills = assessment_data.get("verified_skills", []) if assessment_data else []
    practice_skills = assessment_data.get("needs_practice_skills", []) if assessment_data else []

    comparison_data = []
    for s in analyzer.get_skill_names():
        is_reported = "Yes" if s in all_reported else "No"
        if s in verified_skills:
            status = "✅ Verified (Proof on Record)"
        elif s in practice_skills:
            status = "⚠️ Needs Practice (< 70%)"
        else:
            status = "⚪ Untested (Self-Report Only)"

        if is_reported == "Yes" or s in verified_skills or s in practice_skills:
            comparison_data.append({
                "Skill": s,
                "Self-Reported Claim": is_reported,
                "Audit Status": status,
            })

    if comparison_data:
        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
    else:
        st.info("No profile skills entered yet.")

    st.divider()

    # Export Section
    st.subheader("📥 Export Career Proof Dossier")
    st.write("Export your complete profile, gap analysis, assessment scorecard, and roadmap as local files:")

    markdown_report = StorageManager.generate_markdown_report(
        student_name=st.session_state.get("student_name", "Anonymous Learner"),
        target_role=st.session_state.get("target_role", "Junior Data Analyst"),
        experience_level=st.session_state.get("experience_level", "Beginner"),
        gap_results=gap_data,
        assessment_results=assessment_data,
        roadmap_data=roadmap_data,
    )

    csv_data = StorageManager.generate_csv_export(gap_data, assessment_data)

    json_backup = json.dumps(
        {
            "student_name": st.session_state.get("student_name"),
            "target_role": st.session_state.get("target_role"),
            "experience_level": st.session_state.get("experience_level"),
            "student_skills": st.session_state.get("student_skills"),
            "analysis_results": gap_data,
            "assessment_results": assessment_data,
            "roadmap_data": roadmap_data,
        },
        indent=2,
    )

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.download_button(
            label="📄 Download Report (.MD)",
            data=markdown_report,
            file_name="skillbridge_career_dossier.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_d2:
        st.download_button(
            label="📊 Download Skill Data (.CSV)",
            data=csv_data,
            file_name="skillbridge_skills_audit.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_d3:
        st.download_button(
            label="💾 Download State Backup (.JSON)",
            data=json_backup,
            file_name="skillbridge_state_backup.json",
            mime="application/json",
            use_container_width=True,
        )

    # Privacy Guarantee Card
    with st.expander("🔒 Privacy & Storage Architecture Notice"):
        st.markdown(StorageManager.get_privacy_statement())


# -----------------------------------------------------------------------------
# PAGE 7: ℹ️ About & Architecture
# -----------------------------------------------------------------------------
elif selected_page == "ℹ️ About & Architecture":
    st.title("ℹ️ About SkillBridge AI")
    st.markdown(
        f'<div class="hero-tagline">{APP_TAGLINE} — Open-Source AI Hackathon Solution</div>',
        unsafe_allow_html=True,
    )

    tab_overview, tab_arch, tab_ollama, tab_license = st.tabs([
        "📖 Project Overview",
        "🏗️ System Architecture",
        "🦙 Ollama Local Setup",
        "⚖️ Open Source & Model Licenses",
    ])

    with tab_overview:
        st.markdown(
            """
### The Problem
Traditional tech recruiting relies on self-reported resume bullet points. Students struggle to identify exactly what
skills employers are asking for, while hiring managers are inundated with keyword-stuffed resumes they cannot verify.

### The Solution: SkillBridge AI
SkillBridge AI establishes **evidence-based skill credibility**:
1. **Transparent Keyword & Synonym Extraction:** Transparent parsing derived from an open taxonomy.
2. **Proof-of-Skill Assessments:** Objective MCQs with deterministic scoring and per-question pedagogical rationale.
3. **Structured 7-Day Roadmap:** Micro-tasks yielding concrete evidence artifacts (code scripts, PRs, gists).
4. **Privacy-Preserving Local AI:** Optional local model execution via Ollama (`llama3.2`, `mistral`, `phi3`) with 100% offline fallback.
"""
        )

    with tab_arch:
        st.markdown(
            """
### System Architecture Diagram

```
+------------------------------------------------------------------+
|                     SkillBridge AI Architecture                  |
+------------------------------------------------------------------+
                               |
            +------------------+------------------+
            |                                     |
            v                                     v
  [ Streamlit UI ]                     [ Local Storage / State ]
  - Profile & Job Parser                - Session State Memory
  - Quiz Assessment Runner              - Markdown / CSV Export
  - Roadmap & Dashboard Tracker         - Privacy Guarantee
            |                                     |
            +------------------+------------------+
                               |
            +------------------+------------------+
            |                                     |
            v                                     v
  [ Core Deterministic Engine ]        [ Local AI Engine (Optional) ]
  - skill_analyzer.py (Taxonomy)       - OllamaProvider (localhost:11434)
  - assessment.py (Question Bank)      - llama3.2 / mistral / phi3
  - roadmap.py (Fallback Engine)       - Transparent Provenance Tags
```

- **Clean Decoupling:** Core skill extraction and grading execute with zero network requests.
- **Fail-Safe Design:** If Ollama is offline or times out, the deterministic engine automatically takes over without user disruption.
"""
        )

    with tab_arch:
        st.write("Supported Taxonomy Skills:")
        tax_skills = analyzer.get_all_skills()
        tax_rows = [{"Skill": s["name"], "Category": s["category"], "Synonyms": ", ".join(s["synonyms"][:4])} for s in tax_skills]
        st.dataframe(pd.DataFrame(tax_rows), use_container_width=True, hide_index=True)

    with tab_ollama:
        st.markdown(
            """
### Setting Up Local Ollama (Optional)

SkillBridge AI works completely offline without Ollama, but you can enable real-time local AI generation:

1. **Install Ollama:**
   - Download for Windows from [ollama.com](https://ollama.com).
2. **Pull a lightweight model:**
   ```bash
   ollama pull llama3.2:1b
   # or
   ollama pull llama3.2
   ```
3. **Run Ollama:**
   ```bash
   ollama serve
   ```
4. **Enable in SkillBridge AI:**
   - In the left sidebar, toggle **Enable Local AI (Ollama)**.
   - Click **Test Ollama Connection** to verify status.
"""
        )

    with tab_license:
        st.markdown(
            """
### License & Model Provenance

- **Software License:** MIT License. Free for open-source modification and distribution.
- **Local Model Licenses (when selected by user):**
  - **Llama 3.2 (Meta):** Distributed under the [Llama 3.2 Community License Agreement](https://llama.meta.com/llama3/license/). Permitted for academic and commercial use under 700M monthly active users.
  - **Mistral (Mistral AI):** Distributed under Apache 2.0.
  - **Phi-3 (Microsoft):** Distributed under MIT License.
- **Deterministic Question Bank & Taxonomy:** Included under the project's MIT License.
"""
        )
