# CV Analyzer

> Machine Learning Supported Resume Analysis System — SEN 4015 Advanced Python Programming Term Project

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E.svg)](https://scikit-learn.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docs.docker.com/compose/)

CV Analyzer automates the resume (CV) evaluation process in job applications. It processes CVs in **PDF/TXT** format to perform job category prediction, skill extraction, job-profile compatibility scoring, and personalized recommendation generation — while treating data privacy as a first-class concern through PII masking, temporary file deletion, and secure authentication.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Run with Docker (recommended)](#run-with-docker-recommended)
  - [Manual Setup](#manual-setup)
- [Configuration](#configuration)
- [Model Training](#model-training)
- [Security & Privacy](#security--privacy)
- [Testing](#testing)
- [Future Work](#future-work)
- [Team](#team)
- [References](#references)

---

## Features

- **Job Category Prediction** — Classifies a CV into one of 8 software roles with a confidence score (TF-IDF + Logistic Regression).
- **Skill Extraction** — Detects 75+ skills via regex patterns and estimates proficiency level (Beginner / Intermediate / Advanced) using contextual keyword analysis.
- **Match Scoring** — Calculates a 0–100 compatibility score against a target job profile using weighted required/preferred skill matching.
- **Personalized Recommendations** — Suggests missing skills and a category-based learning roadmap.
- **Privacy by Design** — Masks PII (emails, phone numbers), deletes uploaded files after analysis, and stores only a masked preview in the database.
- **User Accounts & History** — Registered users can store, view, and delete their past analyses (PostgreSQL).
- **One-Command Deployment** — Fully containerized with Docker Compose (app + database).

### Supported Categories

`Backend Developer` · `Cloud Engineer` · `Data Scientist` · `Frontend Developer` · `Full Stack Developer` · `Machine Learning Engineer` · `Mobile App Developer` · `Python Developer`

---

## How It Works

The system runs an input CV through a modular pipeline where each stage can be tested and extended independently (Single Responsibility principle):

```
CV Input (PDF/TXT or raw text)
        │
        ▼
File Parsing            ── ParserFactory → PDFParser / TextParser
        │
        ▼
Skill Extraction        ── SkillExtractor (regex + NLTK)
        │
        ▼
Category Prediction     ── ResumeClassifier (TF-IDF + Logistic Regression)
        │
        ▼
Match Score Calculation ── ResumeScorer (weighted skill matching)
        │
        ▼
Recommendation Engine   ── RecommendationEngine
        │
        ▼
PII Analysis & Masking  ── PIISanitizer
        │
        ▼
Result Display / Database Storage
```

### Scoring Formula

```
Score = (Required Match % × 0.7) + (Preferred Match % × 0.3)
```

Required skills are weighted more heavily, reflecting that missing a required skill is more critical than missing a preferred one.

---

## Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| UI | Streamlit | Multi-page web interface, rapid prototyping |
| ML | scikit-learn | TF-IDF vectorization + Logistic Regression pipeline |
| NLP | NLTK | Tokenization, stopword filtering |
| PDF | PyPDF2 | Lightweight PDF text extraction |
| Database | PostgreSQL 16 | Relational storage, ACID compliance |
| ORM | SQLAlchemy 2.0 | Type-safe models, session management |
| Auth | bcrypt | Secure password hashing |
| Serialization | joblib | Persistent model storage |
| Deployment | Docker Compose | App + database in one command |

---

## Project Structure

```
CV-Analyzer/
├── main.py                          # Streamlit entry point & analysis flow
├── cv_analyzer/
│   ├── services/
│   │   ├── pipeline.py              # Orchestrates the full analysis pipeline
│   │   ├── classifier.py           # TF-IDF + Logistic Regression prediction
│   │   ├── scorer.py               # Weighted skill matching
│   │   └── recommender.py          # Personalized recommendations & roadmaps
│   ├── security/                   # PII masking, file validation, temp-file handling
│   ├── auth/                       # Registration, login, analysis repository
│   ├── db/                         # SQLAlchemy models & DB connection
│   └── ml/
│       └── train_classifier.py     # Model training script
├── pages/
│   └── 1_Gecmis_Analizler.py       # Analysis history page
├── docker/                         # entrypoint.sh and Docker assets
├── gpt_dataset.csv                 # Training dataset (400 CVs, 8 categories)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Getting Started

### Run with Docker (recommended)

The `entrypoint.sh` script waits for PostgreSQL, creates the tables, trains the model if none exists, and starts Streamlit.

```bash
# 1. Clone the repository
git clone https://github.com/ErsinHacioglu/CV-Analyzer.git
cd CV-Analyzer

# 2. Create your environment file
cp .env.example .env   # edit values as needed

# 3. Build and start
docker compose up --build
```

The app will be available at **http://localhost:8501**.

### Manual Setup

Requires Python 3.11+ and a running PostgreSQL 16 instance.

```bash
# 1. Clone and enter the project
git clone https://github.com/ErsinHacioglu/CV-Analyzer.git
cd CV-Analyzer

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env             # set your PostgreSQL connection details

# 5. Train the model (creates the serialized pipeline)
python -m cv_analyzer.ml.train_classifier

# 6. Launch the app
streamlit run main.py
```

---

## Configuration

Copy `.env.example` to `.env` and fill in your settings. Typical values include the PostgreSQL connection parameters (host, port, database, user, password). Refer to `.env.example` for the full list of supported variables.

> **Note:** Never commit your real `.env` file. It is excluded via `.gitignore`.

---

## Model Training

The training script (`cv_analyzer/ml/train_classifier.py`) builds the classification model:

- Vectorizes CV text with **TF-IDF** (`max_features=8000`, `ngram_range=(1, 2)`, `stop_words="english"`).
- Trains a multi-class **Logistic Regression** classifier.
- Uses a **stratified 80/20 train-test split** to preserve class balance.
- Reports **test accuracy** and per-class **precision / recall / F1-score** via `classification_report`.
- Serializes the fitted pipeline with **joblib** for reuse at inference time.

```bash
python -m cv_analyzer.ml.train_classifier
```

---

## Security & Privacy

CV Analyzer is built around a **Privacy by Design** approach (GDPR / KVKK aligned):

- **PIISanitizer** — Detects and masks email addresses and phone numbers as `[EMAIL HIDDEN]` / `[PHONE HIDDEN]`.
- **SecureFileHandler** — Writes uploads to a temporary directory with UUID-based filenames and auto-deletes them after analysis using a context manager.
- **FileValidator** — Enforces extension checks, a 5 MB size limit, PDF magic-byte validation (`%PDF-`), and UTF-8 validation to block malicious uploads.
- **Data Minimization** — Raw CV text is never stored; the database keeps only a masked 400-character preview plus a PII count as metadata.
- **Authentication** — Passwords are hashed with **bcrypt** to resist rainbow-table attacks.

### Database Schema

| Table | Columns |
| --- | --- |
| `users` | `id`, `email`, `password_hash`, `full_name`, `created_at` |
| `analysis_history` | `user_id (FK)`, `category`, `match_score`, `found_skills`, `missing_skills`, `recommendations`, `masked_preview`, `pii_count`, `created_at` |

---

## Testing

### Model Evaluation

Running `train_classifier.py` produces test accuracy and class-based precision/recall/F1 reports over a stratified split.

### Functional Test Scenarios

| Scenario | Expected Result |
| --- | --- |
| PDF CV upload | Text extracted, analysis completed, file deleted |
| Raw text input | Pipeline runs directly |
| CV containing PII | Email/phone masked, warning displayed |
| Invalid file (> 5 MB) | Rejected with `ValueError` |
| Registered user analysis | Record stored in `analysis_history` |
| Target position selection | User can override the predicted category |

---

## Future Work

- Multilingual CV support (Turkish stopwords and skill database)
- Transformer-based classifiers (BERT / DistilBERT)
- Model explainability with SHAP / LIME
- Role-based access control (HR vs. candidate)
- Session management and rate limiting with Redis

---

## Team

| Name | Student ID |
| --- | --- |
| Ersin Hacıoğlu | 2101546 |
| Secem Uğus | 2103281 |
| Bartu Halil | 2103373 |

**Course:** SEN 4015 — Advanced Python Programming · **Date:** June 2026

---

## References

1. Sanchez, C., & Orouskhani, Y. (2020). *Classification of Resumes using Natural Language Processing Techniques and Machine Learning.* ICAISC.
2. van Esch, P., Black, J. S., & Ferolie, J. (2019). *Marketing AI: Artificial Intelligence in Recruiting and the Implications for HR.* Business Horizons, 62(6), 729–739.
3. European Union (2016). *General Data Protection Regulation (GDPR)*, Regulation (EU) 2016/679.
4. Republic of Türkiye (2016). *Personal Data Protection Law No. 6698 (KVKK)*.
5. Pedregosa, F., et al. (2011). *Scikit-learn: Machine Learning in Python.* JMLR, 12, 2825–2830.
6. Streamlit Inc. (2024). *Streamlit Documentation.* https://docs.streamlit.io
7. PostgreSQL Global Development Group (2024). *PostgreSQL 16 Documentation.* https://www.postgresql.org/docs/
