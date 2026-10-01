# request-body-service

Receives copies of API request bodies forwarded by deepwell-service
(`config/middlewares/request_body.py` there) and stores them in two tables:

- `request` — `env` (the sender's `MODE`: `qa`, `prod`, …), `request_id` (the
  sender's X-Request-ID, unique per `env`), `user_id`, `created_at`
- `request_body` — `request_id` (one-to-one), `body` (JSON)

## Run

```bash
uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python manage.py migrate
COLLECTOR_TOKEN=my-secret .venv/bin/python manage.py runserver 0.0.0.0:8000
```

Tests: `.venv/bin/python manage.py test`

## Environment variables

| Name              | Default                | Purpose                                       |
|-------------------|------------------------|-----------------------------------------------|
| `SECRET_KEY`      | insecure dev key       | Django secret key                             |
| `DEBUG`           | `True`                 | `true` / `false`                              |
| `ALLOWED_HOSTS`   | `localhost,127.0.0.1`  | Comma-separated host list                     |
| `COLLECTOR_TOKEN` | empty (check disabled) | Shared secret required in `X-Collector-Token` |

## Endpoint

`POST /api/requests/` with header `X-Collector-Token: <COLLECTOR_TOKEN>`

```json
{"env": "qa", "request_id": "a1b2c3d4e5f6", "user_id": 42, "created_at": "2026-10-01T10:00:00+05:00", "body": {"any": "json"}}
```

| Status | When                                              |
|--------|---------------------------------------------------|
| 201    | Stored                                            |
| 200    | `env` + `request_id` already stored — first copy kept (retry-safe) |
| 400    | Invalid JSON or fields                            |
| 401    | Missing or wrong token                            |
| 405    | Method other than POST                            |
