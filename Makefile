.PHONY: format lint test clean install

# Install dependencies
install:
	pip install -r requirements.txt

# Format code with black and isort
format:
	black host_aggregator.py test_aggregator.py
	isort host_aggregator.py test_aggregator.py

# Run linting tools
lint:
	flake8 host_aggregator.py test_aggregator.py

# Run tests
test:
	python test_aggregator.py

# Run the main script
run:
	python host_aggregator.py

# Clean up generated files
clean:
	rm -f *.csv
	rm -rf data/*.csv

# Format and lint in one command
check: format lint

# Install pre-commit hooks
install-hooks:
	pip install pre-commit
	pre-commit install
