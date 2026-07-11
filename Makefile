.PHONY: up down migrate migration

up:
	docker compose up -d

down:
	docker compose down

migrate:
	docker compose exec app alembic upgrade head

migration:
	docker compose exec app alembic revision --autogenerate -m "$(name)"
