# Use Python 3.11 as the base image
FROM python:3.11

# Disable Python output buffering (logs appear immediately)
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy requirements file first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your application code
COPY . .

# Run your app with Gunicorn (production server)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]