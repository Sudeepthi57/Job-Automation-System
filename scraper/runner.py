import asyncio
from loguru import logger
from sqlalchemy import select

from config import settings
from database.models import init_db, AsyncSession, Job
from scraper.linkedin import LinkedInScraper


async def run_scraper(keyword: str = None, location: str = "India", max_jobs: int = 20):
    await init_db()

    keyword = keyword or settings.target_role
    logger.info(f"Scraping LinkedIn for: '{keyword}' in '{location}' (max {max_jobs} jobs)")

    scraper = LinkedInScraper()
    raw_jobs = await scraper.scrape(keyword, location, max_jobs)

    saved, skipped = 0, 0

    async with AsyncSession() as session:
        for raw in raw_jobs:
            # Skip duplicates by URL
            existing = await session.execute(select(Job).where(Job.url == raw.url))
            if existing.scalar_one_or_none():
                skipped += 1
                continue

            job = Job(
                title=raw.title,
                company=raw.company,
                location=raw.location,
                url=raw.url,
                description=raw.description,
                skills_required=raw.skills,
                source=raw.source,
            )
            session.add(job)
            saved += 1

        await session.commit()

    logger.info(f"Done — saved: {saved}, skipped (duplicate): {skipped}")
    return saved, skipped


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape LinkedIn jobs")
    parser.add_argument("--keyword", default=None, help="Job title to search (default: TARGET_ROLE from .env)")
    parser.add_argument("--location", default="India", help="Location (default: India)")
    parser.add_argument("--max", type=int, default=20, help="Max jobs to scrape (default: 20)")
    args = parser.parse_args()

    asyncio.run(run_scraper(args.keyword, args.location, args.max))
