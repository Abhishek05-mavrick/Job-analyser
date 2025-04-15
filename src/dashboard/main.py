import streamlit as st
import plotly.express as px
import pandas as pd
from typing import List, Dict
import sys
import os
import asyncio

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import IndeedScraper, LinkedInScraper
from processor.job_processor import JobProcessor

class JobMarketDashboard:
    def __init__(self):
        self.job_processor = JobProcessor()
        self.indeed_scraper = IndeedScraper()
        self.linkedin_scraper = LinkedInScraper()

    def run(self):
        st.set_page_config(page_title="Job Market Analyzer", layout="wide")

        # Sidebar for search inputs
        with st.sidebar:
            st.title("Job Market Analyzer 📊")
            st.header("Search Parameters")
            query = st.text_input("Job Title/Skills", "Python Developer")
            location = st.text_input("Location", "Remote")
            work_type = st.selectbox("Work Type", ["All", "On-site", "Remote", "Hybrid"])
            source = st.multiselect("Job Sources", ["Indeed", "LinkedIn"], default=["Indeed", "LinkedIn"])
            num_pages = st.slider("Number of Pages", 1, 10, 3)
            analyze_button = st.button("Analyze Jobs")

        # Main panel content
        if analyze_button:
            with st.spinner("Fetching job data..."):
                jobs = asyncio.run(self.fetch_jobs(query, location, source, num_pages))
                if jobs:
                    # Filter jobs by work type
                    filtered_jobs = self.job_processor.filter_jobs_by_work_type(jobs, work_type)
                    self.display_insights(filtered_jobs)
                else:
                    st.error("No jobs found. Please try different search parameters.")

    async def fetch_jobs(self, query: str, location: str, sources: List[str], num_pages: int) -> List[Dict]:
        """Fetch jobs from selected sources."""
        jobs = []
        if "Indeed" in sources:
            indeed_jobs = await self.indeed_scraper.search_jobs(query, location, num_pages)
            jobs.extend(indeed_jobs)
        if "LinkedIn" in sources:
            linkedin_jobs = await self.linkedin_scraper.search_jobs(query, location, num_pages)
            jobs.extend(linkedin_jobs)
        return jobs

    def display_insights(self, jobs: List[Dict]):
        """Display various insights from job data."""
        try:
            st.title("Job Market Analysis Results")
            
            # Create three columns for key metrics
            col1, col2, col3 = st.columns(3)

            total_jobs = len(jobs)
            with col1:
                st.metric("Total Jobs Found", total_jobs)
            with col2:
                unique_companies = len(set(job['company'] for job in jobs if job.get('company')))
                st.metric("Unique Companies", unique_companies)
            with col3:
                salary_insights = self.job_processor.get_salary_insights(jobs)
                if salary_insights['average_salary'] > 0:
                    st.metric("Average Salary", f"${salary_insights['average_salary']:,.2f}/year")
                else:
                    st.metric("Average Salary", "Not available")

            if total_jobs > 0:
                # Skills Analysis
                st.header("Skills in Demand")
                skill_trends = self.job_processor.get_skill_trends(jobs)
                if skill_trends:
                    skill_df = pd.DataFrame(list(skill_trends.items()), columns=['Skill', 'Count'])
                    skill_df = skill_df.sort_values('Count', ascending=False).head(10)
                    if not skill_df.empty:
                        fig = px.bar(skill_df, x='Skill', y='Count',
                                    title='Top 10 Most In-Demand Skills')
                        st.plotly_chart(fig)
                    else:
                        st.info("No skill data available")

                # Work Type Distribution
                st.header("Work Type Distribution")
                work_type_dist = self.job_processor.get_work_type_distribution(jobs)
                if work_type_dist:
                    work_type_df = pd.DataFrame(list(work_type_dist.items()),
                                            columns=['Work Type', 'Job Count'])
                    if not work_type_df.empty:
                        fig = px.pie(work_type_df, values='Job Count', names='Work Type',
                                    title='Job Distribution by Work Type')
                        st.plotly_chart(fig)
                    else:
                        st.info("No work type data available")

                # Location Analysis
                st.header("Job Distribution by Location")
                location_trends = self.job_processor.get_location_trends(jobs)
                if location_trends:
                    location_df = pd.DataFrame(list(location_trends.items()), 
                                            columns=['Location', 'Job Count'])
                    if not location_df.empty:
                        fig = px.pie(location_df, values='Job Count', names='Location',
                                    title='Job Distribution by Location')
                        st.plotly_chart(fig)
                    else:
                        st.info("No location data available")

                # Salary Analysis
                st.header("Salary Insights")
                if salary_insights['average_salary'] > 0:
                    salary_df = pd.DataFrame([
                        {"Type": "Minimum", "Salary": salary_insights['min_salary']},
                        {"Type": "Maximum", "Salary": salary_insights['max_salary']},
                        {"Type": "Average", "Salary": salary_insights['average_salary']},
                        {"Type": "Median", "Salary": salary_insights['median_salary']}
                    ])
                    salary_df['Formatted_Salary'] = salary_df['Salary'].apply(lambda x: f'${x:,.2f}/year')
                    fig = px.bar(salary_df, x='Type', y='Salary',
                                title='Salary Distribution',
                                labels={'Salary': 'Annual Salary ($)'},
                                text='Formatted_Salary')
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig)
                else:
                    st.info("No salary data available")

                # Recent Job Listings
                st.header("Recent Job Listings")
                for job in jobs[:10]:  # Display most recent 10 jobs
                    try:
                        with st.expander(f"{job.get('title', 'Untitled')} at {job.get('company', 'Unknown Company')}"):
                            st.write(f"🏢 Company: {job.get('company', 'Unknown')}")
                            st.write(f"📍 Location: {job.get('location', 'Location not specified')}")
                            if job.get('salary_range'):
                                salary_data = self.job_processor.analyze_salary_range(job['salary_range'])
                                if salary_data['min_salary'] == salary_data['max_salary']:
                                    if salary_data['average_salary'] > 0:
                                        st.write(f"💰 Salary: ${salary_data['average_salary']:,.2f}/year")
                                else:
                                    st.write(f"💰 Salary Range: ${salary_data['min_salary']:,.2f} - ${salary_data['max_salary']:,.2f}/year")
                            st.write(f"🔗 URL: {job.get('url', '#')}")
                            st.write("📝 Description:")
                            st.write(job.get('description', 'No description available'))
                    except Exception as e:
                        print(f"Error displaying job listing: {str(e)}")
                        continue
            else:
                st.warning("No jobs found matching your criteria. Try adjusting your search parameters.")
        except Exception as e:
            st.error(f"An error occurred while displaying insights: {str(e)}")
            print(f"Error in display_insights: {str(e)}")

if __name__ == "__main__":
    dashboard = JobMarketDashboard()
    dashboard.run()