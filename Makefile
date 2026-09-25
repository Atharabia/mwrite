.PHONY: up down migrate migration

up:
	docker compose up -d --build

down:
	docker compose down

clean:
	docker compose down -v

migrate:
	docker compose exec app alembic upgrade head

migration:
	docker compose exec app alembic revision --autogenerate -m "$(name)"
