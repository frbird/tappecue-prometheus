# Use the official lightweight Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY tappecue_monitor.py .

# Set environment variables
ENV CONFIG_FILE=config.yaml

# Set file permissions
RUN touch tappecue.log && chmod 755 tappecue.log

# Command to run the application
CMD ["python", "tappecue_monitor.py"]