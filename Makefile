include $(shell pwd)/.env

TRASH_PATH := /tmp/null
NETWORK_NAME := csm-network

APP_CONTAINER_NAME := csm-backend
APP_IMAGE := csm-backend
CSM_IMAGE_NAME := csm-backend

MQTT_IMAGE := eclipse-mosquitto:2.0.20
MQTT_VOLUME_PATH := $(shell pwd)/mosquitto.conf:/mosquitto/config/mosquitto.conf

POSTGRES_CONTAINER_NAME := csm-postgres-db-dev
POSTGRES_VOLUME_NAME := csm-postgres-vol-0
POSTGRES_IMAGE := postgres:12.18-bullseye

TEST_DB_NAME := testdb
TEST_DB_PW := testpw
TEST_DB_USER := testuser


help:
	@echo "Usage: make TARGET"
	@echo ""
	@echo "Targets:"
	@echo "  help                         Print this help message"
	@echo "  build                        Build the app image"
	@echo "  dev                          Run the app in development mode"
	@echo "  devclean                     Stop the app in development mode"
	@echo "  devlogs                      Follow the logs of the app in development mode"
	@echo "  test                         Run tests in $(APP_CONTAINER_NAME) container using pipenv and pytest"
	@echo "  broadcast                    Broadcast request for all device states"
	@echo "  shell                        Open shell in $(APP_CONTAINER_NAME) container"
	@echo "  virtual_clients              Run virtual clients"
	@echo ""


.PHONY: build
build:
	@docker compose -f docker-compose-dev.yml build

mqttlogs:
	@docker compose -f docker-compose-dev.yml logs -f csm-mqtt-dev

_testuser:
	@echo "Creating test user if one does not exist. Errors about user already existing are expected."
	@docker exec -it $(POSTGRES_CONTAINER_NAME) /bin/bash -c \
		"psql -c \"CREATE USER testuser WITH ENCRYPTED PASSWORD 'testpw';\" csm" || true

testdb: _testuser
	@echo "Creating test database if one does not exist. Errors about database already existing are expected."
	@docker exec -it $(POSTGRES_CONTAINER_NAME) /bin/bash -c \
		"psql -c 'CREATE DATABASE testdb OWNER testuser;' csm" || true

devclean:
	@docker compose -f docker-compose-dev.yml down

devlogs:
	@docker compose -f docker-compose-dev.yml logs -f

dev: devclean
	@docker compose -f docker-compose-dev.yml up -d
	@make testdb
	@make devlogs

rmdbvolume:
	@docker volume rm $(POSTGRES_VOLUME_NAME)

shell:
	@docker compose -f docker-compose-dev.yml exec csm-backend-dev ash -l || \
	docker run -it --rm -v $(shell pwd):/backend \
      -v $(shell pwd)/csm.sh:/etc/profile.d/csm.sh \
      -w /backend csm-backend:latest ash -l

test: testdb
	@docker compose -f docker-compose-dev.yml exec csm-backend-dev sh -c 'pipenv run pytest -vv'

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
