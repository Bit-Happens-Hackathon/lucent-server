FROM python:3.12-slim

WORKDIR /app

# Install FastAPI and Uvicorn with all standard dependencies
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" 

# Set up Python path
ENV PYTHONPATH=/app

# Create minimal app structure if not mounted
RUN mkdir -p /app/app
RUN echo 'from fastapi import FastAPI\n\napp = FastAPI(\n    title="Lucent API",\n    description="Lucent Server API",\n    version="0.1.0"\n)\n\n@app.get("/")\nasync def root():\n    return {"message": "Welcome to Lucent API. Server is running."}\n' > /app/app/main.py

# Command to run the server
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]