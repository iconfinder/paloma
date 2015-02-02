PY_SRC := paloma tests setup.py

all:

check:
	@flake8 $(PY_SRC)

publish:
	@python setup.py sdist upload

.PHONY: check publish
