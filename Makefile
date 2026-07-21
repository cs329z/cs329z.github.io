server = server.py

preview:
	uv run python $(server)

build:
	uv run python $(server) build

.PHONY: preview build
