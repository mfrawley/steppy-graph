test:
	python -m pytest -vv

mypy:
	mypy .

dist: clean
	python setup.py sdist bdist_wheel

test_pub:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pub:
	twine upload dist/*

clean:
	rm -rf build/*
	rm -rf dist/*


.PHONY: test dist
