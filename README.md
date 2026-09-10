# Tennis Backend

FastAPI backend for the lawn-tennis application. The frontend owns tennis
scoring and serving. It sends the current match state and events to this
service, which validates the request, applies authentication and authorization,
and persists the result.

The backend does not calculate points, games, sets, tiebreaks, or match
winners. Serving metadata is checked for structural validity and stored with
the match and completed sets.

## Technology

- Python
- FastAPI and Uvicorn
- SQLAlchemy 2
- Pydantic
- Alembic
- MySQL through PyMySQL
- JWT authentication with `python-jose`
- `python-dotenv` for environment configuration

## Project layout

```text
app/
├── api/v1/          HTTP routes for auth, users, players, officials,
│                    tournaments, teams, matches, and the dashboard
├── core/            Application configuration
├── db/              SQLAlchemy base and database session
├── exceptions/      Application exceptions and handlers
├── middleware/      JWT authentication and role authorization
├── models/          SQLAlchemy persistence models
├── repositories/    Database access operations
├── schemas/         Pydantic request and response models
├── seeds/           Startup seed data
├── services/        Application and persistence workflows
└── utils/            Shared utilities and logging
alembic/             Database migrations
alembic.ini          Alembic configuration
requirements.txt     Python dependencies
```

The match domain stores player metadata, score fields, completed sets,
serving-state JSON, and `MatchEvent` records. The team module provides team
creation, listing, detail, update, soft delete, and restore operations.

## Configuration

Create a virtual environment, install the pinned dependencies, and configure a
`.env` file in the backend directory:

```text
APP_NAME=Tennis Backend
APP_VERSION=1.0.0
DB_URL=<SQLAlchemy database URL>
SECRET_KEY=<long random signing key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENV=development
ALLOWED_ORIGINS=http://localhost:8081,http://localhost:3000
```

`DB_URL` and `SECRET_KEY` are required at startup. In production, the secret
must not be a known placeholder, must be at least 32 characters, and
`ALLOWED_ORIGINS` must be set.

## Install and run

From `BE-Tennis`:

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Apply the database migrations:

```bash
alembic upgrade head
```

Start the development server:

```bash
python -m uvicorn app.main:app --reload
```

The API is served under `/api/v1`. In development, FastAPI exposes Swagger UI
at `/docs`, ReDoc at `/redoc`, and the OpenAPI document at `/openapi.json`.

## Authentication and authorization

Register and login are available at:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

Protected routes use a bearer JWT. The token contains the authenticated user
identity and role. Route dependencies distinguish authentication from role
authorization. Administrative operations require the roles declared by each
route; match finalization permits `Admin` and `Scorer`, while match creation,
updates, deletion, and restore are administrative operations. `Supervisor` is
handled by the authorization middleware as a full-access role.

## Match API

Match management endpoints are:

- `POST /api/v1/matches`
- `GET /api/v1/matches`
- `GET /api/v1/matches/{match_id}`
- `PUT /api/v1/matches/{match_id}`
- `DELETE /api/v1/matches/{match_id}`
- `POST /api/v1/matches/{match_id}/restore`
- `GET /api/v1/matches/{match_id}/scoreboard`
- `GET /api/v1/matches/{match_id}/events`
- `POST /api/v1/matches/{match_id}/finalize`

The frontend finalizes a completed match with a `final_state` and a non-empty
ordered `events` array. The final state contains the current points, games,
sets, tiebreak values, winner, completed-set metadata, and serving state. Each
event contains its number, event type, player, optional individual server,
elapsed seconds, and optional recording timestamp.

Finalization validates the request structure and lifecycle, locks the match,
and saves the match state, completed sets, and events in one database
transaction. Repeating finalization for an already completed match is rejected.

The scoreboard endpoint returns the persisted match state, completed sets, and
display point values. It does not replay a tennis scoring engine.

## Team API

Team management endpoints are:

- `POST /api/v1/teams`
- `GET /api/v1/teams`
- `GET /api/v1/teams/{team_id}`
- `PUT /api/v1/teams/{team_id}`
- `DELETE /api/v1/teams/{team_id}`
- `POST /api/v1/teams/{team_id}/restore`

## Other API modules

The versioned API also exposes route modules for:

- users and roles (`base_routes.py`)
- players (`player_routes.py`)
- officials (`official_routes.py`)
- tournaments (`tournament_routes.py`)
- teams (`team_routes.py`)
- dashboard summary (`dashboard_routes.py`)

Each module's request and response contract is defined in `app/schemas`.

## Database migrations

Alembic tracks the schema from the initial tables through player metadata,
match metadata, doubles support, match events, teams, and serving-state
metadata. Use the existing migration configuration for upgrades and
downgrades:

```bash
alembic current
alembic history
alembic upgrade head
alembic downgrade -1
```

Do not edit production data as part of a schema upgrade. Review a migration and
the target database revision before applying it.
