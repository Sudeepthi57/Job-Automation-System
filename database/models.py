from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    url = Column(String(1000), unique=True, nullable=False)
    description = Column(Text)
    skills_required = Column(Text)           # comma-separated
    source = Column(String(100))             # linkedin, indeed, etc.

    relevance_score = Column(Float, default=0.0)
    relevance_reason = Column(Text)

    resume_bullets = Column(Text)            # AI-generated tailored bullets
    cover_letter = Column(Text)              # AI-generated cover letter

    status = Column(String(50), default="new")  # new, reviewed, applied, rejected
    applied = Column(Boolean, default=False)
    applied_at = Column(DateTime, nullable=True)

    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


engine = create_async_engine(settings.database_url, echo=False)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
