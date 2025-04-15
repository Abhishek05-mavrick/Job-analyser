from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

class BaseScraper(ABC):
    """Base class for all job scrapers implementing common functionality."""

    def __init__(self, base_url: str):
        """Initialize the scraper with base URL.

        Args:
            base_url (str): The base URL of the job board
        """
        self.base_url = base_url

    @abstractmethod
    async def search_jobs(self, query: str, location: Optional[str] = None, 
                         num_pages: int = 1) -> List[Dict]:
        """Search for jobs based on query and location.

        Args:
            query (str): Job search query (e.g., "python developer")
            location (str, optional): Job location. Defaults to None.
            num_pages (int, optional): Number of pages to scrape. Defaults to 1.

        Returns:
            List[Dict]: List of job listings with details
        """
        pass

    @abstractmethod
    async def get_job_details(self, job_url: str) -> Dict:
        """Get detailed information about a specific job.

        Args:
            job_url (str): URL of the job listing

        Returns:
            Dict: Detailed job information
        """
        pass

    def _normalize_job_data(self, raw_job: Dict) -> Dict:
        """Normalize raw job data into a standard format.

        Args:
            raw_job (Dict): Raw job data from scraper

        Returns:
            Dict: Normalized job data
        """
        return {
            'title': raw_job.get('title', ''),
            'company': raw_job.get('company', ''),
            'location': raw_job.get('location', ''),
            'description': raw_job.get('description', ''),
            'salary_range': raw_job.get('salary_range', ''),
            'skills': raw_job.get('skills', []),
            'url': raw_job.get('url', ''),
            'posted_date': raw_job.get('posted_date', datetime.now().isoformat()),
            'source': raw_job.get('source', self.__class__.__name__)
        }