FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app    

# Expose the desired port
EXPOSE 80

# Use uvicorn to serve the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
