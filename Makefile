clean:
	find ./asset_manager -name '*.pyc' -exec rm --force {} \;
	find ./tests -name '*.pyc' -exec rm --force {} \;

init:
	uv sync

test:
	uv run pytest -v tests

run:
	uv run python -m asset_manager $(PORTFOLIO)
