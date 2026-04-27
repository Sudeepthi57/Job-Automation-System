from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class RawJob:
    title: str
    company: str
    location: str
    url: str
    description: str
    skills: str
    source: str


class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self, keyword: str, location: str, max_jobs: int) -> List[RawJob]:
        pass
