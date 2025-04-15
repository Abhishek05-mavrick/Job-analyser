# Job Market Analyzer - An Intelligent Career Insight Engine

A data-driven analytics dashboard that provides real-time job market insights, skill trend analysis, and personalized career recommendations.

## 🎯 Features

- **Skill Demand Trend Analyzer**
  - Real-time analysis of top skills
  - Emerging skill trend visualization
  - Historical trend tracking

- **Location-Wise Heatmap**
  - Geographic distribution of job opportunities
  - Interactive filtering by skills/roles
  - Regional demand analysis

- **Salary Prediction Model**
  - ML-powered salary predictions
  - Factor-based analysis (skills, location, experience)
  - Market rate insights

- **Resume Matcher**
  - Resume skill extraction
  - Market readiness scoring
  - Personalized skill recommendations

## 🔧 Tech Stack

### Data Processing
- Python 3.x
- Pandas
- NumPy
- SQLite/PostgreSQL

### Web Scraping
- BeautifulSoup/Scrapy
- Selenium (optional)

### ML & NLP
- spaCy/BERT
- Scikit-learn
- XGBoost

### Visualization
- Streamlit
- Plotly
- Seaborn

### Resume Parsing
- PyMuPDF
- pdfminer.six

## 📦 Project Structure

```
.
├── data/               # Dataset storage
├── notebooks/          # Jupyter notebooks for analysis
├── src/                # Source code
│   ├── scraper/        # Web scraping modules
│   ├── processor/      # Data processing pipeline
│   ├── ml/             # Machine learning models
│   ├── api/            # API endpoints
│   └── dashboard/      # Streamlit dashboard
├── tests/              # Unit tests
└── requirements.txt    # Project dependencies
```

## 🚀 Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the dashboard: `streamlit run src/dashboard/main.py`

## 📈 Future Enhancements

- AI-powered career advice
- Email alerts for trending skills
- User accounts and progress tracking

## 📄 License

MIT