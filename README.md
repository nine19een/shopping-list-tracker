# Shopping List Tracker

Lightweight Tkinter desktop app that keeps track of household purchases. Items move through **Candidate → To Buy → Purchased** columns via drag-and-drop, while checkboxes are reserved for delete and live selection totals.

## Features
- Add items with custom names and prices
- Three-column workflow with drag-and-drop transitions
- Per-column totals plus live “selected” counts/costs
- Persistent storage (`shopping_tracker_data.json` in your home directory)
- Optional PyInstaller build for a single-file executable (`统计清单.exe`)

## Getting Started
1. Install Python 3.11+ (Tkinter included on Windows/macOS).
2. Clone the repo and run:
    ```bash
    python list.py
    ```

Add items in the Candidate column, drag them between columns, and use checkboxes only for delete/selection stats.

Build an EXE (optional)
```bash
python -m PyInstaller --noconsole --onefile --name "统计清单" list.py
```

The executable appears under dist/统计清单.exe. It still reads/writes ~/shopping_tracker_data.json.

Notes
Do not commit shopping_tracker_data.json, dist/, build/, or __pycache__/.
To share binaries, upload the generated .exe to a GitHub Release instead of committing it.