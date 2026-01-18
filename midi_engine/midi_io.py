"""MIDI I/O abstraction using mido + python-rtmidi.

Design goals:
- enumerate inputs/outputs
- open multiple inputs/outputs
- provide non-blocking read and blocking read for engine
- unified MidiEvent dataclass
"""

from dataclasses import dataclass
from typing import List, Optional
import time
import mido
from mido import ports


@dataclass
class MidiEvent:
    timestamp: float
    message: mido.Message
    port_name: Optional[str] = None


class MidiIO:
    def __init__(self):
        self.input_ports: List[mido.ports.BaseInput] = []
        self.output_ports: List[mido.ports.BaseOutput] = []
        self.multi_in: Optional[ports.MultiPort] = None

    def list_inputs(self) -> List[str]:
        return mido.get_input_names()

    def list_outputs(self) -> List[str]:
        return mido.get_output_names()

    def open_inputs(self, names: List[str]):
        self.close_inputs()
        ports_list = []
        for n in names:
            ports_list.append(mido.open_input(n))
        self.input_ports = ports_list
        if ports_list:
            self.multi_in = ports.MultiPort(ports_list)
        else:
            self.multi_in = None

    def open_outputs(self, names: List[str]):
        self.close_outputs()
        outs = []
        for n in names:
            outs.append(mido.open_output(n))
        self.output_ports = outs

    def close_inputs(self):
        for p in self.input_ports:
            try:
                p.close()
            except Exception:
                pass
        self.input_ports = []
        self.multi_in = None

    def close_outputs(self):
        for o in self.output_ports:
            try:
                o.close()
            except Exception:
                pass
        self.output_ports = []

    def read_events(self, non_blocking: bool = True) -> List[MidiEvent]:
        """Return list of MidiEvent. Default non-blocking; for engine pass non_blocking=False to block until at least one event."""
        events: List[MidiEvent] = []
        if not self.input_ports:
            return events
        if non_blocking:
            # iterate each port for pending messages
            for p in self.input_ports:
                for msg in p.iter_pending():
                    events.append(
                        MidiEvent(
                            timestamp=time.time(),
                            message=msg,
                            port_name=getattr(p, "name", None),
                        )
                    )
            return events
        else:
            # blocking: use MultiPort.receive() to wait for at least one message
            if self.multi_in is None:
                return events
            msg = self.multi_in.receive()
            if msg is not None:
                events.append(MidiEvent(timestamp=time.time(), message=msg))
            # collect any other pending messages immediately after
            for p in self.input_ports:
                for msg in p.iter_pending():
                    events.append(
                        MidiEvent(
                            timestamp=time.time(),
                            message=msg,
                            port_name=getattr(p, "name", None),
                        )
                    )
            return events

    def send_event(self, event: MidiEvent):
        for o in self.output_ports:
            try:
                o.send(event.message)
            except Exception:
                pass

    def close(self):
        self.close_inputs()
        self.close_outputs()
