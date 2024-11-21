PYTHONPATH := .

RUN = PYTHONPATH=$(PYTHONPATH) poetry run
TEST = $(RUN) pytest $(arg)
POETRY_RUN = poetry run

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install dependencies
	poetry install --no-interaction --no-ansi --no-root --all-extras

.PHONY: lint
lint: ## Run linters in format mode
	$(POETRY_RUN) black ./src ./src/tests
	$(POETRY_RUN) ruff check ./src ./src/tests
	$(POETRY_RUN) pytest --dead-fixtures --dup-fixtures

.PHONY: test
test: ## Runs pytest with coverage
	$(TEST) src/tests/ --cov=src --cov-report json --cov-report term --cov-report xml:cobertura.xml
