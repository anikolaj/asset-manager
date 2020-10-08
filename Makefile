clean:
	find ./asset_manager -name '*.pyc' -exec rm --force {} \;
	find ./tests -name '*.pyc' -exec rm --force {} \;

init:
	pip install -r requirements.txt

test:
	nosetests -v tests/**.py

run:
	python3 -m asset_manager test