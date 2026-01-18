# MIDI Engine Foundation (Python)

This repository contains a foundational, portable MIDI engine implemented in Python with a terminal UI. The Python implementation is designed to be portable to C++ (VST/CLAP) later.

Quick start
-----------

1. Create and activate the `midi` conda environment (Python 3.11+):

```bash
conda create -n midi python=3.11 -y
conda activate midi
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Run the engine (Textual TUI recommended):

```bash
python -m midi_engine.main
# or, in VS Code, choose the "Python: Run midi_engine.main (midi env)" launch configuration
```

What you'll find
-----------------

- `midi_engine/midi_io.py` — MIDI I/O wrapper using `mido` + `python-rtmidi`.
- `midi_engine/engine.py` — single-threaded, deterministic processing loop.
- `midi_engine/config.py` — YAML load/save for `config.yaml` (persists inputs/outputs).
- `midi_engine/tui_textual.py` — Textual-based interactive TUI (modal port selector, live event list).
- `midi_engine/tui.py` — legacy/simple stdin+rich-based TUI (fallback).
- `midi_engine/main.py` — wiring and graceful shutdown. It prefers the Textual TUI when available and falls back to the legacy TUI.

Usage notes
-----------

- Launch the app and press `p` to open the port selector modal (Textual UI). Use `q` to quit.
- The port selector allows selecting multiple inputs/outputs and saving the selection to `midi_engine/config.yaml`.
- Incoming MIDI events are shown live in the event list and are forwarded unchanged to selected outputs (pass-through).

Developer notes
---------------

- No global state: resources are owned by objects (`MidiIO`, `Engine`).
- Design ready for future harmony logic and C++ porting: clear separation of I/O, processing, and UI.
- For richer terminal UX we use `textual`; fallback UI remains in `tui.py`.

Try it locally
--------------

```bash
conda activate midi
python -m midi_engine.main
```

If you want, I can add quick unit tests for `config.py`, or add a small script to simulate MIDI input for development.
