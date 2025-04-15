from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import aiohttp
from datetime import datetime
from .base_scraper import BaseScraper

class IndeedScraper(BaseScraper):
    """Scraper for Indeed job listings."""

    def __init__(self):
        super().__init__('https://www.indeed.com')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def search_jobs(self, query: str, location: Optional[str] = None, 
                         num_pages: int = 1) -> List[Dict]:
        """Search for jobs on Indeed.

        Args:
            query (str): Job search query
            location (str, optional): Job location. Defaults to None.
            num_pages (int, optional): Number of pages to scrape. Defaults to 1.

        Returns:
            List[Dict]: List of job listings
        """
        jobs = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for page in range(num_pages):
                url = self._build_search_url(query, location, page)
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            jobs.extend(self._parse_search_results(soup))
                except Exception as e:
                    print(f"Error scraping page {page}: {str(e)}")
        return jobs

    async def get_job_details(self, job_url: str) -> Dict:
        """Get detailed job information from Indeed listing.

        Args:
            job_url (str): URL of the job listing

        Returns:
            Dict: Detailed job information
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(job_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        return self._parse_job_details(soup, job_url)
            except Exception as e:
                print(f"Error getting job details: {str(e)}")
        return {}

    def _build_search_url(self, query: str, location: Optional[str], page: int) -> str:
        """Build Indeed search URL with parameters."""
        base_query = f"/jobs?q={query.replace(' ', '+')}"
        if location:
            base_query += f"&l={location.replace(' ', '+')}"
        if page > 0:
            base_query += f"&start={page * 10}"
        return f"{self.base_url}{base_query}"

    def _parse_search_results(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse job listings from search results page."""
        jobs = []
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        for card in job_cards:
            try:
                job_data = {
                    'title': card.find('h2', class_='jobTitle').get_text(strip=True),
                    'company': card.find('span', class_='companyName').get_text(strip=True),
                    'location': card.find('div', class_='companyLocation').get_text(strip=True),
                    'url': self.base_url + card.find('a', class_='jcs-JobTitle')['href'],
                    'description': card.find('div', class_='job-snippet').get_text(strip=True),
                    'posted_date': datetime.now().isoformat(),
                    'source': 'Indeed'
                }
                jobs.append(self._normalize_job_data(job_data))
            except Exception as e:
                print(f"Error parsing job card: {str(e)}")
        
        return jobs

    def _parse_job_details(self, soup: BeautifulSoup, job_url: str) -> Dict:
        """Parse detailed job information."""
        try:
            job_data = {
                'title': soup.find('h1', class_='jobsearch-JobInfoHeader-title').get_text(strip=True),
                'company': soup.find('div', class_='jobsearch-CompanyInfoContainer').get_text(strip=True),
                'location': soup.find('div', class_='jobsearch-JobInfoHeader-subtitle').get_text(strip=True),
                'description': soup.find('div', id='jobDescriptionText').get_text(strip=True),
                'url': job_url,
                'posted_date': datetime.now().isoformat(),
                'source': 'Indeed'
            }

            # Extract salary if available
            salary_element = soup.find('div', class_='jobsearch-JobMetadataHeader-item')
            if salary_element:
                job_data['salary_range'] = salary_element.get_text(strip=True)

            return self._normalize_job_data(job_data)
        except Exception as e:
            print(f"Error parsing job details: {str(e)}")
            return {}