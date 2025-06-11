# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install yt-dlp and ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install yt-dlp && \
    apt-get clean

# Copy app files
COPY app.py .

# Expose the port
EXPOSE 8080

# Run the app
CMD ["python", "app.py"]