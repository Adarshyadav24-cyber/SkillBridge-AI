"""Configuration settings for SkillBridge AI.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TAXONOMY_FILE = DATA_DIR / "skill_taxonomy.json"
QUESTIONS_FILE = DATA_DIR / "questions.json"

# App Branding
APP_NAME = "SkillBridge AI"
APP_TAGLINE = "Don't just claim skills. Prove them."
APP_VERSION = "1.0.0-mvp"
APP_ICON = "🎯"

# Predefined Target Roles
DEFAULT_ROLES = [
    "Junior Data Analyst",
    "Python Developer",
    "Machine Learning Intern",
    "Full-Stack Developer",
    "Business Intelligence (BI) Analyst",
    "Cloud & DevOps Associate",
]

# Experience Levels
EXPERIENCE_LEVELS = [
    "Beginner / Student (No commercial experience)",
    "Self-Taught / Career Transitioner",
    "Junior (0 - 1 years experience)",
    "Associate / Early Career (1 - 2 years experience)",
]

# Supported Primary Skill Categories
CORE_SKILLS = [
    "Python",
    "Java",
    "SQL",
    "Statistics",
    "Data Analysis",
    "Machine Learning",
    "Git and GitHub",
    "Problem Solving",
    "Communication",
    "Excel",
]

# Assessment Configuration
PASSING_SCORE_PERCENT = 70
QUESTIONS_PER_SKILL = 3

# Local AI Configuration (Ollama)
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2"
OLLAMA_TIMEOUT_SECONDS = 8
POPULAR_OLLAMA_MODELS = [
    "llama3.2",
    "llama3.2:1b",
    "llama3",
    "mistral",
    "phi3",
    "deepseek-r1",
    "qwen2.5",
]
