include $(shell pwd)/.env

TRASH_PATH := /tmp/null
NETWORK_NAME := csm-network

APP_IMAGE := csm-backend
CSM_IMAGE_NAME := csm-backend

POSTGRES_CONTAINER_NAME := csm-postgres-db-dev

.PHONY: help
help:
	@echo "Usage: make TARGET"
	@echo ""
	@echo "Targets:"
	@echo "  help                         Print this help message"
	@echo "  build                        Build the app image"
	@echo "  dev                          Run the app in development mode"
	@echo "  devclean                     Stop the app in development mode"
	@echo "  devlogs                      Follow the logs of the app in development mode"
	@echo "  clean                        Stop the app and remove all containers and volumes"
	@echo "  black                        Format the code using black"
	@echo "  test                         Run ruff, black, and pytest, using pipenv"
	@echo "  broadcast                    Broadcast request for all device states"
	@echo "  shell                        Open shell in container"
	@echo "  mqttlogs                     Follow the logs of the MQTT broker"
	@echo "  testdb                       Create test database if one does not exist"
	@echo ""


.PHONY: build
build:
	@docker compose -f docker-compose-dev.yml build

.PHONY: mqttlogs
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

.PHONY: devclean
devclean:
	@docker compose -f docker-compose-dev.yml down

.PHONY: devlogs
devlogs:
	@docker compose -f docker-compose-dev.yml logs -f

.PHONY: dev
dev: devclean
	@docker compose -f docker-compose-dev.yml up -d
	@make testdb
	@make devlogs

.PHONY: clean
clean: devclean

.PHONY: shell
shell:
	@docker compose -f docker-compose-dev.yml exec csm-backend-dev ash -l || \
	docker run -it --rm -v $(shell pwd):/backend \
      -v $(shell pwd)/csm.sh:/etc/profile.d/csm.sh \
      -w /backend csm-backend:latest ash -l

.PHONY: test
test: testdb
	@docker compose -f docker-compose-dev.yml exec csm-backend-dev ash -l -c \
	'ruff check /backend && black --check /backend && pytest -vv' || \
	docker run -it --rm -v $(shell pwd):/backend \
      -v $(shell pwd)/csm.sh:/etc/profile.d/csm.sh \
      -w /backend csm-backend:latest ash -l -c \
	'ruff check /backend && black --check /backend && pytest -vv'

.PHONY: coverage
coverage: testdb
	@docker compose -f docker-compose-dev.yml exec csm-backend-dev ash -l -c \
	'pytest --cov=src --cov-report=term-missing tests/' || \
	docker run -it --rm -v $(shell pwd):/backend \
      -v $(shell pwd)/csm.sh:/etc/profile.d/csm.sh \
      -w /backend csm-backend:latest ash -l -c \
	'pytest --cov=src --cov-report=term-missing tests/'

.PHONY: black
black:
	@docker compose -f docker-compose-dev.yml exec csm-backend-dev ash -l -c \
	'black /backend' || \
	docker run -it --rm -v $(shell pwd):/backend \
      -v $(shell pwd)/csm.sh:/etc/profile.d/csm.sh \
      -w /backend csm-backend:latest ash -l -c \
	'black /backend'

.PHONY: broadcast
broadcast:
	@curl --head http://localhost:8000/device/broadcast_request_devices_state/
