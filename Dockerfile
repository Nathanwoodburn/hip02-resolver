FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

# Install curl
RUN apk add --update curl openssl

ENTRYPOINT ["python3"]
CMD ["server.py"]

FROM builder as dev-envs