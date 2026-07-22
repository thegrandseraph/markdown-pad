# App #5: Markdown Pad
#
# A simple .md viewer/editor. Save, load, browse, and delete
# markdown files on the server.
#
# NEW CONCEPTS: Server-side file I/O, file listing, modal/picker UI
#
# Run: python app.py
# Then open http://localhost:5004

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI()

# All markdown files live in a notes/ directory next to this script
NOTES_DIR = os.environ.get("NOTES_DIR") or os.path.join(os.path.dirname(__file__), "notes")
os.makedirs(NOTES_DIR, exist_ok=True)


def list_notes():
    """Return a sorted list of .md filenames (without extension)."""
    files = []
    for f in os.listdir(NOTES_DIR):
        if f.endswith(".md"):
            files.append(f[:-3])  # strip .md
    return sorted(files)


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Markdown Pad</title>

        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }

            body {
                font-family: system-ui, sans-serif;
                background: #1a1a2e;
                color: #e0e0e0;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }

            /* ---------- Toolbar ---------- */
            .toolbar {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: #16213e;
                border-bottom: 1px solid #2a2a3e;
            }
            .toolbar button {
                padding: 0.4rem 1rem;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 0.9rem;
            }
            .toolbar .spacer { flex: 1; }
            .btn-save { background: #2d6a4f; color: white; }
            .btn-load { background: #415a77; color: white; }
            .btn-new  { background: #9b2226; color: white; }
            .btn-toggle {
                background: transparent;
                color: #888;
                font-size: 0.8rem;
                border: 1px solid #415a77 !important;
            }
            .btn-toggle:hover {
                background: #415a77;
                color: white;
            }
            .toolbar .info {
                font-size: 0.8rem;
                color: #666;
            }
            .toolbar .filename {
                font-size: 0.85rem;
                color: #aaa;
                margin: 0 0.5rem;
            }

            /* ---------- Panes ---------- */
            .panes {
                display: grid;
                grid-template-columns: 1fr 1fr;
                flex: 1;
                overflow: hidden;
            }
            .panes.single { grid-template-columns: 1fr; }

            .pane {
                display: flex;
                flex-direction: column;
                min-width: 0;
                overflow: hidden;
            }
            .pane.hidden { display: none; }

            .pane-header {
                display: flex;
                align-items: center;
                padding: 0.3rem 0.5rem;
                background: #16213e;
                border-bottom: 1px solid #2a2a3e;
                font-size: 0.8rem;
                color: #888;
                user-select: none;
            }

            .pane-body {
                flex: 1;
                overflow: hidden;
                display: flex;
            }

            #editor {
                flex: 1;
                padding: 1rem;
                border: none;
                background: #0f172a;
                color: #e0e0e0;
                font-family: 'Courier New', monospace;
                font-size: 1rem;
                line-height: 1.6;
                resize: none;
                outline: none;
            }

            #preview-content {
                flex: 1;
                padding: 1rem;
                overflow-y: auto;
                line-height: 1.7;
            }

            #preview-content h1, #preview-content h2, #preview-content h3 { margin: 1rem 0 0.5rem; }
            #preview-content h1 { font-size: 1.8rem; border-bottom: 1px solid #333; padding-bottom: 0.3rem; }
            #preview-content h2 { font-size: 1.4rem; }
            #preview-content p { margin: 0.5rem 0; }
            #preview-content code {
                background: #2a2a3e;
                padding: 0.2rem 0.4rem;
                border-radius: 3px;
                font-size: 0.9rem;
            }
            #preview-content pre {
                background: #0f172a;
                padding: 1rem;
                border-radius: 6px;
                overflow-x: auto;
                margin: 0.5rem 0;
            }
            #preview-content pre code { background: none; padding: 0; }
            #preview-content ul, #preview-content ol { padding-left: 1.5rem; margin: 0.5rem 0; }
            #preview-content blockquote {
                border-left: 3px solid #415a77;
                padding-left: 1rem;
                color: #999;
                margin: 0.5rem 0;
            }
            #preview-content img { max-width: 100%; border-radius: 4px; }
            #preview-content a { color: #4ea8de; }

            /* ---------- Modal overlay ---------- */
            .modal-overlay {
                display: none;
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.6);
                align-items: center;
                justify-content: center;
                z-index: 100;
            }
            .modal-overlay.open {
                display: flex;
            }
            .modal-box {
                background: #1a1a2e;
                border: 1px solid #415a77;
                border-radius: 10px;
                padding: 1.5rem;
                min-width: 320px;
                max-height: 70vh;
                display: flex;
                flex-direction: column;
            }
            .modal-box h2 {
                font-size: 1.2rem;
                margin-bottom: 1rem;
                color: #e0e0e0;
            }
            .modal-box .file-list {
                overflow-y: auto;
                flex: 1;
            }
            .modal-box .file-item {
                display: flex;
                align-items: center;
                padding: 0.6rem 0.8rem;
                border-radius: 6px;
                cursor: pointer;
                transition: background 0.15s;
            }
            .modal-box .file-item:hover {
                background: #16213e;
            }
            .modal-box .file-item .name {
                flex: 1;
            }
            .modal-box .file-item .delete-btn {
                background: none;
                border: none;
                color: #9b2226;
                cursor: pointer;
                font-size: 1rem;
                padding: 0 0.3rem;
                visibility: hidden;
            }
            .modal-box .file-item:hover .delete-btn {
                visibility: visible;
            }
            .modal-box .file-item .delete-btn:hover {
                color: #e63946;
            }
            .modal-box .empty-msg {
                color: #666;
                font-style: italic;
                text-align: center;
                padding: 2rem;
            }
            .modal-close {
                align-self: flex-end;
                background: none;
                border: none;
                color: #888;
                cursor: pointer;
                font-size: 0.9rem;
                padding: 0.3rem 0.8rem;
                margin-top: 0.8rem;
                border-radius: 5px;
            }
            .modal-close:hover {
                background: #2a2a3e;
                color: #e0e0e0;
            }
        </style>
    </head>
    <body>
        <div class="toolbar">
            <button class="btn-new" onclick="newFile()">New</button>
            <button class="btn-save" onclick="saveFile()">Save</button>
            <button class="btn-load" onclick="loadPicker()">Load</button>
            <span class="filename" id="filenameDisplay">(untitled)</span>
            <span class="spacer"></span>
            <button class="btn-toggle" id="toggleEditor" onclick="togglePane('editor')">◀ Hide Editor</button>
            <button class="btn-toggle" id="togglePreview" onclick="togglePane('preview')">Hide Preview ▶</button>
            <span class="info" id="status">Ready</span>
        </div>

        <div class="panes" id="panes">
            <div class="pane" id="editorPane">
                <div class="pane-header">Editor</div>
                <div class="pane-body">
                    <textarea id="editor" placeholder="Type some markdown..."></textarea>
                </div>
            </div>
            <div class="pane" id="previewPane">
                <div class="pane-header">Preview</div>
                <div class="pane-body">
                    <div id="preview-content">Your rendered markdown will appear here.</div>
                </div>
            </div>
        </div>

        <!-- Modal overlay for the Load picker -->
        <div class="modal-overlay" id="loadModal">
            <div class="modal-box">
                <h2>Saved Files</h2>
                <div class="file-list" id="fileList">
                    <div class="empty-msg">Loading...</div>
                </div>
                <button class="modal-close" onclick="closeModal()">Close</button>
            </div>
        </div>

        <script>
            const editor = document.getElementById('editor');
            const previewContent = document.getElementById('preview-content');
            const status = document.getElementById('status');
            const filenameDisplay = document.getElementById('filenameDisplay');
            const panes = document.getElementById('panes');
            const loadModal = document.getElementById('loadModal');
            const fileList = document.getElementById('fileList');

            let editorHidden = false;
            let previewHidden = false;
            let currentFile = null;  // currently open filename, null = untitled

            // --- Live Preview ---
            editor.addEventListener('input', () => {
                previewContent.innerHTML = marked.parse(editor.value);
            });

            // --- New File ---
            function newFile() {
                if (editor.value.trim() && !confirm('Discard current draft?')) return;
                editor.value = '';
                previewContent.innerHTML = 'Your rendered markdown will appear here.';
                currentFile = null;
                filenameDisplay.textContent = '(untitled)';
                status.textContent = 'New file';
                setTimeout(() => { status.textContent = 'Ready'; }, 1500);
            }

            // --- Save ---
            async function saveFile() {
                let name = currentFile;
                if (!name) {
                    name = prompt('Filename (without .md):');
                    if (!name || !name.trim()) return;
                    name = name.trim();
                }

                const res = await fetch('/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name, content: editor.value })
                });
                const data = await res.json();
                if (data.ok) {
                    currentFile = name;
                    filenameDisplay.textContent = name + '.md';
                    status.textContent = 'Saved ✓';
                } else {
                    status.textContent = 'Error: ' + (data.error || 'save failed');
                }
                setTimeout(() => { status.textContent = 'Ready'; }, 2000);
            }

            // --- Load picker (open modal, fetch file list) ---
            async function loadPicker() {
                const res = await fetch('/files');
                const data = await res.json();
                const files = data.files || [];

                if (files.length === 0) {
                    fileList.innerHTML = '<div class="empty-msg">No saved files yet.</div>';
                } else {
                    let html = '';
                    for (const name of files) {
                        const isActive = name === currentFile;
                        html += `
                            <div class="file-item" onclick="loadFile('${name}')">
                                <span class="name">${name}.md ${isActive ? '(current)' : ''}</span>
                                <button class="delete-btn" onclick="event.stopPropagation(); deleteFile('${name}')">✕</button>
                            </div>
                        `;
                    }
                    fileList.innerHTML = html;
                }
                loadModal.classList.add('open');
            }

            function closeModal() {
                loadModal.classList.remove('open');
            }

            // --- Load a specific file ---
            async function loadFile(name) {
                const res = await fetch('/load/' + encodeURIComponent(name));
                const data = await res.json();
                if (data.ok) {
                    editor.value = data.content;
                    previewContent.innerHTML = marked.parse(data.content);
                    currentFile = name;
                    filenameDisplay.textContent = name + '.md';
                    status.textContent = 'Loaded ✓';
                    closeModal();
                } else {
                    status.textContent = 'Error: ' + (data.error || 'load failed');
                }
                setTimeout(() => { status.textContent = 'Ready'; }, 2000);
            }

            // --- Delete a file ---
            async function deleteFile(name) {
                if (!confirm('Delete "' + name + '.md"?')) return;
                const res = await fetch('/delete/' + encodeURIComponent(name), { method: 'POST' });
                const data = await res.json();
                if (data.ok) {
                    if (currentFile === name) {
                        currentFile = null;
                        filenameDisplay.textContent = '(untitled)';
                    }
                    // Refresh the picker list
                    await loadPicker();
                    status.textContent = 'Deleted ✓';
                } else {
                    status.textContent = 'Error deleting';
                }
                setTimeout(() => { status.textContent = 'Ready'; }, 2000);
            }

            // --- Toggle pane collapse ---
            function togglePane(side) {
                const editorPane = document.getElementById('editorPane');
                const previewPane = document.getElementById('previewPane');

                if (side === 'editor') {
                    editorHidden = !editorHidden;
                    editorPane.classList.toggle('hidden', editorHidden);
                    document.getElementById('toggleEditor').textContent = editorHidden ? '▶ Show Editor' : '◀ Hide Editor';
                } else {
                    previewHidden = !previewHidden;
                    previewPane.classList.toggle('hidden', previewHidden);
                    document.getElementById('togglePreview').textContent = previewHidden ? 'Show Preview ▶' : 'Hide Preview ▶';
                }
                panes.classList.toggle('single', editorHidden || previewHidden);
            }

            // Close modal when clicking the overlay background
            loadModal.addEventListener('click', (e) => {
                if (e.target === loadModal) closeModal();
            });

            // Start with a demo
            editor.value = `# Welcome to Markdown Pad

## Try it out

Type on the **left**, see the result on the **right**.

- **Bold** and *italic*
- \`inline code\`
- Lists and blockquotes

> This is a blockquote.

\`\`\`python
print("Code blocks work too!")
\`\`\`

[Links](https://example.com) and images work as well.
`;
            previewContent.innerHTML = marked.parse(editor.value);
        </script>
    </body>
    </html>
    """)


@app.get("/files")
def get_files():
    """Return a list of saved markdown filenames."""
    return {"files": list_notes()}


@app.post("/save")
async def save_file(request: Request):
    """Save markdown content to notes/<name>.md. Returns error if name is invalid."""
    body = await request.json()
    name = body.get("name", "").strip()
    content = body.get("content", "")

    if not name:
        return {"ok": False, "error": "Filename is required"}

    # Prevent directory traversal — only allow alphanumeric, dashes, underscores
    safe_name = "".join(c for c in name if c.isalnum() or c in "-_.")
    if safe_name != name:
        return {"ok": False, "error": "Invalid characters in filename. Use letters, numbers, dashes, and underscores only."}

    filepath = os.path.join(NOTES_DIR, name + ".md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return {"ok": True}


@app.get("/load/{name}")
def load_file(name: str):
    """Load the content of notes/<name>.md."""
    filepath = os.path.join(NOTES_DIR, name + ".md")
    if not os.path.exists(filepath):
        return {"ok": False, "error": "File not found"}
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return {"ok": True, "content": content}


@app.post("/delete/{name}")
def delete_file(name: str):
    """Delete notes/<name>.md."""
    filepath = os.path.join(NOTES_DIR, name + ".md")
    if os.path.exists(filepath):
        os.remove(filepath)
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5004)
