# Quickstart

## Local (development)

1. Create `.env` from example and edit values:
```bash
cp .env.example .env
```

2. Create venv and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the app:
```bash
FLASK_APP=app flask run --host 0.0.0.0 --port ${PORT:-5000}
```

4. Open the app:
- Photobooth: http://localhost:5000/
- Gallery: http://localhost:5000/gallery
- Settings (admin): http://localhost:5000/settings

## Docker (production-like)

Use the provided deploy script which builds images, generates a self-signed TLS certificate, and starts the stack:
```bash
chmod +x deploy.sh
./deploy.sh
```
Then visit: https://localhost/

See [Deployment (Docker)](./deployment_docker.md) for details.
