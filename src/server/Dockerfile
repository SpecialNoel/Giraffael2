# Docketfile

# Used to set a default template/blueprint for Docker Image

FROM python:3.11-slim

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
