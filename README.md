# Markdown Pad

A simple browser-based .md viewer/editor with live preview. Save, load, browse, and delete markdown files.

### One-command install (once GHCR image is built)

```bash
docker run -d -p 5004:5004 -v $(pwd)/notes-data:/data ghcr.io/thegrandseraph/markdown-pad
```

Or with Docker Compose — create `docker-compose.yml`:

```yaml
services:
  markdown-pad:
    image: ghcr.io/thegrandseraph/markdown-pad
    ports:
      - "5004:5004"
    volumes:
      - ./notes-data:/data
    environment:
      - NOTES_DIR=/data
    restart: unless-stopped
```

Then:

```bash
docker compose up -d
```

### Local dev (clone + build)

```bash
git clone https://github.com/thegrandseraph/markdown-pad.git
cd markdown-pad
pip install -r requirements.txt
python app.py
# → http://localhost:5004
```

### Build locally with Docker

```bash
docker build -t markdown-pad .
docker run -d -p 5004:5004 -v $(pwd)/notes-data:/data markdown-pad
```
