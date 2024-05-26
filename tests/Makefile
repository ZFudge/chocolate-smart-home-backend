TEST_POSTGRES_CONTAINER_NAME := TEST-csm-postgres-db
TEST_APP_CONTAINER_NAME := TEST-csm-app

testdbnew:
	@echo "Starting test postgres database container..."
	@docker run -d \
		--name ${TEST_POSTGRES_CONTAINER_NAME} \
		-p 15432:5432 \
		-e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		-e POSTGRES_USER=$(POSTGRES_USER) \
		-e POSTGRES_DB=$(POSTGRES_DB) \
			${POSTGRES_IMAGE} \
				2> ${TRASH_PATH} || true

testdb: testdbnew
	@echo "Starting test postgres database container..."
	@docker start ${TEST_POSTGRES_CONTAINER_NAME} \
		2> ${TRASH_PATH} || true

cleantestdb:
	@echo "Stopping test postgres database container..."
	@docker stop ${TEST_POSTGRES_CONTAINER_NAME} \
		2> ${TRASH_PATH} || true
	@echo "Removing test postgres database container..."
	@docker rm ${TEST_POSTGRES_CONTAINER_NAME} \
		2> ${TRASH_PATH} || true

testcontainercreate:
	@echo "Creating new ${TEST_APP_CONTAINER_NAME} container if none exists..."
	@docker create --name ${TEST_APP_CONTAINER_NAME} -p 9000:8000 ${APP_IMAGE}

testcontainer: testcontainercreate
	@echo "Starting test container..."
	@docker start ${TEST_APP_CONTAINER_NAME} \
		2> ${TRASH_PATH} || true

cleantestcontainer:
	@echo "Stopping test postgres database container..."
	@docker stop ${TEST_APP_CONTAINER_NAME} \
		2> ${TRASH_PATH} || true
	@echo "Removing test postgres database container..."
	@docker rm ${TEST_APP_CONTAINER_NAME} \
		# 2> ${TRASH_PATH} || true

testssetup: testdb testcontainer

test: testssetup
	@echo "Running test with pytest..."
	@docker exec ${TEST_APP_CONTAINER_NAME} -c 'pytest'

teststeardown: cleantestdb cleantestcontainer
