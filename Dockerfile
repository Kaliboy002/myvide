# Use the official Python 3.9 slim image
FROM python:3.9-slim

# Install FFmpeg and required libraries
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libfreetype6 \
    libx11-6 \
    libx264-dev \
    && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot's code
COPY . .

# Set environment variables for Telegram API credentials
ENV TELEGRAM_API_ID='YOUR_API_ID'
ENV TELEGRAM_API_HASH='YOUR_API_HASH'
ENV BOT_TOKEN='YOUR_BOT_TOKEN'

# Command to run the bot
CMD ["python", "video_compression_bot.py"]
