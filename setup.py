import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="steppygraph",
    version="0.1.0",
    author="Mark Frawley",
    author_email="markfrawley+pypi@gmail.com",
    description="A Python DSL for AWS Step Functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mfrawley/steppy-graph",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
