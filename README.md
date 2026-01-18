# MIDI Engine Foundation (Python)

This repository contains a foundational, portable MIDI engine implemented in Python with a minimal rich-based TUI. It is designed to be straightforward to port to C++ later.

Quick start (create conda env and install requirements):

```bash
# create conda env with modern Python
conda create -n midi python=3.11 -y
conda activate midi
pip install -r requirements.txt

# run the engine
python -m midi_engine.main
```

Files created:

- `midi_engine/midi_io.py` — MIDI I/O wrapper using `mido` + `python-rtmidi`.
- `midi_engine/engine.py` — single-threaded processing loop (runs in its own thread for integration).
- `midi_engine/config.py` — YAML load/save for `config.yaml`.
- `midi_engine/tui.py` — `rich`-based TUI with live event view and simple menus.
- `midi_engine/main.py` — wiring and graceful shutdown.

Notes:

- The TUI uses `rich.Live` and stdin prompts for configuration. It is intentionally lightweight to keep porting simple.
- The engine uses `mido.ports.MultiPort` for deterministic blocking receives.
