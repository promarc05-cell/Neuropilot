<p align="center">
  <img src="./frontend/public/banner.png"
       alt="Neuropilot Banner"
       width="100%"
       height="300"
       style="object-fit: cover; border-radius: 8px;" />
</p>

# <p align="center">🧠 Neuropilot 🧠</p>
### <p align="center">**Adaptive Executive-Function Prosthetic & Cognitive Load Pacing Engine**</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React_18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Python_3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/Groq_LPU-F55036?style=for-the-badge&logo=speedtest&logoColor=white" alt="Groq" />
</p>

---

## 🌟 Introduction

**Neuropilot** is an AI-driven, neurodivergent-aware executive function prosthetic engineered to break task initiation paralysis, regulate cognitive fatigue, and dynamically calibrate academic work. Built on principles from the **Deshmukh Cognitive Framework**, Neuropilot moves beyond static checklist planners by combining passive browser activity sensing, real-time distraction recall, and dynamic task decomposition.

The system features:
1.  **FastAPI & SQLAlchemy Backend**: Ingests unstructured academic syllabi, PDFs, and assignment prompts to generate acyclic directed task graphs (DAGs) with strict Pydantic v2 schema validation.
2.  **Cognitive Adaptation Engine**: Tracks focus patterns using client-side telemetry, updating an Exponential Moving Average (EMA) to scale task duration boundaries between 10 and 35 minutes.
3.  **React + Vite Dashboard**: An accessible interface supporting execution views (Today View, Focus Mode Sprint) paired with proactive, low-friction micro-step interventions.

---

## ✨ Key Features

*   **⚡ Dynamic Task Decomposition**: Generates structured, domain-tailored milestones with subtasks bounded between 15 and 90 minutes. Every task includes strict completion criteria and a zero-friction starter step achievable in under 60 seconds.

*   **👁️ Passive Activity Sensing**: Zero-friction client tracking via the Page Visibility and Window Blur/Focus APIs captures active focus vs. distracted away-time without manual time logging.

*   **📈 EMA Cognitive Load Pacing**: Calculates rolling user telemetry (`session_distraction`, `distraction_ratio`, `avg_switches_per_session`) using a 70/30 Exponential Moving Average to automatically adapt study session chunk sizes.

*   **🛡️ Multi-Provider AI Resilience**: Operates across Groq LPUs, Google Gemini, and OpenAI with automated fallbacks to rule-based heuristics when running offline or hitting rate limits.

*   **🔔 Context-Switch Interventions**: Monitors rolling 10-minute focus windows. When switching frequency hits the threshold ($\ge 2$ tab switches), Neuropilot surfaces a non-judgmental nudge to offer an immediate 2-minute starter breakdown.

*   **📐 Topological Dependency Validation**: Verifies generated microtasks with directed acyclic graph (DAG) cycle checks, ensuring dependencies follow logical execution order without deadlock.

---

## 📐 System Architecture

*Every user action and assignment submission moves through an adaptive loop that continuously tunes task difficulty and pacing.*

<span style="color:#c2410c">#### `LAYER 0 · SENSORY TELEMETRY`</span>
### Client Activity Observer
`useBehaviorTracker` hook running passively inside React during active study sprints.
> `document.visibilitychange` `window.blur / focus` `tab_switch_count` `active_ms vs distracted_ms`

<div align="center"><span style="color:#c2410c">↓</span></div>

<span style="color:#2563eb">#### `LAYER 1 · TELEMETRY INGESTION & ROLLING PROFILES`</span>
### Behavioral Engine
Ingests telemetry batches via `POST /api/telemetry/log` and updates database profiles.
> `session_distraction = away / total` `EMA update: 0.7 · old + 0.3 · new` `UserBehaviorProfile`

<div align="center"><span style="color:#2563eb">↓</span></div>

<span style="color:#d97706">#### `LAYER 2 · INPUT ANALYSIS & DECOMPOSITION ROUTING`</span>
### Assignment Analyzer & Task Generator
Extracts academic context, validates rubrics, and injects observed attention boundaries.
> `Assignment PDF / Raw Text` `Rubric Milestones` `Ambiguity Detection` `Pacing Injection`

<div align="center"><span style="color:#d97706">↓</span></div>

<span style="color:#7c3aed">#### `LAYER 3 · INFERENCE ORCHESTRATION`</span>
### Resilient AI Core (`ai_service.py`)
Executes domain-agnostic structured JSON task breakdowns using the active provider.
**`PROMPT INJECTION`** ➔ **`LLM INFERENCE`** ➔ **`SCHEMA VALIDATION`**
> *Groq LPU (Ultra-Low Latency) · Google Gemini · OpenAI · Rule-Based Fallback*

<div align="center"><span style="color:#7c3aed">↓</span></div>

<span style="color:#0891b2">#### `ENGINE SUBSYSTEMS`</span>

| 📘 Behavioral Memory | 🛠️ Pacing Governor | 🧠 Schema Contracts |
|:---|:---|:---|
| *Deshmukh Telemetry*<br><br>• Rolling switch counters<br>• Focus-to-distraction ratio<br>• **Persistent profile per user** | *Adaptive Bounds*<br><br>• High distraction: 10–15m chunks<br>• High focus: Up to 35m chunks<br>• *Instant 2-minute microstarter* | *Pydantic v2 Enforced*<br><br>• `TaskProposal` validation<br>• Low-friction `<60s` first step<br>• Topological DAG sequencing |

<div align="center"><span style="color:#0891b2">↓</span></div>

<span style="color:#dc2626">#### `LAYER 4 · REAL-TIME INTERVENTION`</span>
### Distraction Recall Gate
Catches context switching mid-session and presents proactive, guilt-free assistance.
> `Threshold trigger (≥ 2 switches)` `Nudge Banner` `Break down task` `Resume session`

<div align="center"><span style="color:#dc2626">↓</span></div>

<span style="color:#4338ca">#### `LAYER 5 · RUNTIME INFRASTRUCTURE`</span>
### Local-First Persistence & Storage
> `FastAPI ASGI` `SQLite / PostgreSQL` `SQLAlchemy ORM` `Client LocalStorage`

---

## 📂 Project Structure

```text
Neuropilot/
├── backend/                        # FastAPI Application & Adaptive Engine
│   ├── main.py                     # ASGI application entry point & router mounting
│   ├── config.py                   # Pydantic-settings & safe environment validation
│   ├── database.py                 # SQLAlchemy engine, sessions & schema migrations
│   ├── models.py                   # ORM models (User, Assignment, Task, BehaviorProfile)
│   ├── schemas.py                  # Pydantic v2 data contracts & API response schemas
│   ├── routes/                     # API endpoint definitions
│   │   ├── assignments.py          # Upload, parsing, and decomposition routes
│   │   ├── tasks.py                # Task status, DAG ordering, and micro-steps
│   │   ├── telemetry.py            # Passive behavior tracking & profile endpoints
│   │   └── auth.py                 # Authentication and development bypass modes
│   └── services/                   # Core business logic & AI orchestration
│       ├── ai_service.py           # Provider dispatch (Groq, Gemini, OpenAI) & JSON parser
│       ├── assignment_analyzer.py  # Syllabus extraction & rubric milestone analyzer
│       └── task_generator.py       # Adaptive task breaking & DAG validation
│
├── frontend/                       # Client Application (React + Vite + TypeScript)
│   ├── src/
│   │   ├── views/                  # Primary user interfaces
│   │   │   ├── TodayView.tsx       # Executive coach, timer sprint, and active tasks
│   │   │   ├── FocusModeView.tsx   # Single-task sprint & 4-step focus breakdown
│   │   │   └── StudyVibeView.tsx   # Ambient study space & companion integration
│   │   ├── hooks/
│   │   │   └── useBehaviorTracker.ts # Page visibility and tab-switch telemetry hook
│   │   ├── api/
│   │   │   └── client.ts           # Axios / Fetch client and backend endpoint bridge
│   │   ├── types.ts                # TypeScript interfaces matching backend schemas
│   │   ├── App.tsx                 # Root component and navigation state
│   │   └── main.tsx                # React DOM mounting
│   ├── package.json                # Dependencies and scripts
│   └── vite.config.ts              # Vite configuration
│
├── tests/                          # Automated Pytest Suite
│   ├── test_telemetry.py           # EMA math, persistence, and chunk sizing tests
│   ├── test_live_ai_service.py     # Live inference, fallback, and schema tests
│   ├── test_dsa_telemetry_decomposition.py # Domain task breakdown and telemetry wiring
│   └── test_config.py              # Environment variable and provider safety tests
│
├── .env.example                    # Template environment variables
├── requirements.txt                # Python backend dependencies
└── README.md                       # Project documentation
