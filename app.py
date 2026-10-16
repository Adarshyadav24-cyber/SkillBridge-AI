"""SkillBridge AI — Ultra-Professional 3D Animated Web Application.

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

# -----------------------------------------------------------------------------
# Ultra-Professional 3D Animated Design System (CSS)
# -----------------------------------------------------------------------------
ULTRA_3D_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* Global Font & Canvas Background */
html, body, [class*="css"] {
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
    color: #F1F5F9;
}

/* Base App Dark Holographic Mesh Background */
.stApp {
    background: radial-gradient(circle at 10% 15%, rgba(99, 102, 241, 0.12) 0%, transparent 45%),
                radial-gradient(circle at 85% 85%, rgba(6, 182, 212, 0.10) 0%, transparent 45%),
                radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.98) 0%, #070B14 100%) !important;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Keyframe Animations */
@keyframes floatSlow {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-7px) rotate(0.4deg); }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.25), inset 0 1px 1px rgba(255,255,255,0.2); }
    100% { box-shadow: 0 0 35px rgba(99, 102, 241, 0.65), inset 0 1px 2px rgba(255,255,255,0.4); }
}

@keyframes shimmerText {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes gradientBorder {
    0% { border-color: rgba(99, 102, 241, 0.3); }
    50% { border-color: rgba(6, 182, 212, 0.5); }
    100% { border-color: rgba(99, 102, 241, 0.3); }
}

/* 3D Holographic Hero Title */
.hero-title-3d {
    font-size: 2.85rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 25%, #818CF8 55%, #38BDF8 85%, #C084FC 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmerText 8s ease infinite;
    margin-bottom: 0.25rem;
    filter: drop-shadow(0 8px 16px rgba(99, 102, 241, 0.3));
}

.hero-tagline-3d {
    font-size: 1.25rem;
    font-weight: 500;
    color: #94A3B8;
    margin-bottom: 1.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

.hero-tagline-3d span {
    color: #38BDF8;
    font-weight: 700;
}

/* 3D Elevated Cards */
.card-3d {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.65) 0%, rgba(15, 23, 42, 0.85) 100%);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.5), inset 0 1px 1px 0 rgba(255, 255, 255, 0.12);
    transition: transform 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.35s ease, border-color 0.35s ease;
    margin-bottom: 1.25rem;
    position: relative;
}

.card-3d:hover {
    transform: translateY(-5px) perspective(1000px) rotateX(1deg);
    box-shadow: 0 25px 50px -12px rgba(99, 102, 241, 0.3), inset 0 1px 2px 0 rgba(255, 255, 255, 0.25);
    border-color: rgba(99, 102, 241, 0.45);
}

/* 3D Metric KPI Cards */
.metric-card-3d {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    box-shadow: 0 12px 30px -10px rgba(0, 0, 0, 0.6), inset 0 1px 1px 0 rgba(255, 255, 255, 0.1);
    transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}

.metric-card-3d::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #6366F1, #38BDF8);
    opacity: 0.8;
}

.metric-card-3d:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 20px 40px -10px rgba(99, 102, 241, 0.4);
    border-color: rgba(99, 102, 241, 0.5);
}

.metric-title-3d {
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94A3B8;
    margin-bottom: 0.4rem;
}

.metric-value-3d {
    font-size: 2.2rem;
    font-weight: 900;
    color: #F8FAFC;
    line-height: 1.1;
    text-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
}

/* 3D Interactive Badges */
.badge-3d-verified {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.35) 100%);
    color: #6EE7B7;
    border: 1px solid rgba(16, 185, 129, 0.5);
    box-shadow: 0 0 15px rgba(16, 185, 129, 0.25), inset 0 1px 1px rgba(255, 255, 255, 0.2);
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

.badge-3d-gap {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.35) 100%);
    color: #FCD34D;
    border: 1px solid rgba(245, 158, 11, 0.5);
    box-shadow: 0 0 15px rgba(245, 158, 11, 0.2), inset 0 1px 1px rgba(255, 255, 255, 0.2);
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

.badge-3d-neutral {
    background: linear-gradient(135deg, rgba(51, 65, 85, 0.5) 0%, rgba(30, 41, 59, 0.6) 100%);
    color: #CBD5E1;
    border: 1px solid rgba(71, 85, 105, 0.5);
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
}

/* 3D Roadmap Day Card */
.day-card-3d {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(20, 30, 55, 0.85) 100%);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-left: 5px solid #6366F1;
    border-radius: 12px;
    padding: 1.25rem 1.4rem;
    box-shadow: 0 10px 25px -8px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255,255,255,0.1);
    transition: all 0.3s ease;
    margin-bottom: 1rem;
}

.day-card-3d:hover {
    transform: translateX(4px) translateY(-2px);
    border-color: rgba(99, 102, 241, 0.6);
    box-shadow: 0 15px 35px -10px rgba(99, 102, 241, 0.25);
}

.day-card-3d.completed {
    border-left-color: #10B981;
    border-color: rgba(16, 185, 129, 0.3);
    background: linear-gradient(135deg, rgba(6, 78, 59, 0.2) 0%, rgba(15, 23, 42, 0.9) 100%);
}

/* 3D Provenance Badges */
.provenance-ai-3d {
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(49, 46, 129, 0.9) 100%);
    border: 1px solid #818CF8;
    color: #E0E7FF;
    padding: 10px 16px;
    border-radius: 10px;
    font-size: 0.88rem;
    font-weight: 600;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

.provenance-fallback-3d {
    background: linear-gradient(135deg, rgba(28, 25, 23, 0.8) 0%, rgba(41, 37, 36, 0.9) 100%);
    border: 1px solid #78716C;
    color: #F5F5F4;
    padding: 10px 16px;
    border-radius: 10px;
    font-size: 0.88rem;
    font-weight: 600;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* 3D Button Depth Styling */
div.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 6px 15px -4px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.15) !important;
}

div.stButton > button:hover {
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 12px 25px -6px rgba(99, 102, 241, 0.4), inset 0 1px 2px rgba(255, 255, 255, 0.25) !important;
}

div.stButton > button:active {
    transform: translateY(1px) scale(0.99) !important;
}

/* User Alert Callout 3D */
.user-alert-3d {
    background: linear-gradient(135deg, rgba(67, 56, 202, 0.15) 0%, rgba(15, 23, 42, 0.85) 100%);
    border: 1px solid rgba(99, 102, 241, 0.4);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 20px -5px rgba(0,0,0,0.4);
}
</style>
"""
st.markdown(ULTRA_3D_CSS, unsafe_allow_html=True)


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
    st.markdown(
        f'<div style="font-size:1.6rem; font-weight:800; color:#F8FAFC;">{APP_ICON} {APP_NAME}</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"v{APP_VERSION} • {APP_TAGLINE}")
    st.divider()

    # User Profile Status Pill
    is_profile_ready = bool(st.session_state.get("profile_completed", False))
    candidate_name = st.session_state.get("student_name", "").strip() or (
        "Anonymous Learner" if st.session_state.get("is_anonymous") else "Profile Unset"
    )
    skill_count = len(st.session_state.get("student_skills", []))

    if is_profile_ready and (candidate_name != "Profile Unset" or st.session_state.get("is_anonymous")):
        st.markdown(
            f"""
            <div style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.4); border-radius:10px; padding:10px 12px; margin-bottom:12px;">
                <div style="font-size:0.75rem; text-transform:uppercase; color:#6EE7B7; font-weight:700;">Active Candidate</div>
                <div style="font-size:1.05rem; font-weight:800; color:#F8FAFC;">👤 {candidate_name}</div>
                <div style="font-size:0.8rem; color:#94A3B8;">{skill_count} declared skill(s) locked in</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background:rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.4); border-radius:10px; padding:10px 12px; margin-bottom:12px;">
                <div style="font-size:0.75rem; text-transform:uppercase; color:#FCD34D; font-weight:700;">Profile Status</div>
                <div style="font-size:0.95rem; font-weight:800; color:#F8FAFC;">⚠️ Profile Not Initialized</div>
                <div style="font-size:0.8rem; color:#94A3B8;">Fill in your details in Student Profile</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
        with st.spinner("Pinging Ollama..."):
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
# PAGE 1: 🏠 Home / Dashboard
# -----------------------------------------------------------------------------
if selected_page == "🏠 Home / Dashboard":
    st.markdown('<div class="hero-title-3d">SkillBridge AI</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-tagline-3d"><span>“Don\'t just claim skills. Prove them.”</span> — Evidence-Based Career Intelligence</div>',
        unsafe_allow_html=True,
    )

    # User Profile Status Banner
    is_ready = bool(st.session_state.get("profile_completed", False))
    user_skills = st.session_state.get("student_skills", [])
    user_name = st.session_state.get("student_name", "").strip() or (
        "Anonymous" if st.session_state.get("is_anonymous") else None
    )

    if not is_ready or not user_skills:
        st.markdown(
            """
            <div class="user-alert-3d">
                <div style="font-size:1.15rem; font-weight:800; color:#F8FAFC; margin-bottom:0.3rem;">
                    👋 Welcome! Your Personal Profile is Fresh & Empty.
                </div>
                <div style="color:#CBD5E1; font-size:0.95rem; margin-bottom:0.85rem;">
                    SkillBridge AI does <b>not</b> assume random mock data. We evaluate <b>only your actual profile</b>
                    and the specific job descriptions you submit.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("⚡ Setup My Profile Now (Add Skills & Role) →", type="primary"):
            st.session_state["active_tab"] = "👤 Student Profile"
            st.rerun()
    else:
        st.markdown(
            f"""
            <div class="user-alert-3d" style="border-color:rgba(16,185,129,0.5); background:linear-gradient(135deg, rgba(6,78,59,0.2) 0%, rgba(15,23,42,0.85) 100%);">
                <div style="font-size:1.1rem; font-weight:800; color:#6EE7B7;">
                    ✅ Profile Active for {user_name or 'You'} ({st.session_state.get('target_role', 'Target Role')})
                </div>
                <div style="color:#E2E8F0; font-size:0.9rem; margin-top:0.25rem;">
                    <b>Your Declared Skills:</b> {", ".join(user_skills)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Top KPI 3D Metric Cards
    gap = st.session_state.get("analysis_results")
    assessment_res = st.session_state.get("assessment_results")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
        <div class="metric-card-3d">
            <div class="metric-title-3d">Your Skills</div>
            <div class="metric-value-3d" style="color:#818CF8;">{len(user_skills)}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
        <div class="metric-card-3d">
            <div class="metric-title-3d">Job Required</div>
            <div class="metric-value-3d" style="color:#38BDF8;">{gap.get('total_required', 0) if gap else 0}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
        <div class="metric-card-3d">
            <div class="metric-title-3d">Skill Gaps</div>
            <div class="metric-value-3d" style="color:#FCD34D;">{gap.get('missing_count', 0) if gap else 0}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with c4:
        verified_count = len(assessment_res.get("verified_skills", [])) if assessment_res else 0
        st.markdown(
            f"""
        <div class="metric-card-3d">
            <div class="metric-title-3d">Verified Skills</div>
            <div class="metric-value-3d" style="color:#6EE7B7;">{verified_count}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("### 🗺️ The 4-Step Proof Pipeline")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(
            """
        <div class="card-3d">
            <div style="font-size:1.8rem;">👤</div>
            <h4 style="margin:0.5rem 0; color:#F8FAFC;">1. Your Profile</h4>
            <p style="font-size:0.88rem; color:#94A3B8;">Declare your actual skills, target role, and career tier.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            """
        <div class="card-3d">
            <div style="font-size:1.8rem;">🔍</div>
            <h4 style="margin:0.5rem 0; color:#F8FAFC;">2. Analyze Job</h4>
            <p style="font-size:0.88rem; color:#94A3B8;">Paste any posting to extract required skills vs your profile.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            """
        <div class="card-3d">
            <div style="font-size:1.8rem;">🎯</div>
            <h4 style="margin:0.5rem 0; color:#F8FAFC;">3. Prove Skills</h4>
            <p style="font-size:0.88rem; color:#94A3B8;">Take deterministic multiple-choice quizzes with explanations.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with s4:
        st.markdown(
            """
        <div class="card-3d">
            <div style="font-size:1.8rem;">🗺️</div>
            <h4 style="margin:0.5rem 0; color:#F8FAFC;">4. 7-Day Roadmap</h4>
            <p style="font-size:0.88rem; color:#94A3B8;">Execute daily micro-tasks yielding real evidence artifacts.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------------
# PAGE 2: 👤 Student Profile (Primary Entry Point)
# -----------------------------------------------------------------------------
elif selected_page == "👤 Student Profile":
    st.markdown('<div class="hero-title-3d">👤 Student Skill Profile</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-tagline-3d">Add your personal details and skills below. <b>SkillBridge AI processes ONLY what you provide.</b></div>',
        unsafe_allow_html=True,
    )

    with st.form("student_profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            anon_toggle = st.checkbox(
                "Use app anonymously (no personal name saved)",
                value=st.session_state.get("is_anonymous", False),
            )
            existing_name = st.session_state.get("student_name", "")
            if anon_toggle:
                student_name = "Anonymous Learner"
                st.text_input("Candidate Name", value=student_name, disabled=True)
            else:
                student_name = st.text_input(
                    "Your Full Name",
                    value=existing_name if existing_name != "Anonymous Learner" else "",
                    placeholder="Enter your name (e.g., Alex Johnson)",
                )

            current_role = st.session_state.get("target_role", "")
            role_options = [""] + DEFAULT_ROLES + ["Other / Custom Role"]
            default_role_idx = role_options.index(current_role) if current_role in role_options else 0

            selected_role = st.selectbox(
                "Target Career Role",
                role_options,
                index=default_role_idx,
                format_func=lambda x: "Select Target Role..." if x == "" else x,
            )
            if selected_role == "Other / Custom Role":
                target_role = st.text_input("Specify Target Role", value="Software Engineer")
            else:
                target_role = selected_role

        with col2:
            current_exp = st.session_state.get("experience_level", "")
            exp_options = [""] + EXPERIENCE_LEVELS
            default_exp_idx = exp_options.index(current_exp) if current_exp in exp_options else 0

            experience_level = st.selectbox(
                "Your Experience Level",
                exp_options,
                index=default_exp_idx,
                format_func=lambda x: "Select Experience Level..." if x == "" else x,
            )

            all_skill_names = analyzer.get_skill_names()
            saved_skills = st.session_state.get("student_skills", [])
            selected_skills = st.multiselect(
                "Your Current Skills (Select everything you know)",
                options=all_skill_names,
                default=[s for s in saved_skills if s in all_skill_names],
                help="Only skills you select here will be treated as your self-reported profile skills.",
            )

        submit_profile = st.form_submit_button("💾 Save & Lock In My Profile", type="primary", use_container_width=True)

        if submit_profile:
            if not anon_toggle and not student_name.strip():
                st.error("Please enter your name or check 'Use app anonymously'.")
            elif not selected_skills:
                st.warning("Please select at least 1 skill you currently know.")
            else:
                st.session_state["student_name"] = "Anonymous Learner" if anon_toggle else student_name.strip()
                st.session_state["is_anonymous"] = anon_toggle
                st.session_state["target_role"] = target_role or "General Tech Role"
                st.session_state["experience_level"] = experience_level or "Beginner / Student"
                st.session_state["student_skills"] = selected_skills
                st.session_state["profile_completed"] = True

                # If job description already exists, refresh gap analysis with user's new skills
                if st.session_state.get("job_description"):
                    res = analyzer.extract_skills_from_text(st.session_state["job_description"])
                    st.session_state["analysis_results"] = analyzer.analyze_skill_gap(
                        res["detected_skills"], selected_skills
                    )
                st.success("✅ Profile successfully saved! Your actual data is now locked in across the entire application.")
                st.rerun()

    # Clear Profile Option
    if st.session_state.get("profile_completed", False):
        col_cl1, col_cl2 = st.columns([3, 1])
        with col_cl2:
            if st.button("🗑️ Clear / Reset My Profile", use_container_width=True):
                st.session_state["student_name"] = ""
                st.session_state["is_anonymous"] = False
                st.session_state["target_role"] = ""
                st.session_state["experience_level"] = ""
                st.session_state["student_skills"] = []
                st.session_state["profile_completed"] = False
                st.session_state["analysis_results"] = None
                st.session_state["assessment_questions"] = []
                st.session_state["user_answers"] = {}
                st.session_state["assessment_results"] = None
                st.session_state["roadmap_data"] = None
                st.info("Profile cleared. You can start fresh.")
                st.rerun()

    # Active Profile Card
    if st.session_state.get("profile_completed", False):
        st.markdown("### 📋 Active Profile Verification Summary")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.write(f"**Candidate:** `{st.session_state.get('student_name')}`")
            st.write(f"**Target Role:** `{st.session_state.get('target_role')}`")
        with sc2:
            st.write(f"**Experience Level:** `{st.session_state.get('experience_level')}`")
        with sc3:
            st.write(f"**Declared Skills ({len(st.session_state.get('student_skills', []))}):**")
            pills = " ".join([f"`{s}`" for s in st.session_state.get("student_skills", [])])
            st.markdown(pills or "*None selected*")


# -----------------------------------------------------------------------------
# PAGE 3: 🔍 Job Description Analysis
# -----------------------------------------------------------------------------
elif selected_page == "🔍 Job Description Analysis":
    st.markdown('<div class="hero-title-3d">🔍 Job Description Skill Gap Analyzer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-tagline-3d">Paste any real job posting to analyze required skills against <b>your actual profile</b>.</div>',
        unsafe_allow_html=True,
    )

    user_skills = st.session_state.get("student_skills", [])
    if not user_skills:
        st.warning(
            "⚠️ **Notice:** You haven't added skills in your **Student Profile** yet. "
            "You can extract job requirements now, but to see your Matched vs Missing gaps, please declare your skills in Student Profile."
        )

    # Optional Benchmark Template Insertion (Without overwriting user profile)
    with st.expander("💡 Or Insert a Benchmark Job Posting Template (Does NOT alter your profile)"):
        st.caption("Click to insert sample job description text into the text area below:")
        tb1, tb2, tb3 = st.columns(3)
        if tb1.button("📋 Template: Data Analyst"):
            st.session_state["job_description"] = """
We are looking for a Junior Data Analyst to join our team.
Requirements:
- Strong proficiency in SQL for aggregating relational databases and generating reports.
- Working knowledge of Python (pandas, numpy) for data cleaning and exploratory data analysis.
- Experience with Excel (pivot tables, XLOOKUP) for business summaries.
- Solid grounding in Statistics (hypothesis testing, distributions, A/B testing).
- Familiarity with Git and GitHub for collaborative script version control.
- Good verbal and written Communication skills to present insights.
- Analytical Problem Solving mindset.
"""
            st.rerun()

        if tb2.button("📋 Template: Python Developer"):
            st.session_state["job_description"] = """
Seeking an early-career Python Developer to build backend microservices and automation workflows.
Key Responsibilities:
- Develop modular Python backend services with clean exception handling and unit tests.
- Query and optimize relational databases using SQL (PostgreSQL).
- Collaborate using Git and GitHub via feature branches and pull requests.
- Solve algorithmic logic puzzles and optimize computational complexity.
- Clear written communication for documentation and technical proposals.
"""
            st.rerun()

        if tb3.button("📋 Template: ML Intern"):
            st.session_state["job_description"] = """
Summer Machine Learning Intern position.
Qualifications:
- Solid Python programming foundation with scikit-learn.
- Strong mathematical background in Statistics and probability theory.
- Hands-on experience with Machine Learning model training, cross-validation, and metrics.
- Experience performing exploratory Data Analysis and data visualization.
- Version control proficiency with Git and GitHub.
"""
            st.rerun()

    job_text = st.text_area(
        "Paste Job Description Here",
        value=st.session_state.get("job_description", ""),
        height=220,
        placeholder="Paste full job posting text here (e.g., qualifications, requirements, responsibilities)...",
    )

    if st.button("🔎 Analyze Against My Profile", type="primary", use_container_width=True):
        st.session_state["job_description"] = job_text
        extraction = analyzer.extract_skills_from_text(job_text)

        if extraction["status"] == "empty_input":
            st.warning("Please paste a non-empty job description.")
            st.session_state["analysis_results"] = None
        elif extraction["status"] == "no_matches":
            st.info("No supported skills from our taxonomy were found in this text. Check About page for supported skills.")
            st.session_state["analysis_results"] = None
        else:
            gap = analyzer.analyze_skill_gap(
                extraction["detected_skills"], st.session_state.get("student_skills", [])
            )
            st.session_state["analysis_results"] = gap
            st.success(f"Extracted {len(extraction['detected_skills'])} relevant skill requirements!")

    # Display Analysis Results
    gap_data = st.session_state.get("analysis_results")
    if gap_data:
        st.divider()
        st.subheader("🎯 Skill Gap Analysis Breakdown")

        pct = gap_data["match_percentage"]
        st.markdown(f"**Readiness Match Score:** `{pct}%`")
        st.progress(pct / 100.0)

        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(f"#### Required Skills ({gap_data['total_required']})")
            for s in gap_data["required_skills"]:
                st.markdown(f"- **{s}**")
        with r2:
            st.markdown(f"#### Matched with You ({len(gap_data['matched_skills'])})")
            if gap_data["matched_skills"]:
                for s in gap_data["matched_skills"]:
                    st.markdown(f"- ✅ <span class='badge-3d-verified'>{s}</span>", unsafe_allow_html=True)
            else:
                st.markdown("*No overlapping skills yet.*")
        with r3:
            st.markdown(f"#### Missing Skill Gaps ({len(gap_data['missing_skills'])})")
            if gap_data["missing_skills"]:
                for s in gap_data["missing_skills"]:
                    st.markdown(f"- ⚠️ <span class='badge-3d-gap'>{s}</span>", unsafe_allow_html=True)
            else:
                st.markdown("🎉 *Zero missing skills! You meet all listed requirements.*")

        st.info(f"💡 **Transparent Analysis:** {gap_data['summary']}")

        col_next1, col_next2 = st.columns(2)
        with col_next1:
            if st.button("🎯 Prove Skills via Assessment →", use_container_width=True):
                st.session_state["active_tab"] = "🎯 Proof-of-Skill Assessment"
                st.rerun()
        with col_next2:
            if st.button("🗺️ View Personalized 7-Day Roadmap →", use_container_width=True):
                st.session_state["active_tab"] = "🗺️ Career Roadmap"
                st.rerun()


# -----------------------------------------------------------------------------
# PAGE 4: 🎯 Proof-of-Skill Assessment
# -----------------------------------------------------------------------------
elif selected_page == "🎯 Proof-of-Skill Assessment":
    st.markdown('<div class="hero-title-3d">🎯 Proof-of-Skill Assessment Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-tagline-3d">“Don\'t just claim skills. Prove them.” Test your knowledge with deterministic grading.</div>',
        unsafe_allow_html=True,
    )

    user_skills = st.session_state.get("student_skills", [])
    gap_data = st.session_state.get("analysis_results") or {}
    missing_skills = gap_data.get("missing_skills", [])

    # The user picks which of THEIR skills or MISSING skills to evaluate
    available_to_test = list(dict.fromkeys(missing_skills + user_skills))
    all_taxonomy = analyzer.get_skill_names()

    if not available_to_test:
        st.info(
            "💡 You haven't added profile skills or analyzed a job description yet. "
            "You can choose any skill from our taxonomy below to take an assessment."
        )
        available_to_test = all_taxonomy

    with st.expander("⚙️ Configure Quiz Parameters", expanded=not bool(st.session_state.get("assessment_questions"))):
        test_skills_chosen = st.multiselect(
            "Choose Skills to Test",
            options=all_taxonomy,
            default=[s for s in available_to_test if s in all_taxonomy][:3] or [all_taxonomy[0]],
            help="Select the specific skills you want to prove.",
        )
        questions_per_skill = st.slider("Questions per Skill", min_value=1, max_value=4, value=2)

        if st.button("🚀 Start Assessment Quiz", type="primary", use_container_width=True):
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
        st.info("Select skills above and click **Start Assessment Quiz** to begin.")
    else:
        # If not evaluated yet, show quiz form
        if not st.session_state.get("assessment_results"):
            with st.form("assessment_quiz_form"):
                answers_in_form = {}

                for idx, q in enumerate(active_questions, start=1):
                    st.markdown(
                        f"""
                        <div class="card-3d" style="border-left:4px solid #6366F1;">
                            <div style="font-weight:700; color:#818CF8; font-size:0.9rem;">
                                Question {idx} • {q['skill_name']} ({q['difficulty']})
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(q["question"])

                    selected_opt = st.radio(
                        f"Select your answer for Question {idx}:",
                        options=list(range(len(q["options"]))),
                        format_func=lambda i, opts=q["options"]: opts[i],
                        key=f"q_radio_{q['id']}",
                    )
                    answers_in_form[q["id"]] = selected_opt
                    st.divider()

                submit_quiz = st.form_submit_button("🏁 Submit for Deterministic Grading", type="primary", use_container_width=True)

                if submit_quiz:
                    eval_results = assessment_mgr.evaluate_answers(answers_in_form)
                    st.session_state["user_answers"] = answers_in_form
                    st.session_state["assessment_results"] = eval_results
                    st.rerun()

        # Scorecard
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

            # Breakdown
            st.markdown("### Per-Skill Verification Breakdown")
            breakdown_rows = []
            for sk, data in eval_results["skill_breakdown"].items():
                breakdown_rows.append({
                    "Skill": sk,
                    "Score (%)": f"{data['score_percent']}%",
                    "Score Ratio": f"{data['correct_answers']} / {data['total_questions']}",
                    "Evidence Status": "Verified (Pass)" if data["is_verified"] else "Needs Practice",
                })
            st.dataframe(pd.DataFrame(breakdown_rows), use_container_width=True, hide_index=True)

            # Detailed explanations
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
                if st.button("🗺️ Build Personalized Roadmap →", type="primary", use_container_width=True):
                    st.session_state["active_tab"] = "🗺️ Career Roadmap"
                    st.rerun()


# -----------------------------------------------------------------------------
# PAGE 5: 🗺️ Career Roadmap
# -----------------------------------------------------------------------------
elif selected_page == "🗺️ Career Roadmap":
    st.markdown('<div class="hero-title-3d">🗺️ Personalized 7-Day Career Roadmap</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-tagline-3d">Concrete micro-tasks and evidence deliverables tailored to your target role and gaps.</div>',
        unsafe_allow_html=True,
    )

    gap_data = st.session_state.get("analysis_results") or {}
    assessment_data = st.session_state.get("assessment_results") or {}

    missing = gap_data.get("missing_skills", [])
    needs_practice = assessment_data.get("needs_practice_skills", [])
    verified = assessment_data.get("verified_skills", [])

    target_role = st.session_state.get("target_role", "").strip() or "Junior Data Analyst"
    experience = st.session_state.get("experience_level", "").strip() or "Beginner / Student"

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        if st.button("⚡ Generate / Regenerate My 7-Day Roadmap", type="primary", use_container_width=True):
            with st.spinner("Synthesizing 7-day action plan..."):
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
        st.info("Click **Generate / Regenerate My 7-Day Roadmap** above to generate your customized action plan.")
    else:
        # Provenance attribution
        source = roadmap.get("source", "Fallback Engine")
        if "Ollama" in source:
            st.markdown(
                f'<div class="provenance-ai-3d">🤖 <b>AI Provider Active:</b> {source} — {roadmap.get("generation_note", "")}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="provenance-fallback-3d">⚙️ <b>Engine Active:</b> {source} — {roadmap.get("generation_note", "")}</div>',
                unsafe_allow_html=True,
            )

        m1, m2, m3 = st.columns(3)
        with m1:
            st.write(f"**Target Role:** `{roadmap.get('target_role')}`")
        with m2:
            st.write(f"**Experience Level:** `{roadmap.get('experience_level')}`")
        with m3:
            p_skills = ", ".join(roadmap.get("priority_skills", [])) or "Core Fundamentals"
            st.write(f"**Priority Focus:** `{p_skills}`")

        st.divider()

        # 7 Days Interactive Checklist
        st.subheader("📅 7-Day Action Plan")
        completed_set = st.session_state.get("completed_tasks", set())

        for d in roadmap.get("days", []):
            day_num = d["day"]
            is_done = day_num in completed_set
            completed_cls = "completed" if is_done else ""

            st.markdown(
                f"""
                <div class="day-card-3d {completed_cls}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#F8FAFC;">Day {day_num}: {d['title']}</h4>
                        <span class="badge-3d-neutral">⏱️ {d['estimated_time']}</span>
                    </div>
                    <p style="margin-top:0.5rem; color:#CBD5E1;"><b>🎯 Objective:</b> {d['objective']}</p>
                    <p style="color:#CBD5E1;"><b>🛠️ Practical Task:</b> {d['practical_task']}</p>
                    <p style="color:#94A3B8; font-size:0.9rem;"><b>📦 Expected Evidence:</b> <code>{d['expected_evidence']}</code></p>
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
    st.markdown('<div class="hero-title-3d">📊 Progress Dashboard & Privacy Export</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-tagline-3d">Track completed milestones and download your local Career Proof Dossier.</div>',
        unsafe_allow_html=True,
    )

    gap_data = st.session_state.get("analysis_results")
    assessment_data = st.session_state.get("assessment_results")
    roadmap_data = st.session_state.get("roadmap_data")
    completed_set = st.session_state.get("completed_tasks", set())

    total_days = len(roadmap_data.get("days", [])) if roadmap_data else 7
    done_count = len(completed_set)
    done_pct = round((done_count / total_days * 100), 1) if total_days > 0 else 0.0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Roadmap Completion", f"{done_pct}%", f"{done_count}/{total_days} Days Completed")
    with c2:
        verified_cnt = len(assessment_data.get("verified_skills", [])) if assessment_data else 0
        st.metric("Verified Skills", verified_cnt)
    with c3:
        needs_work_cnt = len(assessment_data.get("needs_practice_skills", [])) if assessment_data else 0
        st.metric("Skills Needing Practice", needs_work_cnt)

    st.progress(done_pct / 100.0)
    st.divider()

    # Evidence Matrix
    st.subheader("📋 Evidence vs Claim Verification Matrix")
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
        st.info("No profile skills entered yet. Complete your profile to populate the matrix.")

    st.divider()

    # Export Section
    st.subheader("📥 Export Career Proof Dossier")
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

    with st.expander("🔒 Privacy & Storage Architecture Notice"):
        st.markdown(StorageManager.get_privacy_statement())


# -----------------------------------------------------------------------------
# PAGE 7: ℹ️ About & Architecture
# -----------------------------------------------------------------------------
elif selected_page == "ℹ️ About & Architecture":
    st.markdown('<div class="hero-title-3d">ℹ️ About SkillBridge AI</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-tagline-3d">{APP_TAGLINE} — Open-Source AI Hackathon Solution</div>',
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
1. **User-Centric Data Governance:** We never process random mock data without your consent. Your profile is the sole anchor.
2. **Transparent Keyword & Synonym Extraction:** Transparent parsing derived from an open taxonomy.
3. **Proof-of-Skill Assessments:** Objective MCQs with deterministic scoring and per-question pedagogical rationale.
4. **Structured 7-Day Roadmap:** Micro-tasks yielding concrete evidence artifacts (code scripts, PRs, gists).
5. **Privacy-Preserving Local AI:** Optional local model execution via Ollama (`llama3.2`, `mistral`, `phi3`) with 100% offline fallback.
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
"""
        )

    with tab_ollama:
        st.markdown(
            """
### Setting Up Local Ollama (Optional)

SkillBridge AI works completely offline without Ollama, but you can enable real-time local AI generation:

1. **Install Ollama:** Download from [ollama.com](https://ollama.com).
2. **Pull a model:** `ollama pull llama3.2:1b`
3. **Run Ollama:** `ollama serve`
4. **Toggle in SkillBridge AI:** Enable the switch in the sidebar.
"""
        )

    with tab_license:
        st.markdown(
            """
### License & Model Provenance

- **Software License:** MIT License.
- **Open-Weight Models:** Llama 3.2 (Meta Community License), Mistral (Apache 2.0), Phi-3 (MIT).
"""
        )
