FROM docker-registry.wikimedia.org/python3-bookworm:latest

# Create Quarry user, create /results folder owned by this user,
# to be mounted as volume to be shared between web and runner in dev setup
RUN useradd -r -m quarry && \
    mkdir /results && \
    chown -R quarry: /results

WORKDIR /app

# 1. Update pip, install Poetry, and set venv path
RUN pip install --break-system-packages --upgrade pip==24.0 wheel && \
    pip install --break-system-packages poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="/app/.venv/bin:$PATH"

# 2. Copy dependency files
COPY pyproject.toml poetry.lock /app/

# 3. Install dependencies via Poetry (no --break-system-packages needed)
RUN poetry install --no-root --only main --no-interaction

# 4. Ensure quarry user can access the virtual environment
RUN chown -R quarry:quarry /app/.venv

# Copy app code
USER quarry
COPY . /app

# Expose port for web server
EXPOSE 5000

# Entrypoint is set elsewhere, as it's different for web and worker
