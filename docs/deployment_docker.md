# Deployment (Docker)

This project includes a production-like Docker stack with Nginx (TLS termination) and Gunicorn.

## Files
- `docker/Dockerfile.web` – Flask app image (Gunicorn on port 8000)
- `docker/Dockerfile.nginx` – Nginx reverse proxy (ports 80/443)
- `docker/nginx.conf` – Proxy and TLS config (serves `/static/` directly)
- `docker-compose.yml` – Orchestration of both services
- `deploy.sh` – Builds images, generates self-signed certs, and starts the stack

## Usage
```bash
chmod +x deploy.sh
./deploy.sh
```
Then open `https://localhost/` and accept the self-signed certificate.

## Volumes
- `./photos` → `/app/photos`
- `./config` → `/app/config`
- `./static/frames` → `/app/static/frames`
- `./docker/certs` → `/etc/nginx/ssl`

## Environment
The `web` service reads configuration from `.env`.

## Managing the stack
- Logs: `docker compose logs -f`
- Restart: `docker compose restart`
- Stop: `docker compose down`
- Rebuild after code changes: `docker compose build --no-cache && docker compose up -d`
