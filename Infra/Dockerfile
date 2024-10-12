# Step 1: Use an official Python runtime as a parent image
FROM python:3.9-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container at /app
COPY . /app

# # Step 4: Copy the model directory
# COPY '../models' /app

# # Step 5: Copy application code
# COPY '../application.py' /app

# Install PostgreSQL client and development libraries
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Install any required libraries (define your Python libraries in a requirements.txt file)
RUN pip3 install --no-cache-dir -r requirements.txt

# Step 5: Expose the port the app runs on
EXPOSE 5001

# Step 6: Define environment variable for Flask
ENV FLASK_APP=application.py

# Step 7: Run the Flask app
CMD ["python", "application.py"]
