FROM docker-registry.wikimedia.org/python3-bookworm:latest

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    tox

COPY . /quarry
WORKDIR /quarry

ENTRYPOINT ["tox"]
