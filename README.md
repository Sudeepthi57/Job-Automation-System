# AI-Powered Job Application Automation System

An end-to-end automation pipeline that scrapes job listings from LinkedIn, scores them using AI, and generates tailored resumes and cover letters — all tracked through a custom dashboard.

---

## What It Does

Most job applications involve the same repetitive tasks: searching for jobs, filtering relevant ones, rewriting your resume for each role, drafting cover letters. This system automates all of it.

```
LinkedIn Jobs  →  AI Relevance Filter  →  Resume & Cover Letter Generator  →  Dashboard
```

1. **Scrape** — Playwright opens LinkedIn, logs in, and collects job listings matching your target role
2. **Score** — GPT reads each job description and scores relevance (1-10) based on your skills
3. **Filter** — Jobs below your threshold are automatically rejected
4. **Generate** — For high-scored jobs, GPT writes tailored resume bullets and a custom cover letter
5. **Track** — Dashboard shows all jobs with scores, generated content, and application status

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Scraping | Python + Playwright |
| Backend | FastAPI + Uvicorn |
| AI | OpenAI GPT-4o-mini |
| Database | SQLite + SQLAlchemy (async) |
| Frontend | Vanilla JS + HTML/CSS |
| Config | Pydantic Settings + python-dotenv |
| Logging | Loguru |

---

## Project Structure

```
job-automation-system/
├── scraper/
│   ├── base.py          # Abstract base scraper
│   ├── linkedin.py      # LinkedIn Playwright scraper
│   └── runner.py        # CLI entry point
├── ai/
│   ├── scorer.py        # GPT relevance scoring
│   └── runner.py        # Batch scoring runner
├── generator/
│   ├── generator.py     # Resume bullets + cover letter generation
│   └── runner.py        # Batch generation runner
├── api/
│   └── routes.py        # FastAPI REST endpoints
├── database/
│   └── models.py        # SQLAlchemy Job model
├── dashboard/
│   ├── templates/       # Jinja2 HTML templates
│   └── static/          # CSS + JS
├── main.py              # FastAPI app entry point
├── config.py            # Settings via .env
└── resume_data.json     # Your profile (skills, experience, projects)
```

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone https://github.com/Sudeepthi57/Job-Automation-System.git
cd Job-Automation-System
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-key-here
TARGET_ROLE=AI Engineer
TARGET_SKILLS=Python, FastAPI, LLM, Machine Learning, Backend
MIN_RELEVANCE_SCORE=6
```

### 3. Add your profile

Edit `resume_data.json` with your real name, experience, projects, and skills. This is what the AI uses to generate tailored content.

---

## Usage

Run each step in order. Keep the dashboard server running in a separate terminal.

### Start the dashboard
```bash
python main.py
# Open http://localhost:8000
```

### Step 1 — Scrape jobs
```bash
python -m scraper.runner --keyword "AI Engineer" --location "India" --max 20
```
A Chrome window opens. Log in to LinkedIn — the scraper takes over from there.

### Step 2 — Score with AI
```bash
python -m ai.runner --batch 20
```
Each job is scored 1-10. Jobs below `MIN_RELEVANCE_SCORE` are auto-rejected.

### Step 3 — Generate application content
```bash
python -m generator.runner --batch 10
```
For each high-scored job, GPT generates tailored resume bullet points and a cover letter.

### Step 4 — Review on dashboard
Open `http://localhost:8000`, browse jobs, copy the generated content, and mark applications as applied.

---

## Dashboard Features

- Stats bar — total jobs, new, reviewed, applied, rejected, average AI score
- Job cards with relevance score badge and status badge
- Filter by status, minimum score, or search by title/company
- Detail modal — AI reason, matched skills, resume bullets, cover letter, job description preview
- One-click status updates (reviewed / applied / rejected)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List all jobs (supports `?status=` and `?min_score=`) |
| GET | `/api/jobs/{id}` | Get single job details |
| PATCH | `/api/jobs/{id}/status` | Update job status |
| GET | `/api/stats` | Aggregated stats |

---

## How the AI Scoring Works

The scorer sends the job description along with your target role and skills to GPT. It returns:

```json
{
  "score": 8,
  "reason": "Strong match — requires Python, FastAPI, and LLM experience which aligns well with the candidate's profile.",
  "matched_skills": ["Python", "FastAPI", "OpenAI API"],
  "missing_skills": ["Kubernetes"]
}
```

Jobs scoring below the configured threshold are automatically marked as rejected so you only see relevant opportunities.

---

## Resume Generation Example

Given a job description for an *"AI Backend Engineer"* role, the generator produces bullets like:

```
• Built async FastAPI service handling 15k+ daily requests with sub-100ms latency
• Integrated GPT-4 for automated document processing, reducing manual review by 70%
• Designed SQLAlchemy ORM layer with async sessions for concurrent job pipeline
```

---

## What This Project Demonstrates

- **Systems thinking** — end-to-end pipeline with clear separation of concerns
- **Automation** — real browser automation with Playwright, not just API calls
- **AI integration** — practical LLM usage beyond basic chat (scoring, generation, structured output)
- **Backend engineering** — async FastAPI, SQLAlchemy, REST API design
- **Product mindset** — solves a real problem with a usable interface
