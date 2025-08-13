#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
CERT_DIR="$APP_DIR/docker/certs"
ENV_FILE="$APP_DIR/.env"

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
info() { printf '\033[34m[i]\033[0m %s\n' "$*"; }
success() { printf '\033[32m[✓]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[!]\033[0m %s\n' "$*"; }
err() { printf '\033[31m[✗]\033[0m %s\n' "$*"; }

bold "Virtual Photobooth – Docker Deploy"

# Helper: detect primary local IP address
detect_ip() {
	# Try Linux first
	if command -v hostname >/dev/null 2>&1; then
		IP=$(hostname -I 2>/dev/null | awk '{print $1}')
		if [[ -n "${IP:-}" ]]; then echo "$IP"; return 0; fi
	fi
	if command -v ip >/dev/null 2>&1; then
		IP=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '/src/ {for(i=1;i<=NF;i++) if ($i=="src") print $(i+1)}' | head -n1)
		if [[ -n "${IP:-}" ]]; then echo "$IP"; return 0; fi
	fi
	# macOS: detect default interface and query it
	if command -v route >/dev/null 2>&1 && command -v awk >/dev/null 2>&1; then
		IFACE=$(route -n get default 2>/dev/null | awk '/interface:/{print $2; exit}')
		if [[ -n "${IFACE:-}" ]] && command -v ipconfig >/dev/null 2>&1; then
			IP=$(ipconfig getifaddr "$IFACE" 2>/dev/null || true)
			if [[ -n "${IP:-}" ]]; then echo "$IP"; return 0; fi
		fi
	fi
	# Fallbacks for common interfaces
	for i in en0 en1 eth0; do
		if command -v ipconfig >/dev/null 2>&1; then
			IP=$(ipconfig getifaddr "$i" 2>/dev/null || true)
			[[ -n "${IP:-}" ]] && { echo "$IP"; return 0; }
		fi
		done
	# Last resort
	echo "127.0.0.1"
}

# 0) Update repository first (pull latest), but stop if deploy.sh itself changed
if command -v git >/dev/null 2>&1 && git -C "$APP_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
	info "Checking for repository updates..."
	BRANCH=$(git -C "$APP_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
	if git -C "$APP_DIR" remote get-url origin >/dev/null 2>&1; then
		git -C "$APP_DIR" fetch --tags --prune origin "$BRANCH" >/dev/null 2>&1 || true
		# Detect if there are incoming changes
		if ! git -C "$APP_DIR" diff --quiet HEAD..origin/"$BRANCH" --; then
			CHANGED_FILES=$(git -C "$APP_DIR" diff --name-only HEAD..origin/"$BRANCH" || true)
			if echo "$CHANGED_FILES" | grep -q "^deploy.sh$"; then
				warn "deploy.sh has updates in origin/$BRANCH."
				err "For safety, please run a manual 'git pull' to update the deploy script, then re-run ./deploy.sh."
				exit 1
			fi
			info "Pulling latest changes from origin/$BRANCH..."
			git -C "$APP_DIR" pull --rebase --autostash origin "$BRANCH"
			success "Repository updated"
		else
			info "Repository is up to date"
		fi
	else
		warn "No 'origin' remote found. Skipping git update."
	fi
else
	warn "Not a git repository or git not installed. Skipping repo update."
fi

# 1) Ensure required tools and pick docker compose command
if ! command -v docker >/dev/null 2>&1; then
	err "docker is required but not found. Please install Docker."
	exit 1
fi
if ! command -v openssl >/dev/null 2>&1; then
	err "openssl is required but not found."
	exit 1
fi

DC=""
if docker compose version >/dev/null 2>&1; then
	DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
	DC="docker-compose"
else
	err "Neither 'docker compose' nor 'docker-compose' found. Please install Docker Compose."
	exit 1
fi
success "Using compose command: $DC"

# Helpers for editing .env safely (macOS/BSD compatible)
set_env_var() {
	# Usage: set_env_var KEY VALUE FILE
	local key="$1"; shift
	local value="$1"; shift
	local file="$1"
	if grep -qE "^${key}=" "$file"; then
		# Replace existing line
		tmpfile="${file}.tmp.$$"
		sed "s|^${key}=.*$|${key}=${value}|" "$file" > "$tmpfile" && mv "$tmpfile" "$file"
	else
		echo "${key}=${value}" >> "$file"
	fi
}

# 2) Ensure .env exists or offer to replace
SKIP_ADMIN_PROMPT=0
if [[ -f "$ENV_FILE" ]]; then
	info ".env already exists."
	read -r -p "Do you want to use the existing .env? [Y/n]: " USE_EXISTING
	USE_EXISTING=${USE_EXISTING:-Y}
	if [[ "$USE_EXISTING" =~ ^[Nn]$ ]]; then
		TS=$(date +%Y%m%d_%H%M%S)
		mv "$ENV_FILE" "$ENV_FILE.bak.$TS"
		warn "Backed up existing .env to .env.bak.$TS"
		if [[ -f "$APP_DIR/.env.example" ]]; then
			cp "$APP_DIR/.env.example" "$ENV_FILE"
			info "Created new .env from .env.example"
		else
			touch "$ENV_FILE"
			info "Created new empty .env"
		fi
	else
		info "Keeping existing .env"
		SKIP_ADMIN_PROMPT=1
	fi
else
	if [[ -f "$APP_DIR/.env.example" ]]; then
		cp "$APP_DIR/.env.example" "$ENV_FILE"
		warn ".env was missing. Created from .env.example."
	else
		touch "$ENV_FILE"
		warn ".env was missing. Created an empty .env."
	fi
fi

# 2b) Offer to set ADMIN_PASSWORD only when creating/replacing .env
if [[ "$SKIP_ADMIN_PROMPT" -eq 0 ]]; then
	read -r -p "Do you want to set ADMIN_PASSWORD now? [Y/n]: " SET_ADMIN
	SET_ADMIN=${SET_ADMIN:-Y}
	if [[ "$SET_ADMIN" =~ ^[Nn]$ ]]; then
		info "Using default ADMIN_PASSWORD=admin123"
		set_env_var ADMIN_PASSWORD admin123 "$ENV_FILE"
	else
		while true; do
			read -r -s -p "Enter ADMIN_PASSWORD: " APW; echo
			read -r -s -p "Confirm ADMIN_PASSWORD: " APW2; echo
			if [[ "$APW" == "$APW2" && -n "$APW" ]]; then
				set_env_var ADMIN_PASSWORD "$APW" "$ENV_FILE"
				success "ADMIN_PASSWORD set in .env"
				break
			else
				warn "Passwords did not match or were empty. Please try again."
			fi
		done
	fi
else
	info "Using ADMIN_PASSWORD from existing .env"
fi

# 3) Generate self-signed certificate if absent
mkdir -p "$CERT_DIR"
CRT="$CERT_DIR/server.crt"
KEY="$CERT_DIR/server.key"
if [[ ! -f "$CRT" || ! -f "$KEY" ]]; then
	DOMAIN=${DOMAIN:-localhost}
	info "Generating self-signed TLS cert for $DOMAIN (valid 825 days)"
	openssl req -x509 -nodes -days 825 -newkey rsa:2048 \
		-keyout "$KEY" -out "$CRT" \
		-subj "/C=US/ST=NA/L=Local/O=VirtualPhotobooth/OU=Dev/CN=$DOMAIN" \
		-addext "subjectAltName=DNS:$DOMAIN,IP:127.0.0.1" >/dev/null 2>&1
	success "Self-signed cert generated: docker/certs/server.crt, server.key"
else
	info "Using existing TLS certificate in docker/certs/"
fi

# 4) Build and start containers
info "Building containers..."
$DC build --no-cache
success "Build complete"

info "Starting stack..."
$DC up -d
success "Services started"

# 5) Preload common Piper models (list repo and download) using Hugging Face client inside Docker
info "Preloading common Piper models (if missing)..."
MODEL_DIR="$APP_DIR/piper/models"
mkdir -p "$MODEL_DIR"
docker run --rm -e HF_HUB_DISABLE_TELEMETRY=1 -v "$MODEL_DIR":/models python:3.11-slim bash -lc "pip install --no-cache-dir --upgrade pip >/dev/null 2>&1 && pip install --no-cache-dir huggingface_hub >/dev/null 2>&1 && python - <<'PY'
import os, gzip, shutil
from huggingface_hub import list_repo_files, hf_hub_download

REPO = 'rhasspy/piper-voices'
LANG_DIRS = ['en', 'de', 'es', 'it', 'zh', 'ja', 'ko', 'ru']

def pick_files():
    files = list_repo_files(REPO)
    # consider both .onnx and .onnx.gz
    onnx = [f for f in files if '/' in f and (f.endswith('.onnx') or f.endswith('.onnx.gz'))]
    picks = []
    for lang in LANG_DIRS:
        lang_files = [f for f in onnx if f.startswith(lang + '/')]
        lang_files.sort(key=lambda x: (0 if ('-low.onnx' in x or '-low.onnx.gz' in x) else 1, x))
        for f in lang_files[:2]:
            picks.append(f)
    # de-dupe preserve order
    seen = set(); out = []
    for f in picks:
        if f not in seen:
            seen.add(f); out.append(f)
    return out

def ensure_download(rel, target):
    path = hf_hub_download(REPO, filename=rel)
    base = os.path.basename(path)
    dest = os.path.join(target, base)
    if not os.path.exists(dest):
        with open(path, 'rb') as src, open(dest, 'wb') as dst:
            dst.write(src.read())
    if dest.endswith('.gz'):
        out_path = dest[:-3]
        if not os.path.exists(out_path):
            with gzip.open(dest, 'rb') as f_in, open(out_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    # config json
    try:
        cfg_path = hf_hub_download(REPO, filename=rel + '.json')
        cfg_dest = os.path.join(target, os.path.basename(cfg_path))
        if not os.path.exists(cfg_dest):
            with open(cfg_path, 'rb') as src, open(cfg_dest, 'wb') as dst:
                dst.write(src.read())
    except Exception:
        pass

def main():
    target = '/models'
    os.makedirs(target, exist_ok=True)
    files = pick_files()
    downloaded = 0
    for rel in files:
        try:
            before = set(os.listdir(target))
            ensure_download(rel, target)
            after = set(os.listdir(target))
            if after - before:
                downloaded += 1
                print('Downloaded', rel)
        except Exception as e:
            print('Failed', rel, e)
    print(f'Preload complete, {downloaded} file(s) downloaded to {target}')

if __name__ == '__main__':
    main()
PY"

# 5) Post-deploy info
WEB_CONTAINER=$($DC ps -q web || true)
NGINX_CONTAINER=$($DC ps -q nginx || true)

HOST_IP=${HOST_IP:-$(detect_ip)}
bold "Deployment summary"
cat <<SUMMARY
- Web container: ${WEB_CONTAINER:-(not found)}
- Nginx container: ${NGINX_CONTAINER:-(not found)}
- HTTPS URL: https://$HOST_IP/
- HTTP redirects to HTTPS
- Static frames dir (mounted): ./static/frames
- Photos dir (mounted): ./photos
- Settings stored in: ./config/settings.json
- Admin Settings page: https://$HOST_IP/settings
  • Password set via ADMIN_PASSWORD in .env
- SMS via SMSGate: configure in Settings (docs: https://sms-gate.app/)
- Email via SMTP: configure in Settings

Troubleshooting:
- View live logs: $DC logs -f
- Restart: $DC restart
- Stop: $DC down
- Rebuild after changes: $DC build --no-cache && $DC up -d
- If browser warns about self-signed cert, proceed to advanced/continue for local dev.
SUMMARY

success "Deployment complete. Open https://localhost in your browser."
