clean:
	find . -name \*.pyc -delete

test: clean
	python setup.py test

publish:
	git tag $$(python setup.py --version)
	git push && git push --tags
	python setup.py sdist upload

.PHONY: publish clean test
