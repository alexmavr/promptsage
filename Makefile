.PHONY: test test-env

test: 
	poetry run python3 -m pytest tests

test-env:
	docker-compose -f docker-compose.dev.yml up -d 
	# TODO: test if the server is up and running