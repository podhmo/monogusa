test:
	pytest -vv --show-capture=all

ci:
	pytest --show-capture=all --cov=monogusa --no-cov-on-fail --cov-report term-missing
	$(MAKE) lint typing

format:
#	pip install -e .[dev]
	black monogusa setup.py

# https://www.flake8rules.com/rules/W503.html
# https://www.flake8rules.com/rules/W504.html
# https://www.flake8rules.com/rules/E203.html
# https://www.flake8rules.com/rules/E501.html
lint:
#	pip install -e .[dev]
	flake8 monogusa --ignore W503,W504,E203,E501

typing:
#	pip install -e .[dev]
	mypy --strict --strict-equality --ignore-missing-imports monogusa
mypy: typing

build:
#	pip install wheel
	python setup.py bdist_wheel

upload:
#	pip install twine
	twine check dist/monogusa-$(shell cat VERSION)*
	twine upload dist/monogusa-$(shell cat VERSION)*

.PHONY: test ci format lint typing mypy build upload
