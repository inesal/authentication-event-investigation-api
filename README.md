# Authentication Event Investigation API

A small FastAPI and PostgreSQL service for exploring authentication events. It
supports time and identity filters, suspicious-activity summaries, and cursor
pagination for deep event searches.

This is a learning and portfolio project. It is not a production security
monitoring system and does not make automated threat verdicts.

## What it demonstrates

- Async REST API design with FastAPI and SQLAlchemy
- Parameterized PostgreSQL queries and indexed event searches
- Docker Compose development setup
- API tests with Pytest
- Basic load checks with k6
- Offset and keyset pagination for event queries

## Architecture

The API exposes endpoints under `/api/v1`. PostgreSQL stores normalized event
fields plus the original input row as JSONB. The CSV importer maps an
authentication log export into the database schema.

## Run locally

1. Copy the example configuration and change the local password:

   ```sh
   cp .env.example .env
   ```

2. Start the API and database:

   ```sh
   docker compose up --build
   ```

3. Open the interactive API docs at `http://localhost:8000/docs`.
## Load a dataset

No dataset is included in this repository. The original prototype was tested
with an RBA-style authentication log export. Before using any dataset, check its
license and terms, and make sure it contains no real credentials or identifying
personal or infrastructure data.

Place an authorized CSV at `data/local/events.csv` (that folder is ignored by
Git), then run:

```sh
docker compose exec api python scripts/seed.py --csv data/local/events.csv
```

The importer expects columns including `Login Timestamp`, `User ID`,
`IP Address`, `Country` or `ASN`, `Browser Name and Version`, and
`Login Successful`. The `--truncate` option clears the database table first;
use it only with disposable local data.

## API

- `GET /api/v1/health` — application and database status
- `GET /api/v1/stats` — event count and time range
- `GET /api/v1/events` — filtered event search; supports offset or cursor paging
- `GET /api/v1/suspicious/top-users` — users with failed login events
- `GET /api/v1/suspicious/top-hosts` — most frequent hosts
- `GET /api/v1/suspicious/user-timeline` — event counts by time bucket
- `GET /api/v1/aggregate/user-to-host` — user and host event counts

For cursor pagination, pass both `cursor_ts` and `cursor_id` from the last
row of the previous page. The API rejects requests that provide only one.
## Tests and load check

Run the API tests locally:

```sh
python -m pip install -r requirements.txt
python -m pytest -q
```

With the Compose stack running, run a short k6 smoke test:

```sh
k6 run k6/smoke.js
```

The smoke test checks endpoint availability. Its results depend on the local
machine and dataset; they are not production performance claims.

## Configuration and safety

- Copy `.env.example` to `.env`; the real `.env` is ignored by Git.
- Example credentials are for local development only. Use managed secrets and
  a deployment-specific configuration outside this demo.
- Bind the development service to localhost; do not expose it to the Internet.
- Do not commit datasets, database exports, logs, credentials, or real
  authentication records.

## Contributors

Developed by [@inesal](https://github.com/inesal) with contributions from
[@noob216](https://github.com/noob216).

No license is included in this preparation copy. Agree on the project license
with all contributors before public release.