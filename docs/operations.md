# Operations

Common operational tasks:

## Backups
- Photos: backup `./photos/`
- Settings: backup `./config/settings.json`
- Frames: backup `./static/frames/`

## Updates
- Pull latest code, then: `docker compose build --no-cache && docker compose up -d`

## Logs
- `docker compose logs -f`

## Health checks
- Open `/` to confirm photobooth page loads
- Open `/settings` and `/gallery`

## Common issues
- Permissions on mounted volumes (ensure container user can read/write)
- Browser permissions for camera access
- Self-signed certificate browser warning (expected in local deployments)
