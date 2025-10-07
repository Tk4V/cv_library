FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3

WORKDIR /app

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    pkg-config \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-xlib-2.0-dev \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python - --version ${POETRY_VERSION}
ENV PATH="/root/.local/bin:$PATH"

# Copy and install dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry lock --no-update && \
    poetry install --no-root --no-interaction --no-ansi --only main

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x entrypoint.sh start.sh start_prod.sh && \
    sed -i 's/\r$//' entrypoint.sh start.sh start_prod.sh

# Use entrypoint script
ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
CMD ["gunicorn", "CVProject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "30"]
