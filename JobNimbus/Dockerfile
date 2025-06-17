# Use official Python slim image
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Expose Flask port
EXPOSE 5000

# Run tests first (optional)
RUN pytest || echo "Tests failed"

# Default command to run the Flask app
CMD ["python", "run.py"]
