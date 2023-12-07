# Use the official Python 3.12 image as the base image
FROM python:3.8

# Set the working directory inside the container to /app
WORKDIR /app

COPY requirements.txt /app

# Install the Python dependencies listed in requirements.txt using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the business_logic_service.py file from the host to the container's /app directory
COPY . /app

# Define the command to run when the container starts
CMD ["python", "-u","bot_run.py"]
