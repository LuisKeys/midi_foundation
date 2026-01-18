"""Main entry: wire config, MIDI I/O, engine, and TUI together."""

from pathlib import Path
import queue
import signal
import sys

from .config import load_config, save_config, Config
from .midi_io import MidiIO
from .engine import Engine

try:
    from .tui_textual import run_tui

    _USE_TEXTUAL = True
except Exception:
    from .tui import TUI  # type: ignore

    _USE_TEXTUAL = False


def main():
    cfg = load_config()
    midi = MidiIO()

    # open configured ports if present
    if cfg.midi.inputs:
        midi.open_inputs(cfg.midi.inputs)
    if cfg.midi.outputs:
        midi.open_outputs(cfg.midi.outputs)

    event_q = queue.Queue()

    def on_event(e):
        try:
            event_q.put_nowait(e)
        except Exception:
            pass

    engine = Engine(midi, event_callback=on_event)

    def _shutdown(sig, frame):
        engine.stop()
        midi.close()
        save_config(cfg)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    engine.start()
    try:
        if _USE_TEXTUAL:
            # textual app blocks and handles its own lifecycle
            run_tui(event_q, midi, cfg, save_callback=save_config)
        else:
            tui = TUI(event_q, midi, cfg, save_callback=save_config)
            tui.run()
    finally:
        engine.stop()
        midi.close()
        save_config(cfg)


if __name__ == "__main__":
    main()
