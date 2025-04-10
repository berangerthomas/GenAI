FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all necessary files
COPY . .

# Ensure chroma_db directory exists and has proper permissions
RUN mkdir -p chroma_db && chmod -R 777 chroma_db

# Expose the port
EXPOSE 8000

# Run Chainlit with proper host and port
CMD ["chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]