import asyncio
import json
from loguru import logger
from sqlalchemy import select

from config import settings
from database.models import init_db, AsyncSession, Job
from ai.scorer import score_job


async def run_scoring(batch_size: int = 10):
    await init_db()

    async with AsyncSession() as session:
        # Fetch jobs that haven't been scored yet
        result = await session.execute(
            select(Job)
            .where(Job.relevance_score == 0.0)
            .limit(batch_size)
        )
        jobs = result.scalars().all()

    if not jobs:
        logger.info("No unscored jobs found")
        return

    logger.info(f"Scoring {len(jobs)} jobs...")

    scored, filtered = 0, 0

    for job in jobs:
        result = await score_job(job.title, job.description or "", job.company)

        async with AsyncSession() as session:
            db_job = await session.get(Job, job.id)
            db_job.relevance_score = result.score
            db_job.relevance_reason = result.reason
            db_job.skills_required = (
                ", ".join(result.matched_skills) if result.matched_skills else db_job.skills_required
            )

            if result.score < settings.min_relevance_score:
                db_job.status = "rejected"
                filtered += 1
                logger.info(f"[{result.score}/10] FILTERED — {job.title} @ {job.company}: {result.reason}")
            else:
                scored += 1
                logger.info(f"[{result.score}/10] KEPT    — {job.title} @ {job.company}: {result.reason}")

            await session.commit()

        # Small delay to avoid rate limits
        await asyncio.sleep(0.5)

    logger.info(f"Done — kept: {scored}, filtered out: {filtered} (score < {settings.min_relevance_score})")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Score scraped jobs using AI")
    parser.add_argument("--batch", type=int, default=10, help="Number of jobs to score (default: 10)")
    args = parser.parse_args()

    asyncio.run(run_scoring(args.batch))
