# Audris - DORA Assessment Tool

A comprehensive DORA (Digital Operational Resilience Act) compliance assessment tool for EU-regulated financial institutions. Audris helps organizations identify, assess, and manage ICT-related vendor risks while ensuring regulatory compliance through advanced AI-powered analysis.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Authors & Acknowledgements](#authors--acknowledgements)

---

## Features

- **Contract Analysis**: AI-powered extraction of DORA-relevant clauses from vendor contracts
- **Risk Assessment**: Machine learning-based ICT risk scoring with 90% accuracy
- **Vendor Onboarding**: Streamlined vendor registration with automated data extraction
- **Regulatory Register**: Comprehensive vendor and service documentation
- **Compliance Tracking**: Audit logs and regulatory alert monitoring
- **API Integration**: RESTful API with JWT authentication
- **SyntechAI Ecosystem**: Integration with Runegard for regulatory data
- **Multi-format Support**: PDF and DOCX document processing

## Tech Stack

- **Language**: Python 3.11+
- **Web Framework**: Streamlit (UI), FastAPI (API)
- **Database**: PostgreSQL with connection pooling
- **AI/ML**: OpenAI GPT-4o, scikit-learn, spaCy
- **Authentication**: JWT tokens
- **Document Processing**: pdfplumber, python-docx, trafilatura
- **External APIs**: OpenAI, Twilio, Jira integration
- **Deployment**: Replit-optimized with Docker support

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- OpenAI API key (for advanced features)

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_GITHUB_USERNAME/audris-dora-assessment.git
cd audris-dora-assessment

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy the example env file and configure your settings
cp .env.example .env
# Edit .env with your API keys and database settings

# 5. Initialize the database
python -c "from app.database.handler import DatabaseHandler; DatabaseHandler().init_schema()"

# 6. Start the Streamlit application
streamlit run ui/streamlit_app.py --server.port 5000

# 7. (Optional) Start the API server
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

## Configuration

### Required Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database
PGHOST=localhost
PGPORT=5432
PGUSER=your_username
PGPASSWORD=your_password
PGDATABASE=your_database

# API Keys
OPENAI_API_KEY=sk-your-openai-api-key

# Optional Integrations
RUNEGARD_API_KEY=your-runegard-key
RUNEGARD_API_URL=https://api.runegard.com

# Twilio (for SMS alerts)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number

# Jira Integration (for ticketing)
JIRA_ENABLED=true
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_PROJECT_KEY=DORA
JIRA_USERNAME=your-email@domain.com
JIRA_API_TOKEN=your-jira-token
```

### API Configuration

The application includes a FastAPI server for programmatic access:

- API runs on port 8000 by default
- JWT authentication required for protected endpoints
- Swagger documentation available at `/docs`

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python test_dora_app.py
python test_api_client.py
python test_ml_model.py

# Quick validation test
python quick_test.py
```

## Deployment

### Replit Deployment

The application is optimized for Replit deployment:

1. Import the project to Replit
2. Configure secrets in the Replit environment
3. Run using the configured workflow

### Docker Deployment

```bash
# Build the container
docker build -t audris-dora .

# Run with environment variables
docker run -p 5000:5000 --env-file .env audris-dora
```

### Manual Deployment

Ensure your production environment has:
- Python 3.11+
- PostgreSQL database
- Required environment variables
- SSL certificates for HTTPS

## Troubleshooting

### Common Issues

**Database Connection Issues**
- Verify PostgreSQL is running and accessible
- Check DATABASE_URL format and credentials
- Ensure database exists and user has proper permissions

**OpenAI API Issues**
- Verify API key is valid and has sufficient quota
- Check for rate limiting or billing issues
- Application includes fallback processing without OpenAI

**File Upload Problems**
- Ensure uploaded files are PDF or DOCX format
- Check file size limits (10MB default)
- Verify sufficient disk space for temporary files

**Performance Issues**
- Consider upgrading to full spaCy language model
- Monitor database connection pool usage
- Check available memory for ML model operations

### Logs and Monitoring

- Application logs: `dora_assessment.log`
- Database logs: Check PostgreSQL logs
- API logs: Available through FastAPI logging
- Streamlit logs: Console output during development

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors & Acknowledgements

- **SyntechAI Team** - Initial development and architecture
- **EU Regulatory Authorities** - DORA technical standards and guidelines
- **Open Source Community** - Supporting libraries and frameworks

### Third-Party Acknowledgements

- OpenAI for GPT-4o language model
- Streamlit for the web application framework
- FastAPI for the REST API framework
- PostgreSQL for robust data storage
- scikit-learn for machine learning capabilities

---

For support or questions, please open an issue on GitHub or contact the development team.
