# SkillBridge AI 🎯

> **“Don't just claim skills. Prove them.”**  
> An open-source, privacy-first career intelligence MVP that assesses practical knowledge, identifies skill gaps from actual job postings, and builds actionable 7-day learning roadmaps.

---

## 📌 Problem Statement

In the modern tech hiring landscape, the gap between what job descriptions ask for and what students present on resumes is widening:
1. **Unverified Claims:** Resumes are filled with buzzwords without evidence. Recruiters face hundreds of identical applications with no proof of capability.
2. **Opaque Job Requirements:** Students and early-career transitioners struggle to dissect what skills employers actually prioritize in a posting.
3. **Overwhelming Learning Paths:** Generic online courses take months to finish and fail to target the student's exact missing competencies.
4. **Cloud Privacy & Cost Barriers:** Many AI career tools mandate paid subscriptions, log personal resumes to proprietary cloud LLMs, or require complex cloud account configurations.

---

## 💡 Proposed Solution

**SkillBridge AI** provides a transparent, local-first alternative designed for students, bootcamp graduates, and career transitioners:
- **Transparent Skill Extraction:** Parses real job descriptions against an open, editable taxonomy covering both canonical skills and common synonyms.
- **Proof-of-Skill Assessments:** Replaces vague claims with deterministic, multiple-choice quizzes that evaluate practical code and analytical intuition, recording pass/fail benchmarks.
- **Evidence-Based 7-Day Roadmaps:** Produces focused daily micro-tasks that result in concrete deliverables (e.g. GitHub gists, PRs, scripts) alongside a role-aligned capstone project idea.
- **Decoupled Local AI Architecture:** Operates with 100% functionality offline using a deterministic rule-based engine, with optional zero-cloud local AI enhancement via Ollama.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **👤 Student Skill Profile** | Declare current self-reported skills, select target roles (e.g. Junior Data Analyst, Python Developer, ML Intern), and set experience level. Supports anonymous usage. |
| **🔍 Job Description Analyzer** | Extracts required skills from unstructured postings using regex and synonym mapping. Highlights matched vs missing skills with transparent explanations. |
| **🎯 Proof-of-Skill Assessment** | Practical multiple-choice quizzes with separate secret answer storage, deterministic scoring, and detailed pedagogical explanations for every choice. |
| **🗺️ Personalized 7-Day Roadmap** | Generates a 7-day action plan featuring objectives, practical tasks, time estimates, and verifiable evidence artifacts. |
| **🏆 Capstone Portfolio Blueprint** | Delivers role-tailored project blueprints with problem statements, architecture, milestone breakdowns, and recruiter presentation advice. |
| **🤖 Local Ollama AI Integration** | Optional local model support (e.g., `llama3.2`, `mistral`, `phi3`) with real-time ping detection, strict timeouts, and transparent provenance badges. |
| **📊 Evidence vs Claim Dashboard** | Differentiates unverified self-reported claims from assessment-verified competencies. |
| **🔒 Privacy-Preserving Export** | 100% local operation with zero telemetry. Export full Career Proof Dossiers as Markdown (`.md`), tabular data as CSV (`.csv`), or JSON state backups. |

---

## 🛠️ Technology Stack

- **Runtime:** Python 3.11+
- **Frontend / Interface:** [Streamlit](https://streamlit.io/) (with custom CSS design system)
- **Data Manipulation:** [Pandas](https://pandas.pydata.org/)
- **Network Requests:** [Requests](https://requests.readthedocs.io/) (for local Ollama HTTP REST API)
- **Optional Local AI:** [Ollama](https://ollama.com/) (Open-weight local models: Llama 3.2, Mistral, Phi-3)
- **Storage:** Browser session state & local JSON/CSV/Markdown file exports (zero cloud database)
- **Testing:** Python `unittest` suite (18 automated tests)

---

## 🏗️ System Architecture

```
+-------------------------------------------------------------------------+
|                           SkillBridge AI                                |
+-------------------------------------------------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
  [ Streamlit UI (app.py) ]                    [ Local State & Export ]
  - 🏠 Home / Overview Dashboard                - Browser Session State
  - 👤 Student Profile Manager                  - Markdown Dossier (.md)
  - 🔍 Job Description Analyzer                 - Skill Gap Audit (.csv)
  - 🎯 Proof-of-Skill Quiz Engine               - State Backup (.json)
  - 🗺️ 7-Day Roadmap & Checklist                - Zero External Telemetry
  - 📊 Progress & Audit Matrix                              |
  - ℹ️ About & Architecture                                 |
            |                                               |
            +-----------------------+-----------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
  [ Core Deterministic Engine ]               [ Local AI Engine (Optional) ]
  - modules/skill_analyzer.py                 - modules/ai_provider.py
    * data/skill_taxonomy.json                  * Ollama REST API (localhost:11434)
  - modules/assessment.py                       * llama3.2, mistral, phi3
    * data/questions.json                     - Transparent Provenance Attribution
  - modules/roadmap.py (Fallback)               * Never claims AI if fallback ran
```

### Decoupled Resilience Design
- Skill extraction, gap analysis, and quiz scoring do **not** depend on any AI model.
- If Ollama is unavailable or times out, the roadmap generator automatically switches to the built-in deterministic pedagogical engine.
- The interface explicitly indicates the provenance of every output (`[🤖 Local Ollama AI]` vs `[⚙️ Deterministic Fallback Engine]`).

---

## 🚀 Installation & Running on Windows 10/11

### Prerequisites
- Python 3.11 installed and added to `PATH`.
- Git installed.

### 1. Clone or Open the Workspace
```powershell
# Open PowerShell in the project directory
cd "SkillBridge AI"
```

### 2. (Optional but Recommended) Create a Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Run the Automated Test Suite
```powershell
python -m unittest discover tests
```
*All 18 unit tests should pass with `OK`.*

### 5. Launch the Streamlit Web Application
```powershell
streamlit run app.py
```
The application will launch in your default browser at `http://localhost:8501`.

---

## 🦙 Optional: Enabling Local AI with Ollama

SkillBridge AI functions completely out-of-the-box without Ollama. If you wish to enable dynamic local AI roadmap enrichment:

1. **Download & Install Ollama:**
   - Download the installer for Windows from [ollama.com](https://ollama.com/download/windows).
2. **Start the Ollama daemon:**
   ```powershell
   ollama serve
   ```
3. **Pull a lightweight open-weight model:**
   ```powershell
   # Lightweight option (ideal for 8GB/16GB RAM machines)
   ollama pull llama3.2:1b

   # Standard option (3B parameters)
   ollama pull llama3.2
   ```
4. **Connect in SkillBridge AI:**
   - In the left sidebar under **🤖 Local AI Engine**, toggle **Enable Local AI (Ollama)**.
   - Select your target model (e.g., `llama3.2` or `llama3.2:1b`).
   - Click **🔌 Test Ollama Connection** to verify status.

---

## 📖 Example Walkthrough

1. **Load a Preset:** On the Home page, click **📊 Load Junior Data Analyst Demo**.
2. **Analyze the Posting:** Navigate to **Job Description Analysis**. View the extracted requirements (`SQL`, `Python`, `Statistics`, `Excel`, `Git and GitHub`) and observe that `Statistics` and `Git and GitHub` are identified as missing skill gaps.
3. **Prove Practical Knowledge:** Go to **Proof-of-Skill Assessment**. Complete the multiple-choice quiz on `SQL` and `Python`. Submit to see deterministic scoring with full explanations for each question.
4. **Follow the Roadmap:** Open **Career Roadmap** to view a tailored 7-day action plan targeting the identified gaps. Check off Day 1 once you complete the practical task.
5. **Export Your Dossier:** Go to **Progress & Export** to download your complete Markdown dossier (`skillbridge_career_dossier.md`) or CSV audit table.

---

## ⚖️ Open-Weight Model Licensure & Provenance

When utilizing local models via Ollama, users are subject to each model's respective upstream license:

| Model | Provider | Model ID | Official License Source | Key Terms & Restrictions |
| :--- | :--- | :--- | :--- | :--- |
| **Llama 3.2** | Meta AI | `llama3.2`, `llama3.2:1b` | [Meta Llama 3.2 License](https://llama.meta.com/llama3/license/) | Free for commercial and research use under 700M monthly active users. Attribution required. |
| **Mistral 7B** | Mistral AI | `mistral` | [Apache 2.0](https://github.com/mistralai/mistral-src/blob/main/LICENSE) | Permissive open-source license permitting modification and commercial redistribution. |
| **Phi-3** | Microsoft | `phi3` | [MIT License](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct) | Permissive open-source license. |

*SkillBridge AI does not bundle model weights. Weights are fetched solely by the user on their local machine via Ollama.*

---

## 🔒 Privacy & Data Sovereignty

- **100% Local Processing:** Candidate names, resumes, quiz answers, and roadmaps reside exclusively in local browser session memory.
- **Zero Third-Party Beacons:** No telemetry, analytics pixels, or remote logging services are embedded.
- **Zero Cloud LLM Exposure:** Ollama requests are routed exclusively to `http://localhost:11434`.

---

## ⚠️ Known Limitations

1. **Keyword Extraction Boundary:** The skill extraction algorithm uses transparent regex matching and synonyms. Complex colloquialisms or non-standard acronyms not present in `data/skill_taxonomy.json` will not be detected unless added to the taxonomy file.
2. **Deterministic Question Bank Size:** The MVP question bank includes curated questions for all 10 core categories. Expanding questions for additional specialized skills requires adding entries to `data/questions.json`.
3. **Formative Assessment Disclaimer:** Proof-of-Skill assessments serve as formative benchmarking tools and do not constitute accredited academic credentials or employability guarantees.

---

## 🤝 Contribution Guidelines

We welcome community contributions:
1. **Adding Skills to Taxonomy:** Edit `data/skill_taxonomy.json` to include new skills, categories, and synonym aliases.
2. **Expanding the Question Bank:** Add high-quality scenario-based MCQs to `data/questions.json` ensuring 4 options and detailed educational rationales.
3. **Adding Tests:** Place new unit tests in the `tests/` directory and ensure `python -m unittest discover tests` passes before opening a pull request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
