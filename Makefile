test: mypy
	python -m pytest -vv

mypy:
	mypy steppygraph

dist: clean test
	python setup.py sdist bdist_wheel

test_pub:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pub: dist
	twine upload dist/*

clean:
	rm -rf build/*
	rm -rf dist/*


.PHONY: test dist
