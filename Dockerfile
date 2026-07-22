FROM python:3.12-slim

WORKDIR /app

# Install only what's needed
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY app.py .

# Notes directory for persistent markdown files
RUN mkdir /data
VOLUME /data

ENV NOTES_DIR=/data

EXPOSE 5004

CMD ["python", "app.py"]
