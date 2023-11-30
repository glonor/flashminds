# Use the clearlinux/tesseract-ocr image as the base image
FROM clearlinux/tesseract-ocr

# Expose port 5003 for incoming connections
EXPOSE 5003

# Copy the trained data for English language to the container
COPY eng.traineddata /usr/share/tessdata

# Set the working directory inside the container to /app
WORKDIR /app

# Create uploads directory inside the container
RUN mkdir /app/uploads

COPY requirements.txt /app

# Install the Python dependencies listed in requirements.txt using pip
RUN pip install -r requirements.txt

# Copy the data_layer_service.py file from the host to the container's /app directory
COPY . /app

# Define the command to run when the container starts
CMD python -u ocr_service.py