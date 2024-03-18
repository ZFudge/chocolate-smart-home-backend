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

run: shell
	@pipenv run uvicorn chocolate_smart_home.main:app --reload

testdbsetup:
	@docker run --name ${TEST_DB_NAME} -d \
		-p 15432:5432 \
		-e POSTGRES_PASSWORD=testpassword \
		-e POSTGRES_USER=testuser \
		-e POSTGRES_DB=testdb \
		postgres \
		|| true

testteardowndb:
	@docker stop ${TEST_DB_NAME} || true
	@docker rm   ${TEST_DB_NAME} || true

testrun:
	@pytest

test: shell testdbsetup testrun testteardowndb
