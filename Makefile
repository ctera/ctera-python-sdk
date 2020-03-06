# *** WARNING: Targets are meant to run in a build container - Use skipper make ***

all: pylint flake8 doc8

flake8:
	flake8 cterasdk

pylint:
	mkdir -p build/
	PYLINTHOME=reports/ pylint -r n cterasdk

doc8:
	doc8 docs/source

test:
	# Run the unittests and create a junit-xml report
	mkdir -p build/
	nose2 --config=tests/ut/nose2.cfg --verbose --project-directory .

coverage: test
	# Create a coverage report and validate the given threshold
	coverage html --fail-under=60 -d build/coverage

nose2:
	mkdir -p build/


	# Run the example nose2 tests - validate the package works
	DTT_COMPOSE_PATH=$(DTT_COMPOSE_PATH) \
	nose2 --config=tests/integration/nose2.cfg --verbose --project-directory .

pytest:
	mkdir -p build/

	# Run the example pytest tests - validate the package works
	DTT_COMPOSE_PATH=$(DTT_COMPOSE_PATH) \
	pytest -v tests/integration/

prepare-dist:
	# Create the source distribution
	python3 setup.py sdist bdist_wheel

upload-test:
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

clean:
	# Clean any generated files
	rm -rf build dist .coverage .cache