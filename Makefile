# *** WARNING: Targets are meant to run in a build container - Use skipper make ***

all: pylint flake8

flake8:
	flake8 cterasdk

pylint:
	mkdir -p build/
	PYLINTHOME=reports/ pylint -r n cterasdk

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

dist/ctera-sdk-*.tar.gz:
	# Create the source distribution
	python setup.py sdist

clean:
	# Clean any generated files
	rm -rf build dist .coverage .cache