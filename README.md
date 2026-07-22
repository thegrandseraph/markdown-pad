# Markdown Pad

A simple browser-based **.md viewer/editor** with live preview. Type markdown on the left, see the rendered HTML on the right in real time. Save, load, browse, and delete files — all from your browser.

---

## Quick Start

### Docker (any platform)

```bash
docker run -d -p 5004:5004 -v $(pwd)/notes-data:/data ghcr.io/thegrandseraph/markdown-pad
```

Then open **http://localhost:5004**.

The image is multi-arch (amd64 + arm64) — Docker pulls the right variant for your machine automatically.

### Docker Compose

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

```bash
docker compose up -d
```

### Local dev (no Docker)

```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5004
```

### Build the Docker image yourself

```bash
git clone https://github.com/thegrandseraph/markdown-pad.git
cd markdown-pad
docker build -t markdown-pad .
docker run -d -p 5004:5004 --name markdown-pad -v $(pwd)/notes-data:/data markdown-pad
```

---

## Features

| Feature | How |
|---------|-----|
| **Live preview** | Type in the editor — the preview updates on every keystroke |
| **Save files** | Click Save. New files get a prompt for the filename. Existing files save in-place. |
| **Load files** | Click Load to open a file picker. Browse, open, or delete saved .md files. |
| **New file** | Clears the editor for a fresh document. |
| **Toggle panes** | Hide the editor or preview to go full-width on one side. |
| **Mobile responsive** | Panes stack vertically on phones. Toolbar wraps to fit small screens. |

---

## How it works

- **Backend:** A single Python file (`app.py`) using FastAPI + uvicorn
- **Markdown rendering:** [marked.js](https://marked.js.org/) loaded from CDN — all processing happens in your browser
- **File storage:** Markdown files are saved as `.md` files in a `notes-data/` directory (or `/data` inside the container)
- **No database needed:** Each file is a plain `.md` file — portable, readable, directly accessible on disk

---

## API endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the web app |
| `/files` | GET | Lists saved filenames |
| `/save` | POST | Saves content to `notes/<name>.md` |
| `/load/{name}` | GET | Loads content of a file |
| `/delete/{name}` | POST | Deletes a file |

---

## Files

All saved markdown files live in `notes-data/` (or whatever directory you mount to `/data`). Each file is `.md` plain text — openable in any text editor, version-controllable, portable.

---

## Tech stack

- **Python 3.12+** / **FastAPI** / **uvicorn**
- **marked.js** (CDN) for markdown rendering
- **Docker** (multi-arch: amd64 + arm64)
- Built and published via **GitHub Actions** to **GHCR**

---

## Development

```bash
git clone https://github.com/thegrandseraph/markdown-pad.git
cd markdown-pad
pip install -r requirements.txt
python app.py
```

Edit `app.py` to change the UI, add features, or modify the API. The HTML/CSS/JS are all inline — no separate template files, no build step.

---

## License

Do whatever you want with it.
