init:
	pip install -r requirements.txt

format:
	ruff format .
	docformatter --in-place --recursive src tests scripts

test:
	py.test tests

.PHONY: init test
