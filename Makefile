test:
	python -m pytest -vv

mypy:
	mypy .

gen_dist:
	python setup.py sdist bdist_wheel

.PHONY: test
