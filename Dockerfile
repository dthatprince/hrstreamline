# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Set environment (use development config)
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV CONFIG_CLASS=config.DevelopmentConfig
ENV FLASK_RUN_HOST=0.0.0.0

# Ensure instance folder exists
RUN mkdir -p /app/instance

# Expose port
EXPOSE 5000

# Run Flask app
CMD ["flask", "run"]
