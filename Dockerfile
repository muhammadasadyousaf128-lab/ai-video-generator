FROM python:3.11-slim

# FFmpeg aur system dependencies install karo
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Project files copy karo
COPY . .

# Static aur music folders banao
RUN mkdir -p static music

EXPOSE 8000

# Backend chalao
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]