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
	@uvicorn chocolate_smart_home.main:app --reload

test: shell
	@pytest
