import asyncio
from loguru import logger
from sqlalchemy import select

from config import settings
from database.models import init_db, AsyncSession, Job
from generator.generator import generate_for_job


async def run_generator(batch_size: int = 5):
    await init_db()

    async with AsyncSession() as session:
        result = await session.execute(
            select(Job)
            .where(Job.relevance_score >= settings.min_relevance_score)
            .where(Job.cover_letter == None)
            .where(Job.status != "rejected")
            .order_by(Job.relevance_score.desc())
            .limit(batch_size)
        )
        jobs = result.scalars().all()

    if not jobs:
        logger.info("No jobs need content generation")
        return

    logger.info(f"Generating resume content for {len(jobs)} jobs...")

    for job in jobs:
        logger.info(f"Generating for: {job.title} @ {job.company} (score: {job.relevance_score})")
        try:
            content = await generate_for_job(job.title, job.company, job.description or "")

            async with AsyncSession() as session:
                db_job = await session.get(Job, job.id)
                db_job.resume_bullets = content.resume_bullets
                db_job.cover_letter = content.cover_letter
                db_job.status = "reviewed"
                await session.commit()

            logger.info(f"Done: {job.title} @ {job.company}")
            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Failed for {job.title} @ {job.company}: {e}")
            continue

    logger.info("Generation complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate tailored resume bullets and cover letters")
    parser.add_argument("--batch", type=int, default=5, help="Number of jobs to process (default: 5)")
    args = parser.parse_args()

    asyncio.run(run_generator(args.batch))
