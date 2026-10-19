FROM python:3.14-alpine AS csm-backend
LABEL org.opencontainers.image.authors="zacheryfudge+docker@gmail.com"
WORKDIR /backend
RUN apk update && apk add --no-cache curl python3-dev libpq-dev gcc
COPY src /backend/src/
COPY logs.ini requirements.txt /backend/
RUN pip install -r requirements.txt
RUN for dir in src/plugins/device_plugins/*/; do \
  if [ -f "${dir}requirements.txt" ]; then \
  pip install -r "${dir}requirements.txt"; \
  fi; done

FROM eclipse-mosquitto:2.0.20 AS csm-mqtt
COPY mosquitto/mosquitto.conf /mosquitto/config/mosquitto.conf
COPY mosquitto/conf.d/mosquitto.conf /mosquitto/config/conf.d/mosquitto.conf
COPY scripts/mqtt_healthcheck.sh /usr/local/bin/healthcheck.sh
