include $(PWD)/.env

TRASH_PATH := /tmp/null
APP_IMAGE := chocolate-smart-home-backend
APP_CONTAINER_NAME := csm-fastapi-server
CSM_IMAGE_NAME := chocolate-smart-home-backend
MQTT_IMAGE := eclipse-mosquitto:2.0.15
MQTT_VOLUME_PATH := $(PWD)/mosquitto.conf:/mosquitto/config/mosquitto.conf
NETWORK_NAME := chocolate-smart-home-network
POSTGRES_IMAGE := postgres:12.18-bullseye
POSTGRES_VOLUME_NAME := chocolate-smart-home-postgres-vol
POSTGRES_CONTAINER_NAME := csm-postgres-db
TEST_DB_NAME := testdb
TEST_DB_USER := testuser
TEST_DB_PW := testpw


help:
	@echo "Usage: make TARGET"
	@echo ""
	@echo "Targets:"
	@echo "  help                         Print this help message"
	@echo "  build                        Build the app image"
	@echo "  run                          Run the app with app database and testing database"
	@echo "  clean                        Stop the app"
	@echo "  test                         Run tests in $(APP_CONTAINER_NAME) container using pipenv and pytest"
	@echo "  mqtt                         Run mqtt container"
	@echo "  network                      Create $(NETWORK_NAME) network"
	@echo "  attach                       Attach session to $(APP_CONTAINER_NAME) output"
	@echo "  cleanmqtt                    Remove mqtt container from docker network and delete container"
	@echo "  cleannetwork                 Remove $(NETWORK_NAME) network"
	@echo ""

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
		-p 1883:1883 -p 9001:9001 \
		-v $(MQTT_VOLUME_PATH) \
		$(MQTT_IMAGE)

cleanmqtt:
	@docker stop mqtt 2> ${TRASH_PATH} || true
	@docker rm mqtt 2> ${TRASH_PATH} || true

up:
	@docker-compose up -d

createtestdb:
	@docker exec -it $(POSTGRES_CONTAINER_NAME) /bin/bash -c \
		"psql -c 'CREATE DATABASE testdb OWNER testuser;' chocolatesmarthome"

createtestuser:
	@docker exec -it $(POSTGRES_CONTAINER_NAME) /bin/bash -c \
		"psql -c \"CREATE USER testuser WITH ENCRYPTED PASSWORD 'testpw';\" chocolatesmarthome"

run: up createtestuser createtestdb

clean:
	@docker-compose down

attach:
	@docker-compose logs --follow $(APP_CONTAINER_NAME)

test:
	@docker exec -it $(APP_CONTAINER_NAME) sh -c 'pipenv run pytest'

testing: test
