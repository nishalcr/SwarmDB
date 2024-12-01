# Use the official Python base image
FROM python:3.9-slim

# Set the environment variable to prevent buffering of Python output
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script into the container
COPY consumer.py /app/

# Copy the Python config into the container
COPY config.json /app/

# Set the entry point to run the script
ENTRYPOINT ["python", "consumer.py"]
