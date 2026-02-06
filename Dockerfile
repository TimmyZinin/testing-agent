# Andry Tester Bot - Dockerfile for Railway deployment
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY config/ config/
COPY bot/ bot/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Run the bot
CMD ["python", "-m", "bot.telegram_bot"]
