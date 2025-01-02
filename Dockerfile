# Use the official Python image as a base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements.txt file to the container
COPY requirements.txt /code/

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the current directory contents into the container at /code
COPY . /code/

# Expose the port Django will run on
EXPOSE 8000

# Define the command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
