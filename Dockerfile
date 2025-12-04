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
COPY . /app

# Build JS assets
RUN apt-get update &&  \
    apt-get install -y nodejs npm && \
    NODE_ENV=production npm ci && \
    npm run build && \
    # Once the build is run, dependencies are no longer needed, delete them
    # to keep image small
    rm -rf node_modules &&  \
    apt-get remove -y nodejs npm && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

USER quarry

# Expose port for web server
EXPOSE 5000

# Entrypoint is set elsewhere, as it's different for web and worker
