export SHELL:=/bin/sh
export SHELLOPTS:=$(if $(SHELLOPTS),$(SHELLOPTS):)pipefail:errexit

.ONESHELL:

dev:
	echo "Starting development environment..."
	docker-compose up --no-deps backend

test-backend:
	echo "Running tests..."
	rm -f ./backend/test.db
	docker build -f backend/Dockerfile.test -t reflect_test .
	docker run --rm -e TEST=true -e isAdmin=false -e production=false -v $(PWD)/backend:/backend reflect_test
# for windows, use PowerShell:
# Remove-Item .\backend\test.db -ErrorAction Ignore
# docker build -f backend/Dockerfile.test -t reflect_test .
# docker run --rm -e TEST=true -e isAdmin=false -e production=false -v ${PWD}\backend:/backend reflect_test