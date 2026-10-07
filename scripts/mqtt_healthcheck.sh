#!/bin/sh

echo "Checking if mqtt is healthy..."

error_code=$(mosquitto_sub -h localhost -C 1 -i docker_healthcheck_client -W 1 -t topic 2>&1)

wait

echo "Error code: $error_code"

if [[ $(echo $error_code | grep Error | wc -l) -gt 0 ]]; then
    echo "MQTT is not healthy"
    exit 1
else
    echo "MQTT is healthy"
    exit 0
fi

