# PayFlow

## Database Migrations

To apply the latest database migrations against the dockerized database, run:
```bash
docker compose exec app python -m app.db.migrate
```
