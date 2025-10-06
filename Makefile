DOCKER_COMPOSE = docker compose
SERVICE_WEB = web
SERVICE_DB = db
SERVICE_NGINX = nginx

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

restart: down up

logs:
	$(DOCKER_COMPOSE) logs -f

migrate:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_WEB) python manage.py migrate

superuser:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_WEB) python manage.py createsuperuser

collectstatic:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_WEB) python manage.py collectstatic --noinput

shell:
	$(DOCKER_COMPOSE) exec $(SERVICE_WEB) bash
