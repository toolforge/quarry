FROM docker-registry.wikimedia.org/python3-bookworm:latest

# Create Quarry user, create /results folder owned by this user,
# to be mounted as volume to be shared between web and runner in dev setup
RUN useradd -r -m quarry && \
    mkdir /results && \
    chown -R quarry: /results

WORKDIR /app

COPY requirements.txt /app
# Install dependencies
# TODO: Use a venv instead of --break-system-packages
# TODO: Use newer pip. That requires newer celery, which in turn requires
# newer versions of basically everything else.
RUN pip install --break-system-packages --upgrade pip==24.0 wheel && \
    pip install --break-system-packages -r requirements.txt

# Copy app code
USER quarry
COPY . /app

# Expose port for web server
EXPOSE 5000

# Entrypoint is set elsewhere, as it's different for web and worker
