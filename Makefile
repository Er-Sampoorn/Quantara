.PHONY: dev test seed build reset clean docker-up docker-down

dev:
	@echo "Starting Quantara local environment..."
	@bash scripts/dev.sh

test:
	@echo "Running full test suite..."
	@pytest -v

seed:
	@echo "Seeding demo market data and strategies..."
	@python -m database.seeds.seed_data

docker-up:
	@docker-compose up -d --build

docker-down:
	@docker-compose down

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .pytest_cache .coverage
