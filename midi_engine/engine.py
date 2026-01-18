"""Single-threaded engine loop (runs in its own thread for integration with TUI)."""

from typing import Callable
import threading
from .midi_io import MidiIO, MidiEvent


class Engine:
    def __init__(
        self, midi_io: MidiIO, event_callback: Callable[[MidiEvent], None] | None = None
    ):
        self.midi_io = midi_io
        self.event_callback = event_callback
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _run(self):
        # Blocking, deterministic processing: wait for events using blocking read
        while self._running:
            events = self.midi_io.read_events(non_blocking=False)
            for e in events:
                # placeholder for future processing
                if self.event_callback:
                    try:
                        self.event_callback(e)
                    except Exception:
                        pass
                # pass-through
                try:
                    self.midi_io.send_event(e)
                except Exception:
                    pass
