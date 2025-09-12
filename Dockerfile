# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app  

# Install any necessary system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copies all the files in the current directory to the working directory inside the container
COPY . . 

# Set environment variables
ENV FLASK_ENV=production

# Expose the port your Flask app runs on (default is 5000)
EXPOSE 5000

# Start the Flask application using Gunicorn
# Adjust the command according to your app's entry point
# Assuming your Flask app instance is named 'app' in run.py and listens on port 5000 and runs with gunicorn server
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]  