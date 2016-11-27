
test:
	python -m unittest discover -s gecvw

clean:
	find . -name "*~" -type f -delete
	find . -name "*.pyc" -type f -delete
	find . -name "__pycache__" -delete

.PHONY: clean test
