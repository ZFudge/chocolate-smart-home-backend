include $(shell pwd)/.env

TRASH_PATH := /tmp/null
NETWORK_NAME := csm-network

APP_CONTAINER_NAME := csm-backend
APP_IMAGE := csm-backend
CSM_IMAGE_NAME := csm-backend

MQTT_IMAGE := eclipse-mosquitto:2.0.20
MQTT_VOLUME_PATH := $(shell pwd)/mosquitto.conf:/mosquitto/config/mosquitto.conf

POSTGRES_CONTAINER_NAME := csm-postgres-db-dev
POSTGRES_VOLUME_NAME := csm-postgres-vol
POSTGRES_IMAGE := postgres:12.18-bullseye

TEST_DB_NAME := testdb
TEST_DB_PW := testpw
TEST_DB_USER := testuser


help:
	@echo "Usage: make TARGET"
	@echo ""
	@echo "Targets:"
	@echo "  help                         Print this help message"
	@echo "  network                      Create $(NETWORK_NAME) network"
	@echo "  cleannetwork                 Remove $(NETWORK_NAME) network"
	@echo "  mqtt                         Run mqtt container"
	@echo "  cleanmqtt                    Remove mqtt container from docker network and delete container"
	@echo "  build                        Build the app image"
	@echo "  run                          Run the app with app database and testing database"
	@echo "  clean                        Stop the app"
	@echo "  test                         Run tests in $(APP_CONTAINER_NAME) container using pipenv and pytest"
	@echo "  broadcast                    Broadcast request for all device states"
	@echo "  attach                       Attach session to $(APP_CONTAINER_NAME) output"
	@echo "  shell                        Open shell in $(APP_CONTAINER_NAME) container"
	@echo ""


.PHONY: build
build:
	@docker-compose build

network:
	@docker network create -d bridge $(NETWORK_NAME) \
		2> ${TRASH_PATH} || true

cleannetwork: cleanmqtt
	@docker network rm $(NETWORK_NAME) \
		2> ${TRASH_PATH}

mqtt: network
	@docker run -it -d \
		--name=mqtt \
		--network=$(NETWORK_NAME) \
		-p 1883:1883 \
		-p 9001:9001 \
		-v $(MQTT_VOLUME_PATH) \
		$(MQTT_IMAGE)


mqttlogs:
	@docker exec -it mqtt /bin/sh -c 'tail -50 -f /mosquitto/log/mosquitto.log'

cleanmqtt:
	@docker stop mqtt 2> ${TRASH_PATH} || true
	@docker rm mqtt 2> ${TRASH_PATH} || true

up:
	@docker-compose up -d

_testuser:
	@echo "Creating test user if one does not exist. Errors about user already existing are expected."
	@docker exec -it $(POSTGRES_CONTAINER_NAME) /bin/bash -c \
		"psql -c \"CREATE USER testuser WITH ENCRYPTED PASSWORD 'testpw';\" csm" || true

testdb: _testuser
	@echo "Creating test database if one does not exist. Errors about database already existing are expected."
	@docker exec -it $(POSTGRES_CONTAINER_NAME) /bin/bash -c \
		"psql -c 'CREATE DATABASE testdb OWNER testuser;' csm" || true

run: up testdb

clean:
	@docker-compose down

rmdbvolume:
	@docker volume rm $(POSTGRES_VOLUME_NAME)

attach:
	@docker-compose logs --follow $(APP_CONTAINER_NAME)

shell:
	@docker-compose exec -it $(APP_CONTAINER_NAME) sh

test: testdb
	@docker exec -it $(APP_CONTAINER_NAME) sh -c 'pipenv run pytest -vv'

testing: test

broadcast:
	@curl --head http://localhost:8000/device/broadcast_request_devices_state/

virtual_clients:
	@docker stop vcs 2> ${TRASH_PATH} || true
	@docker rm vcs 2> ${TRASH_PATH} || true
	@docker run -it \
		--network=$(NETWORK_NAME) \
		--name=vcs \
		csm-backend:latest \
		sh -c "pipenv run uvicorn src.virtual_client:virtual_clients --port=8001"
