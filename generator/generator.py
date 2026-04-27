import json
from dataclasses import dataclass
from pathlib import Path
from openai import AsyncOpenAI
from loguru import logger

from config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

RESUME_PATH = Path(__file__).parent.parent / "resume_data.json"


def load_resume() -> dict:
    with open(RESUME_PATH, "r") as f:
        return json.load(f)


@dataclass
class GeneratedContent:
    resume_bullets: str     # newline-separated tailored bullet points
    cover_letter: str


async def generate_for_job(job_title: str, company: str, job_description: str) -> GeneratedContent:
    resume = load_resume()
    resume_summary = _build_resume_summary(resume)

    bullets = await _generate_bullets(job_title, company, job_description, resume_summary)
    cover_letter = await _generate_cover_letter(job_title, company, job_description, resume, bullets)

    return GeneratedContent(resume_bullets=bullets, cover_letter=cover_letter)


async def _generate_bullets(job_title: str, company: str, description: str, resume_summary: str) -> str:
    prompt = f"""You are a professional resume writer.

Candidate's background:
{resume_summary}

Job they are applying for:
- Title: {job_title}
- Company: {company}
- Description:
{description[:2500]}

Write 4-5 strong, tailored resume bullet points for this specific job.
Rules:
- Start each bullet with an action verb
- Include metrics/numbers wherever possible
- Match keywords from the job description
- Be concise (one line each)
- Output ONLY the bullet points, one per line, starting with •"""

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()


async def _generate_cover_letter(
    job_title: str, company: str, description: str, resume: dict, bullets: str
) -> str:
    prompt = f"""You are a professional cover letter writer.

Candidate:
- Name: {resume['name']}
- Summary: {resume['summary']}
- Key skills: {', '.join(resume['skills']['languages'] + resume['skills']['frameworks'] + resume['skills']['ai_ml'])}

Tailored resume highlights:
{bullets}

Job:
- Title: {job_title}
- Company: {company}
- Description:
{description[:2000]}

Write a concise, professional cover letter (3 short paragraphs):
1. Opening — why this role and company specifically
2. Middle — connect 2-3 of the candidate's strongest experiences to the job requirements
3. Closing — call to action

Keep it under 250 words. Address it to "Hiring Team" if no name is known."""

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()


def _build_resume_summary(resume: dict) -> str:
    lines = [f"Name: {resume['name']}", f"Summary: {resume['summary']}", ""]

    lines.append("Experience:")
    for exp in resume.get("experience", []):
        lines.append(f"  - {exp['title']} at {exp['company']} ({exp['duration']})")
        for b in exp.get("bullets", []):
            lines.append(f"    • {b}")

    lines.append("\nProjects:")
    for proj in resume.get("projects", []):
        lines.append(f"  - {proj['name']} ({proj['tech']})")
        for b in proj.get("bullets", []):
            lines.append(f"    • {b}")

    skills = resume.get("skills", {})
    all_skills = skills.get("languages", []) + skills.get("frameworks", []) + skills.get("ai_ml", [])
    lines.append(f"\nSkills: {', '.join(all_skills)}")

    return "\n".join(lines)
