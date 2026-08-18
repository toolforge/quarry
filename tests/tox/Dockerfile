FROM docker-registry.wikimedia.org/python3-trixie:latest

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    tox redis

RUN pip install --break-system-packages --ignore-installed --upgrade pip wheel && \
    pip install --break-system-packages poetry

COPY . /quarry
WORKDIR /quarry

ENTRYPOINT ["tox"]
