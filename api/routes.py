from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update
from database.models import AsyncSession, Job

router = APIRouter()


@router.get("/jobs")
async def get_jobs(status: str = None, min_score: float = 0):
    async with AsyncSession() as session:
        query = select(Job).order_by(Job.scraped_at.desc())
        if status:
            query = query.where(Job.status == status)
        if min_score > 0:
            query = query.where(Job.relevance_score >= min_score)
        result = await session.execute(query)
        jobs = result.scalars().all()
        return [_job_to_dict(j) for j in jobs]


@router.get("/jobs/{job_id}")
async def get_job(job_id: int):
    async with AsyncSession() as session:
        job = await session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return _job_to_dict(job)


@router.patch("/jobs/{job_id}/status")
async def update_status(job_id: int, status: str):
    valid = {"new", "reviewed", "applied", "rejected"}
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid}")
    async with AsyncSession() as session:
        job = await session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        job.status = status
        await session.commit()
        return {"ok": True}


@router.get("/stats")
async def get_stats():
    async with AsyncSession() as session:
        result = await session.execute(select(Job))
        jobs = result.scalars().all()
        return {
            "total": len(jobs),
            "new": sum(1 for j in jobs if j.status == "new"),
            "reviewed": sum(1 for j in jobs if j.status == "reviewed"),
            "applied": sum(1 for j in jobs if j.applied),
            "rejected": sum(1 for j in jobs if j.status == "rejected"),
            "avg_score": round(sum(j.relevance_score for j in jobs) / len(jobs), 1) if jobs else 0,
        }


def _job_to_dict(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "url": job.url,
        "skills_required": job.skills_required,
        "source": job.source,
        "relevance_score": job.relevance_score,
        "relevance_reason": job.relevance_reason,
        "resume_bullets": job.resume_bullets,
        "cover_letter": job.cover_letter,
        "status": job.status,
        "applied": job.applied,
        "applied_at": job.applied_at.isoformat() if job.applied_at else None,
        "scraped_at": job.scraped_at.isoformat() if job.scraped_at else None,
    }
