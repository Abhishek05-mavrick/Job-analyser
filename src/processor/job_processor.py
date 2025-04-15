import spacy
from typing import Dict, List, Set
from collections import Counter
from datetime import datetime

class JobProcessor:
    """Process job listings to extract insights and analyze trends."""

    def __init__(self):
        """Initialize the job processor with NLP model."""
        self.nlp = spacy.load('en_core_web_sm')
        self.common_skills = set(['python', 'java', 'javascript', 'sql', 'aws',
                                'react', 'node.js', 'docker', 'kubernetes',
                                'machine learning', 'data analysis'])
        self.work_type_keywords = {
            'On-site': ['on-site', 'onsite', 'in office', 'in-office', 'office based', 'office-based', 'on location', 'on-location', 'physical location'],
            'Remote': ['remote', 'work from home', 'wfh', 'virtual', 'telecommute', 'telework', '100% remote', 'fully remote'],
            'Hybrid': ['hybrid', 'flexible', 'partially remote', 'remote optional', 'flexible work arrangement', 'mix of remote and office']
        }

    def extract_skills(self, text: str) -> Set[str]:
    
        doc = self.nlp(text.lower())
        skills = set()

        # Extract skills based on pattern matching and known skill set
        for token in doc:
            if token.text in self.common_skills:
                skills.add(token.text)
            # Check for compound skills (e.g., 'machine learning')
            if token.i < len(doc) - 1:
                bigram = f"{token.text} {doc[token.i + 1].text}"
                if bigram in self.common_skills:
                    skills.add(bigram)

        return skills

    def analyze_salary_range(self, salary_text: str) -> Dict[str, float]:
        """Parse and normalize salary information with improved handling of various formats.

        Args:
            salary_text (str): Raw salary text from job listing

        Returns:
            Dict[str, float]: Normalized salary range with min, max, and average
        """
        try:
            if not salary_text or not isinstance(salary_text, str):
                return {'min_salary': 0.0, 'max_salary': 0.0, 'average_salary': 0.0}

            # Remove currency symbols and normalize text
            cleaned = salary_text.lower().strip()
            cleaned = cleaned.replace('$', '').replace(',', '')
            cleaned = cleaned.replace('usd', '').replace('us', '')
            
            # Handle various salary formats and multipliers
            multipliers = {
                'k': 1000,
                'm': 1000000,
                'thousand': 1000,
                'million': 1000000
            }
            
            for key, multiplier in multipliers.items():
                if key in cleaned:
                    cleaned = cleaned.replace(key, '')
                    cleaned = cleaned.strip()
                    # Extract numbers before applying multiplier
                    import re
                    numbers = [float(n) * multiplier for n in re.findall(r'\d+(?:\.\d+)?', cleaned)]
                    break
            else:
                # If no multiplier found, extract numbers normally
                numbers = [float(n) for n in re.findall(r'\d+(?:\.\d+)?', cleaned)]
            
            # Determine if salary is hourly/monthly/yearly
            time_multipliers = {
                '/hr': 2080,  # 40 hours * 52 weeks
                'per hour': 2080,
                'hourly': 2080,
                '/mo': 12,    # 12 months per year
                'per month': 12,
                'monthly': 12
            }
            
            # Apply time-based multiplier if found
            for pattern, multiplier in time_multipliers.items():
                if pattern in cleaned:
                    numbers = [n * multiplier for n in numbers]
                    break
            
            # Handle edge cases and validate numbers
            numbers = [n for n in numbers if 10000 <= n <= 1000000]  # Filter unlikely salaries
            
            if len(numbers) >= 2:
                min_sal = min(numbers)
                max_sal = max(numbers)
                return {
                    'min_salary': round(min_sal, 2),
                    'max_salary': round(max_sal, 2),
                    'average_salary': round((min_sal + max_sal) / 2, 2)
                }
            elif len(numbers) == 1:
                salary = numbers[0]
                return {
                    'min_salary': round(salary, 2),
                    'max_salary': round(salary, 2),
                    'average_salary': round(salary, 2)
                }
            
        except Exception as e:
            print(f"Error parsing salary: {str(e)}")
        
        return {
            'min_salary': 0.0,
            'max_salary': 0.0,
            'average_salary': 0.0
        }

    def get_skill_trends(self, jobs: List[Dict]) -> Dict[str, int]:
        """Analyze skill frequency across job listings.

        Args:
            jobs (List[Dict]): List of job listings

        Returns:
            Dict[str, int]: Skill frequency count
        """
        all_skills = []
        for job in jobs:
            description = job.get('description', '')
            skills = self.extract_skills(description)
            all_skills.extend(list(skills))
        
        return dict(Counter(all_skills))

    def get_location_trends(self, jobs: List[Dict]) -> Dict[str, int]:
        """Analyze job distribution by location.

        Args:
            jobs (List[Dict]): List of job listings

        Returns:
            Dict[str, int]: Job count by location
        """
        locations = [job.get('location', '').split(',')[0].strip() 
                    for job in jobs if job.get('location')]
        return dict(Counter(locations))

    def detect_work_type(self, description: str) -> str:
        if not description:
            return 'Unknown'
            
        description = description.lower()
        matches = {work_type: 0 for work_type in self.work_type_keywords.keys()}
        
        # Enhanced pattern matching with context awareness
        for work_type, keywords in self.work_type_keywords.items():
            for keyword in keywords:
                # Check for exact matches and surrounding context
                if keyword in description:
                    # Higher weight for phrases that appear in job requirements or location sections
                    if any(context in description for context in ['job type:', 'work arrangement:', 'location:', 'position type:']):
                        matches[work_type] += 2
                    else:
                        matches[work_type] += 1
                        
                # Check for negations
                if f'not {keyword}' in description or f'no {keyword}' in description:
                    matches[work_type] -= 1
        
        # Advanced decision making
        if matches:
            # Filter out negative scores
            valid_matches = {k: v for k, v in matches.items() if v > 0}
            if valid_matches:
                max_matches = max(valid_matches.values())
                max_types = [wt for wt, count in valid_matches.items() if count == max_matches]
                
                # If single clear winner
                if len(max_types) == 1:
                    return max_types[0]
                    
                # If multiple matches with same score, use priority
                priority_order = ['Remote', 'Hybrid', 'On-site']
                for work_type in priority_order:
                    if work_type in max_types:
                        return work_type
        
        return 'Unknown'

    def analyze_salary_range(self, salary_text: str) -> Dict[str, float]:
        try:
            if not salary_text or not isinstance(salary_text, str):
                return {'min_salary': 0.0, 'max_salary': 0.0, 'average_salary': 0.0}

            # Enhanced cleaning and normalization
            cleaned = salary_text.lower().strip()
            cleaned = cleaned.replace('$', '').replace(',', '')
            cleaned = cleaned.replace('usd', '').replace('us', '')
            
            # Handle ranges with various separators
            range_separators = ['-', 'to', '~', 'through', 'up to']
            
            # Handle various salary formats and multipliers with improved accuracy
            multipliers = {
                'k': 1000,
                'm': 1000000,
                'thousand': 1000,
                'million': 1000000,
                'yr': 1,
                'year': 1,
                'annual': 1
            }
            
            # Time-based multipliers with improved accuracy
            time_multipliers = {
                '/hr': 2080,
                'per hour': 2080,
                'hourly': 2080,
                '/day': 260,
                'per day': 260,
                'daily': 260,
                '/wk': 52,
                'per week': 52,
                'weekly': 52,
                '/mo': 12,
                'per month': 12,
                'monthly': 12
            }
            
            # Apply multipliers
            import re
            numbers = []
            
            # First check for time-based multipliers
            time_multiplier = 1
            for pattern, mult in time_multipliers.items():
                if pattern in cleaned:
                    time_multiplier = mult
                    cleaned = cleaned.replace(pattern, '')
                    break
            
            # Then check for magnitude multipliers
            magnitude_multiplier = 1
            for key, mult in multipliers.items():
                if key in cleaned:
                    magnitude_multiplier = mult
                    cleaned = cleaned.replace(key, '')
                    break
            
            # Extract numbers and apply both multipliers
            raw_numbers = re.findall(r'\d+(?:\.\d+)?', cleaned)
            numbers = [float(n) * magnitude_multiplier * time_multiplier for n in raw_numbers]
            
            # Validate and filter numbers
            numbers = [n for n in numbers if 10000 <= n <= 1000000]  # Annual salary range
            
            if len(numbers) >= 2:
                min_sal = min(numbers)
                max_sal = max(numbers)
                return {
                    'min_salary': round(min_sal, 2),
                    'max_salary': round(max_sal, 2),
                    'average_salary': round((min_sal + max_sal) / 2, 2)
                }
            elif len(numbers) == 1:
                salary = numbers[0]
                return {
                    'min_salary': round(salary * 0.9, 2),  # Estimate range as ±10% of single value
                    'max_salary': round(salary * 1.1, 2),
                    'average_salary': round(salary, 2)
                }
            
        except Exception as e:
            print(f"Error parsing salary: {str(e)}")
        
        return {
            'min_salary': 0.0,
            'max_salary': 0.0,
            'average_salary': 0.0
        }

    def filter_jobs_by_work_type(self, jobs: List[Dict], work_type: str) -> List[Dict]:
        """Filter jobs by work type.

        Args:
            jobs (List[Dict]): List of job listings
            work_type (str): Work type to filter by

        Returns:
            List[Dict]: Filtered job listings
        """
        if work_type == 'All':
            return jobs
        return [job for job in jobs if self.detect_work_type(job.get('description', '')) == work_type]

    def get_work_type_distribution(self, jobs: List[Dict]) -> Dict[str, int]:
        """Get distribution of jobs by work type.

        Args:
            jobs (List[Dict]): List of job listings

        Returns:
            Dict[str, int]: Count of jobs by work type
        """
        work_types = [self.detect_work_type(job.get('description', '')) for job in jobs]
        return dict(Counter(work_types))

    def get_salary_insights(self, jobs: List[Dict]) -> Dict[str, float]:
        """Calculate salary statistics across job listings.

        Args:
            jobs (List[Dict]): List of job listings

        Returns:
            Dict[str, float]: Salary statistics
        """
        salaries = []
        for job in jobs:
            try:
                if job.get('salary_range'):
                    salary_data = self.analyze_salary_range(job['salary_range'])
                    if salary_data['average_salary'] > 0:
                        salaries.append(salary_data['average_salary'])
                elif 'salary' in job:
                    salary_data = self.analyze_salary_range(str(job['salary']))
                    if salary_data['average_salary'] > 0:
                        salaries.append(salary_data['average_salary'])
            except Exception as e:
                print(f"Error processing salary for job {job.get('title', 'Unknown')}: {str(e)}")
                continue

        if not salaries:
            return {
                'min_salary': 0.0,
                'max_salary': 0.0,
                'average_salary': 0.0,
                'median_salary': 0.0
            }

        return {
            'min_salary': min(salaries),
            'max_salary': max(salaries),
            'average_salary': sum(salaries) / len(salaries),
            'median_salary': sorted(salaries)[len(salaries) // 2]
        }