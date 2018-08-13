test:
	python -m pytest

mypy:
	mypy .

gen_dist:
	python setup.py sdist bdist_wheel

.PHONY: test
