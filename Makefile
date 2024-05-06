TEST_DB_NAME := test-postgres-db

help:
	@echo "Usage: make TARGET"
	@echo ""
	@echo "Targets:"
	@echo "  help                         Print this help message"
	@echo "  shell                        Enable pipenv shell"
	@echo "  run                          Run the app"
	@echo "  test                         Run tests with pytest"
	@echo ""

shell:
	@pipenv shell || true

logs:
	@python chocolate_smart_home/prep_logs.py

run: shell logs
	@pipenv run uvicorn \
		chocolate_smart_home.main:app --reload \
		--env-file .env \
		--log-level debug \
		--log-config logs.ini

cleanmqtt:
	@echo "Removing any existing mqtt container..."
	@docker stop mqtt || true
	@docker rm   mqtt || true

runmqtt: cleanmqtt
	@echo "Starting new mqtt container..."
	@docker run -it -d \
		--name=mqtt \
		-v $(PWD)/mosquitto.conf:/mosquitto/config/mosquitto.conf \
		-p 1883:1883 \
		-p 9001:9001 \
		eclipse-mosquitto:2.0.18

testdbsetup:
	@docker run --name ${TEST_DB_NAME} -d \
		-p 15432:5432 \
		-e POSTGRES_PASSWORD=testpassword \
		-e POSTGRES_USER=testuser \
		-e POSTGRES_DB=testdb \
		postgres:12.18-bullseye \
		|| true

testteardowndb:
	@docker stop ${TEST_DB_NAME} || true
	@docker rm   ${TEST_DB_NAME} || true

testrun:
	@pytest

test: shell testteardowndb testdbsetup testrun testteardowndb
