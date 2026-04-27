import asyncio
import random
from typing import List
from playwright.async_api import async_playwright, Page, TimeoutError as PWTimeout
from loguru import logger

from scraper.base import BaseScraper, RawJob


class LinkedInScraper(BaseScraper):
    BASE_URL = "https://www.linkedin.com"

    async def scrape(self, keyword: str, location: str, max_jobs: int = 20) -> List[RawJob]:
        jobs: List[RawJob] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # headless=False so you can log in
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()

            await self._login(page)
            job_urls = await self._collect_job_urls(page, keyword, location, max_jobs)
            logger.info(f"Found {len(job_urls)} job links")

            for i, url in enumerate(job_urls):
                try:
                    job = await self._scrape_job_detail(page, url)
                    if job:
                        jobs.append(job)
                        logger.info(f"[{i+1}/{len(job_urls)}] Scraped: {job.title} @ {job.company}")
                    await self._human_delay(2, 4)
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {e}")
                    continue

            await browser.close()

        return jobs

    async def _login(self, page: Page):
        await page.goto(f"{self.BASE_URL}/login")
        logger.info("Please log in to LinkedIn in the browser window...")
        # Wait until the user is on the feed (post-login)
        await page.wait_for_url("**/feed/**", timeout=120_000)
        logger.info("Login detected — starting scrape")

    async def _collect_job_urls(self, page: Page, keyword: str, location: str, max_jobs: int) -> List[str]:
        search_url = (
            f"{self.BASE_URL}/jobs/search/"
            f"?keywords={keyword.replace(' ', '%20')}"
            f"&location={location.replace(' ', '%20')}"
            f"&f_TPR=r86400"   # last 24 hours
        )
        await page.goto(search_url)
        await page.wait_for_load_state("networkidle")
        await self._human_delay(2, 3)

        job_urls: List[str] = []
        seen: set = set()

        while len(job_urls) < max_jobs:
            cards = await page.query_selector_all("a.job-card-list__title--link, a.job-card-container__link")
            for card in cards:
                href = await card.get_attribute("href")
                if href and "/jobs/view/" in href:
                    clean = href.split("?")[0]
                    if clean not in seen:
                        seen.add(clean)
                        job_urls.append(clean)

            if len(job_urls) >= max_jobs:
                break

            # Scroll to load more
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self._human_delay(1.5, 2.5)

            # Try clicking "See more jobs" button if present
            try:
                btn = page.locator("button:has-text('See more jobs')")
                if await btn.is_visible():
                    await btn.click()
                    await self._human_delay(2, 3)
            except Exception:
                break

        return job_urls[:max_jobs]

    async def _scrape_job_detail(self, page: Page, url: str) -> RawJob | None:
        full_url = url if url.startswith("http") else f"{self.BASE_URL}{url}"
        await page.goto(full_url)
        await page.wait_for_load_state("networkidle")
        await self._human_delay(1, 2)

        # Expand "See more" in description if present
        try:
            see_more = page.locator("button:has-text('See more')")
            if await see_more.first.is_visible():
                await see_more.first.click()
                await self._human_delay(0.5, 1)
        except Exception:
            pass

        title = await self._safe_text(page, "h1.job-details-jobs-unified-top-card__job-title, h1.t-24")
        company = await self._safe_text(page, "a.job-details-jobs-unified-top-card__company-name, .topcard__org-name-link")
        location = await self._safe_text(page, ".job-details-jobs-unified-top-card__bullet, .topcard__flavor--bullet")
        description = await self._safe_text(page, "div.jobs-description__content, div#job-details")
        skills = await self._extract_skills(page)

        if not title or not company:
            return None

        return RawJob(
            title=title.strip(),
            company=company.strip(),
            location=location.strip() if location else "",
            url=full_url,
            description=description.strip() if description else "",
            skills=skills,
            source="linkedin",
        )

    async def _extract_skills(self, page: Page) -> str:
        try:
            skill_els = await page.query_selector_all(".job-details-skill-match-status-list__skill-item, .job-details-how-you-match__skills-item")
            skills = [await el.inner_text() for el in skill_els]
            return ", ".join(s.strip() for s in skills if s.strip())
        except Exception:
            return ""

    async def _safe_text(self, page: Page, selector: str) -> str:
        try:
            el = page.locator(selector).first
            if await el.is_visible(timeout=3000):
                return await el.inner_text()
        except PWTimeout:
            pass
        except Exception:
            pass
        return ""

    async def _human_delay(self, min_sec: float, max_sec: float):
        await asyncio.sleep(random.uniform(min_sec, max_sec))
