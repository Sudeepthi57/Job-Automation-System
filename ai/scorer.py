import json
from dataclasses import dataclass
from openai import AsyncOpenAI
from loguru import logger

from config import settings


@dataclass
class ScoreResult:
    score: float        # 1-10
    reason: str
    matched_skills: list[str]
    missing_skills: list[str]


client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are a job relevance evaluator. Given a job description and a candidate profile,
score how relevant the job is for the candidate on a scale of 1 to 10.

Respond ONLY with a valid JSON object in this exact format:
{
  "score": <number 1-10>,
  "reason": "<1-2 sentence explanation>",
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"]
}"""


async def score_job(job_title: str, job_description: str, company: str) -> ScoreResult:
    user_message = f"""Candidate Profile:
- Target Role: {settings.target_role}
- Skills: {settings.target_skills}

Job to evaluate:
- Title: {job_title}
- Company: {company}
- Description:
{job_description[:3000]}

Rate this job's relevance for the candidate."""

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=300,
        )

        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)

        return ScoreResult(
            score=float(data.get("score", 0)),
            reason=data.get("reason", ""),
            matched_skills=data.get("matched_skills", []),
            missing_skills=data.get("missing_skills", []),
        )

    except json.JSONDecodeError:
        logger.warning(f"Could not parse AI response for '{job_title}' — defaulting to score 0")
        return ScoreResult(score=0, reason="Failed to parse AI response", matched_skills=[], missing_skills=[])
    except Exception as e:
        logger.error(f"OpenAI API error for '{job_title}': {e}")
        return ScoreResult(score=0, reason=str(e), matched_skills=[], missing_skills=[])
