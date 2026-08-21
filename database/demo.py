"""Safe, fictional data for the public portfolio deployment."""

from datetime import datetime, timedelta

from sqlalchemy import select

from database.models import AsyncSession, Job


DEMO_JOBS = [
    {
        "title": "AI Backend Engineer",
        "company": "Northstar Labs",
        "location": "Bengaluru, India",
        "url": "https://www.linkedin.com/jobs/search/?keywords=AI%20Backend%20Engineer",
        "description": "Build reliable Python services that integrate LLM workflows, APIs, and data pipelines.",
        "skills_required": "Python, FastAPI, PostgreSQL, OpenAI API, Docker",
        "relevance_score": 9.1,
        "relevance_reason": "Strong fit for Python backend work, asynchronous APIs, and practical LLM integrations.",
        "resume_bullets": "• Built asynchronous FastAPI services for AI-assisted workflows.\n• Designed SQLAlchemy data layers for reliable job-pipeline tracking.\n• Integrated LLM APIs into production-oriented backend features.",
        "cover_letter": "Dear Hiring Team,\n\nI am excited by the opportunity to build dependable AI backend systems. My work combines Python, FastAPI, and LLM integrations with a focus on useful product workflows and clean APIs.",
        "status": "reviewed",
        "applied": False,
        "scraped_at": datetime.utcnow() - timedelta(hours=2),
    },
    {
        "title": "Machine Learning Platform Intern",
        "company": "Atlas Systems",
        "location": "Hyderabad, India",
        "url": "https://www.linkedin.com/jobs/search/?keywords=Machine%20Learning%20Platform%20Intern",
        "description": "Support internal ML tooling and API services used by product engineering teams.",
        "skills_required": "Python, SQL, REST APIs, Machine Learning, Git",
        "relevance_score": 8.4,
        "relevance_reason": "Relevant Python, API, and machine-learning tooling requirements with room to grow in platform engineering.",
        "resume_bullets": "• Built REST APIs with FastAPI and async database access.\n• Applied structured prompts to automate job-description analysis.\n• Delivered an end-to-end workflow from ingestion to dashboard review.",
        "cover_letter": "Dear Hiring Team,\n\nI would bring hands-on experience building Python automation and API-driven workflows, along with a strong interest in developer-focused ML platforms.",
        "status": "new",
        "applied": False,
        "scraped_at": datetime.utcnow() - timedelta(hours=7),
    },
    {
        "title": "Backend Developer",
        "company": "Cobalt Commerce",
        "location": "Remote, India",
        "url": "https://www.linkedin.com/jobs/search/?keywords=Backend%20Developer",
        "description": "Develop backend services and integrations for a high-volume commerce platform.",
        "skills_required": "Python, FastAPI, SQLAlchemy, PostgreSQL, REST",
        "relevance_score": 7.8,
        "relevance_reason": "A solid backend match, especially for API design and database-backed services.",
        "resume_bullets": "• Created modular FastAPI endpoints backed by SQLAlchemy.\n• Implemented job-status tracking through a REST API and dashboard.\n• Used async I/O to support concurrent data operations.",
        "cover_letter": "Dear Hiring Team,\n\nI am interested in building thoughtful, maintainable backend services and would value the opportunity to apply my FastAPI and data-modeling experience to your platform.",
        "status": "applied",
        "applied": True,
        "scraped_at": datetime.utcnow() - timedelta(days=1),
    },
]


async def seed_demo_jobs() -> None:
    """Add the public showcase data only once to an empty database."""
    async with AsyncSession() as session:
        existing = await session.execute(select(Job.id).limit(1))
        if existing.first():
            return
        session.add_all([Job(source="demo", **job) for job in DEMO_JOBS])
        await session.commit()
