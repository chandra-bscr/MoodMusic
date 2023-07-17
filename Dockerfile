# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code to the container
COPY . .

# Expose the port that the Flask application listens on
EXPOSE 5000

# Define the command to run the Flask application
CMD ["python", "app.py"]
