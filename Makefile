
PACKAGE_NAME = webwhatsapi
PACKAGE_COVERAGE = webwhatsapi

help:
	@echo "Options"
	@echo "-----------------------------------------------------------------------"
	@echo "help:                     This help"
	@echo "requirements:             Download requirements"
	@echo "requirements-test:        Download requirements for tests"
	@echo "requirements-docs:        Download requirements for docs"
	@echo "run-tests:                Run tests with coverage"
	@echo "publish:                  Publish new version on Pypi"
	@echo "clean:                    Clean compiled files"
	@echo "flake:                    Run Flake8"
	@echo "prepush:                  Helper to run before to push to repo"
	@echo "pull-request:             Helper to run before to merge a pull request"
	@echo "autopep:                  Reformat code using PEP8"
	@echo "-----------------------------------------------------------------------"

requirements:
	@echo "Installing ${PACKAGE_NAME} requirements..."
	pip install -r requirements.txt

requirements-test: requirements
	@echo "Installing ${PACKAGE_NAME} tests requirements..."
	pip install -r requirements-test.txt

requirements-docs: requirements
	@echo "Installing ${PACKAGE_NAME} docs requirements..."
	pip install -r requirements-docs.txt

run-tests:
	@echo "Running tests..."
	nosetests --with-coverage -d --cover-package=${PACKAGE_COVERAGE} --cover-erase

publish:
	@echo "Publishing new version on Pypi..."
	python setup.py bdist_wheel upload

clean:
	@echo "Cleaning compiled files..."
	find . | grep -E "(__pycache__|\.pyc|\.pyo)$ " | xargs rm -rf
	@echo "Cleaning distribution files..."
	rm -rf dist
	@echo "Cleaning build files..."
	rm -rf build
	@echo "Cleaning egg info files..."
	rm -rf ${PACKAGE_NAME}.egg-info
	@echo "Cleaning coverage files..."
	rm -f .coverage

build:
	python3 setup.py bdist_wheel

flake:
	@echo "Running flake8 tests..."
	flake8 ${PACKAGE_COVERAGE}
	flake8 tests

autopep:
	autopep8 --max-line-length 120 -r -j 8 -i .

prepush: flake run-tests

pull-request: flake run-tests