FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure data directory exists
RUN mkdir -p /app/data

EXPOSE 5000

# Use gunicorn for production-grade serving
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
