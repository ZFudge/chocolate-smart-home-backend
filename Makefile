include $(PWD)/.env

TRASH_PATH := /tmp/null
APP_IMAGE := chocolate-smart-home-backend
BE_CONTAINER_NAME := csm-fastapi-server
CSM_IMAGE_NAME := chocolate-smart-home-backend
MQTT_IMAGE := eclipse-mosquitto:2.0.15
MQTT_VOLUME_PATH := $(PWD)/mosquitto.conf:/mosquitto/config/mosquitto.conf
NETWORK_NAME := chocolate-smart-home-network
POSTGRES_IMAGE := postgres:12.18-bullseye
POSTGRES_VOLUME_NAME := chocolate-smart-home-postgres-vol

include $(PWD)/tests/Makefile

help:
	@echo "Usage: make TARGET"
	@echo ""
	@echo "Targets:"
	@echo "  help                         Print this help message"
	@echo "  shell                        Enable pipenv shell"
	@echo "  build                        Build the app image"
	@echo "  mqtt                         Run mqtt container"
	@echo "  network                      Create ${NETWORK_NAME} network"
	@echo "  run                          Run the app"
	@echo "  attach                       Attach current session to ${BE_CONTAINER_NAME} output"
	@echo "  cleanmqtt                    Remove mqtt container from network and delete container"
	@echo "  cleannetwork                 Remove ${NETWORK_NAME} network"
	@echo "  clean                        Stop the app"
	@echo "  "
	@echo "Tests Targets:"
	@echo "  testssetup"
	@echo "      testdb                   Start test postgres container"
	@echo "      testcontainer            Start test app container"
	@echo "  teststeardown
	@echo "      cleantestcontainer       Stop and remove test app container"
	@echo "      cleantestdb              Stop and remove test postgres container"
	@echo "  test                         Run tests in ${TEST_APP_CONTAINER_NAME} container using pytest"
	@echo ""

shell:
	@pipenv shell || true

build:
	@docker-compose build

network:
	@echo "Creating ${NETWORK_NAME} network..."
	@docker network create -d bridge ${NETWORK_NAME} \
		2> ${TRASH_PATH} || true

cleannetwork: cleanmqtt
	@echo "Removing ${NETWORK_NAME} network..."
	@docker network rm ${NETWORK_NAME} \
		2> ${TRASH_PATH}

mqtt: network
	@echo "Starting new mqtt container..."
	@docker run -it -d \
		--name=mqtt \
		--network=$(NETWORK_NAME) \
		-p 1883:1883 -p 9001:9001 \
		-v $(MQTT_VOLUME_PATH) \
		$(MQTT_IMAGE)

cleanmqtt:
	@echo "Removing mqtt container..."
	@docker stop mqtt 2> ${TRASH_PATH} || true
	@docker rm mqtt 2> ${TRASH_PATH} || true

logs:
	@python chocolate_smart_home/prep_logs.py

run: shell clean logs
	@echo "Starting app containers..."
	@docker-compose up -d --remove-orphans

clean:
	@echo "Stopping app containers..."
	@docker-compose down

attach:
	@docker-compose logs --follow ${BE_CONTAINER_NAME}
