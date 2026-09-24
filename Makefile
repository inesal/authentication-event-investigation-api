up:
	docker compose up -d --build

down:
	docker compose down

seed:
	docker compose exec api python scripts/seed.py --csv data/local/events.csv --truncate

test:
	pytest -q
