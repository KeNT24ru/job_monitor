.PHONY: help build build_venv build_deps static run shell test

port=8000
proxy=

# default target is to show help
help:
	@echo "make install  - create virtual environment and download packages"
	@echo "make run    - run webserver on port $(port)"
	@echo "              (make run PORT=8080 for custom port)"
	@echo "make shell  - django shell"

build: build_venv build_deps

build_venv:
	virtualenv --no-site-packages .env --distribute
	
build_deps:
	.env/bin/pip install -r requirements.txt --proxy=$(proxy)

static:
	./manage.py collectstatic --link --noinput

run:
	./manage.py runserver 0.0.0.0:$(port)

shell:
	./manage.py shell_plus

test:
	./manage.py test test

update_lib:
	.env/bin/pip install -U $(app)

automig:
	./manage.py schemamigration $(app) --auto
	./manage.py migrate $(app)

sync:
	./manage.py syncdb --migrate
