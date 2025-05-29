# Use official Python image
FROM python:3.13-slim

# Install uv package manager
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy all source code first
COPY . .

# Install dependencies and package
RUN uv pip install --system -e .

# Default command
CMD ["python", "run.py"]
