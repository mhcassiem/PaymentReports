# Variables
DOCKER_COMPOSE = docker-compose
PYTHON = poetry run python

# Targets
.PHONY: help build up down test

help: ## Show this help menu
	@echo "Usage:"
	@echo "  make <target>"
	@echo
	@echo "Targets:"
	@sed -n 's/^##//p' $(MAKEFILE_LIST)

build: ## Build the Docker images
	$(DOCKER_COMPOSE) build

up: ## Start the application containers
	$(DOCKER_COMPOSE) up app

clean: ## Stop and remove the containers
	$(DOCKER_COMPOSE) down

test: ## Run tests for the application
	$(DOCKER_COMPOSE) up tests
	$(DOCKER_COMPOSE) down tests
