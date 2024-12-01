# Use an official Python runtime as a parent image
FROM python:3.9.7-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY configure_mongo_cluster.py /app

# Install any needed dependencies
RUN pip install --no-cache-dir pymongo

# Run configure_mongo_cluster.py when the container starts
CMD ["python", "configure_mongo_cluster.py"]
