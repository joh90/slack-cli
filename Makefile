.PHONY: install dev test build clean lint format

install:
	uv sync

dev:
	uv pip install -e .

test:
	uv run pytest

test-cov:
	uv run pytest --cov=slack_cli --cov-report=html

build:
	uv run pyinstaller --onefile \
		--name slack \
		--hidden-import slack_sdk \
		--hidden-import click \
		--hidden-import rich \
		slack_cli/__main__.py

clean:
	rm -rf build/ dist/ *.spec __pycache__ .pytest_cache htmlcov/ .coverage

lint:
	uv run ruff check slack_cli/

format:
	uv run ruff format slack_cli/
