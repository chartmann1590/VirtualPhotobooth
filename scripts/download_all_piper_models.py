#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

FALLBACK_URLS = [
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json",
    "https://raw.githubusercontent.com/rhasspy/piper-voices/main/voices.json",
]


def fetch_json(url: str):
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "./piper/models"
    os.makedirs(target_dir, exist_ok=True)

    data = None
    last_err = None
    for url in FALLBACK_URLS:
        try:
            data = fetch_json(url)
            break
        except Exception as e:
            last_err = e
    if data is None:
        print(f"Failed to fetch voices.json: {last_err}", file=sys.stderr)
        sys.exit(1)

    # voices.json structure: { lang: { voice: { quality: { files: { 'onnx': url } } } } }
    count = 0
    for lang, voices in data.items():
        if not isinstance(voices, dict):
            continue
        for voice, variants in voices.items():
            if not isinstance(variants, dict):
                continue
            for quality, meta in variants.items():
                files = meta.get("files") or {}
                onnx = files.get("onnx")
                if not onnx:
                    continue
                fname = os.path.basename(onnx)
                dest = os.path.join(target_dir, fname)
                if os.path.exists(dest):
                    continue
                try:
                    print(f"Downloading {fname} ...")
                    urllib.request.urlretrieve(onnx, dest)
                    count += 1
                except Exception as e:
                    print(f"Failed {fname}: {e}", file=sys.stderr)
    print(f"Downloaded {count} model(s) to {target_dir}")


if __name__ == "__main__":
    main()


