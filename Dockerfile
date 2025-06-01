FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads

# Expose ports
EXPOSE 5000 8000

# Environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=5000
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/_stcore/health || exit 1

# Start command
CMD ["streamlit", "run", "ui/streamlit_app.py", "--server.port", "5000", "--server.address", "0.0.0.0"]