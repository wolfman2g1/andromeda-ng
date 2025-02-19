FROM python:3.10-slim

# Install system dependencies (adjust these based on your project's needs)
RUN apt-get update && apt-get install -y gcc libpq-dev python3-dev curl  # Common dependencies
# Add any other system packages your project requires here.  For example:
# RUN apt-get install -y libssl-dev  # If you need OpenSSL libraries
# RUN apt-get install -y build-essential  # If you need build tools

# Python environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# Copy only the necessary files *before* installing dependencies (important for caching)
COPY pyproject.toml poetry.lock ./ 
COPY . ./  

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="$PATH:/root/.local/bin"

# Ensure virtualenvs are disabled (generally recommended for Docker)
RUN poetry config virtualenvs.create false

# Install project dependencies (using --no-cache to avoid potential issues)
RUN poetry install --no-root -vvv  # Install project dependencies. The --no-root option installs dependencies in the container's virtual environment, not the system environment.

# Expose port and set healthcheck
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl http://localhost:8000/api/v1/ping || exit 1  # Replace with your actual healthcheck endpoint

# Set the entrypoint (how your application starts)
CMD ["poetry", "run", "python", "app/app.py"] # Or "python app.py" if it's in the root.