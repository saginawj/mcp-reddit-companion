FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Create and activate virtual environment
RUN uv venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install dependencies
RUN uv pip install .

# Set environment variables
ENV PYTHONPATH=/app

# Run the MCP server
CMD ["python", "-m", "src.mcp_reddit_companion.server"] 