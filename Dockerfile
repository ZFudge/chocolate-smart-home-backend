FROM python:3.12-alpine AS base
LABEL org.opencontainers.image.authors="zacheryfudge+docker@gmail.com"
WORKDIR /backend
RUN apk add --no-cache curl
COPY . /backend/
RUN mkdir -p /var/logs/csm/

FROM base AS csm-backend
COPY scripts/csm.sh /etc/profile.d/csm.sh
RUN pip install pipenv && pipenv install

FROM base AS csm-scheduler
RUN pip install -r requirements.txt
RUN for dir in src/plugins/device_plugins/*/; do \
  if [ -f "${dir}requirements.txt" ]; then \
  pip install -r "${dir}requirements.txt"; \
  fi; done

FROM eclipse-mosquitto:2.0.20 AS csm-mqtt
COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY scripts/mqtt_healthcheck.sh /usr/local/bin/healthcheck.sh
