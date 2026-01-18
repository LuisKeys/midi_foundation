from __future__ import annotations
from typing import List
import asyncio
import queue

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Checkbox, Static, ListView, ListItem
from textual.containers import Vertical, Horizontal, Container
from textual.screen import ModalScreen


class PortSelector(ModalScreen):
    """Modal screen to pick MIDI inputs or outputs via checkboxes."""

    def __init__(self, kind: str, items: List[str], current: List[str]):
        super().__init__()
        self.kind = kind
        self.items = items
        self.current = set(current)

    def compose(self) -> ComposeResult:
        yield Static(f"Select MIDI {self.kind.capitalize()}", id="title")
        with Vertical(id="list"):
            for name in self.items:
                checked = name in self.current
                yield Checkbox(label=name, value=checked, id=name)
        with Horizontal(id="buttons"):
            yield Button("Apply", id="apply", variant="primary")
            yield Button("Save & Apply", id="save")
            yield Button("Cancel", id="cancel", variant="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore
        if event.button.id == "cancel":
            await self.app.pop_screen()
            return
        selected: List[str] = []
        for name in self.items:
            cb = self.query_one(f"#{name}", Checkbox)
            if cb.value:
                selected.append(name)
        await self.app.post_message(PortSelected(self.kind, selected, save=(event.button.id == "save")))
        await self.app.pop_screen()


class PortSelected:
    def __init__(self, kind: str, selected: List[str], save: bool = False):
        self.kind = kind
        self.selected = selected
        self.save = save


class MidiApp(App):
    """Textual application showing live MIDI events and port configuration."""

    BINDINGS = [("q", "quit", "Quit"), ("p", "ports", "Configure Ports")]

    def __init__(self, thread_queue: queue.Queue, midi_io, config, save_callback=None):
        super().__init__()
        self.thread_queue = thread_queue
        self.midi_io = midi_io
        self.config = config
        self.save_callback = save_callback
        self._poller: asyncio.Task | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container():
            yield ListView(id="events")
        yield Footer()

    async def on_mount(self) -> None:
        # Start background task to poll the thread-safe queue
        self._poller = asyncio.create_task(self._poll_thread_queue())

    async def _poll_thread_queue(self) -> None:
        while True:
            try:
                e = self.thread_queue.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.05)
                continue
            await self._push_event(e)

    async def _push_event(self, e) -> None:
        lv = self.query_one("#events", ListView)
        entry = f"{e.timestamp:.3f} {e.message.type} {getattr(e.message, 'channel', '-')}: {str(e.message)}"
        await lv.append(ListItem(Static(entry)))
        # trim
        if len(lv.children) > 300:
            await lv.remove(lv.children[0])

    async def action_ports(self) -> None:
        inputs = self.midi_io.list_inputs()
        await self.push_screen(PortSelector("inputs", inputs, list(self.config.midi.inputs)))

    async def on_message(self, message) -> None:
        if isinstance(message, PortSelected):
            kind, selected, save = message.kind, message.selected, message.save
            try:
                if kind == "inputs":
                    self.config.midi.inputs = selected
                    self.midi_io.open_inputs(selected)
                else:
                    self.config.midi.outputs = selected
                    self.midi_io.open_outputs(selected)
                if save and self.save_callback:
                    try:
                        self.save_callback(self.config)
                    except Exception:
                        pass
            except Exception:
                pass

    async def action_quit(self) -> None:
        if self._poller:
            self._poller.cancel()
        await self.shutdown()


def run_tui(thread_queue: queue.Queue, midi_io, config, save_callback=None):
    app = MidiApp(thread_queue, midi_io, config, save_callback=save_callback)
    app.run()


if __name__ == "__main__":
    import sys

    print("Run via main.py")
    sys.exit(0)
from __future__ import annotations
from typing import List
import asyncio
import queue

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Checkbox, Static, ListView, ListItem
from textual.containers import Vertical, Horizontal, Container
from textual.screen import ModalScreen


class PortSelector(ModalScreen):
    """Modal screen to pick MIDI inputs or outputs via checkboxes."""

    def __init__(self, kind: str, items: List[str], current: List[str]):
        super().__init__()
        self.kind = kind
        self.items = items
        self.current = set(current)

    def compose(self) -> ComposeResult:
        yield Static(f"Select MIDI {self.kind.capitalize()}", id="title")
        with Vertical(id="list"):
            for name in self.items:
                checked = name in self.current
                yield Checkbox(label=name, value=checked, id=name)
        with Horizontal(id="buttons"):
            yield Button("Apply", id="apply", variant="primary")
            yield Button("Save & Apply", id="save")
            yield Button("Cancel", id="cancel", variant="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore
        if event.button.id == "cancel":
            await self.app.pop_screen()
            return
        selected: List[str] = []
        for name in self.items:
            cb = self.query_one(f"#{name}", Checkbox)
            if cb.value:
                selected.append(name)
        await self.app.post_message(PortSelected(self.kind, selected, save=(event.button.id == "save")))
        await self.app.pop_screen()


class PortSelected:
    def __init__(self, kind: str, selected: List[str], save: bool = False):
        self.kind = kind
        self.selected = selected
        self.save = save


class MidiApp(App):
    """Textual application showing live MIDI events and port configuration."""

    BINDINGS = [("q", "quit", "Quit"), ("p", "ports", "Configure Ports")]

    def __init__(self, thread_queue: queue.Queue, midi_io, config, save_callback=None):
        super().__init__()
        self.thread_queue = thread_queue
        self.midi_io = midi_io
        self.config = config
        self.save_callback = save_callback
        self._poller: asyncio.Task | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container():
            yield ListView(id="events")
        yield Footer()

    async def on_mount(self) -> None:
        # Start background task to poll the thread-safe queue
        self._poller = asyncio.create_task(self._poll_thread_queue())

    async def _poll_thread_queue(self) -> None:
        while True:
            try:
                e = self.thread_queue.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.05)
                continue
            await self._push_event(e)

    async def _push_event(self, e) -> None:
        lv = self.query_one("#events", ListView)
        entry = f"{e.timestamp:.3f} {e.message.type} {getattr(e.message, 'channel', '-')}: {str(e.message)}"
        await lv.append(ListItem(Static(entry)))
        # trim
        if len(lv.children) > 300:
            await lv.remove(lv.children[0])

    async def action_ports(self) -> None:
        inputs = self.midi_io.list_inputs()
        await self.push_screen(PortSelector("inputs", inputs, list(self.config.midi.inputs)))

    async def on_message(self, message) -> None:
        if isinstance(message, PortSelected):
            kind, selected, save = message.kind, message.selected, message.save
            try:
                if kind == "inputs":
                    self.config.midi.inputs = selected
                    self.midi_io.open_inputs(selected)
                else:
                    self.config.midi.outputs = selected
                    self.midi_io.open_outputs(selected)
                if save and self.save_callback:
                    try:
                        self.save_callback(self.config)
                    except Exception:
                        pass
            except Exception:
                pass

    async def action_quit(self) -> None:
        if self._poller:
            self._poller.cancel()
        await self.shutdown()


def run_tui(thread_queue: queue.Queue, midi_io, config, save_callback=None):
    app = MidiApp(thread_queue, midi_io, config, save_callback=save_callback)
    app.run()


if __name__ == "__main__":
    import sys

    print("Run via main.py")
    sys.exit(0)
from __future__ import annotations
from typing import List
import asyncio
import queue

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Checkbox, Static, ListView, ListItem
from textual.containers import Vertical, Horizontal, Container
from textual.screen import ModalScreen


class PortSelector(ModalScreen):
    """Modal screen to pick MIDI inputs or outputs via checkboxes."""

    def __init__(self, kind: str, items: List[str], current: List[str]):
        super().__init__()
        self.kind = kind
        self.items = items
        self.current = set(current)

    def compose(self) -> ComposeResult:
        yield Static(f"Select MIDI {self.kind.capitalize()}", id="title")
        with Vertical(id="list"):
            for name in self.items:
                checked = name in self.current
                yield Checkbox(label=name, value=checked, id=name)
        with Horizontal(id="buttons"):
            yield Button("Apply", id="apply", variant="primary")
            yield Button("Save & Apply", id="save")
            yield Button("Cancel", id="cancel", variant="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore
        if event.button.id == "cancel":
            await self.app.pop_screen()
            return
        selected: List[str] = []
        for name in self.items:
            cb = self.query_one(f"#{name}", Checkbox)
            if cb.value:
                selected.append(name)
        await self.app.post_message(PortSelected(self.kind, selected, save=(event.button.id == "save")))
        await self.app.pop_screen()


class PortSelected:
    def __init__(self, kind: str, selected: List[str], save: bool = False):
        self.kind = kind
        self.selected = selected
        self.save = save


class MidiApp(App):
    """Textual application showing live MIDI events and port configuration."""

    BINDINGS = [("q", "quit", "Quit"), ("p", "ports", "Configure Ports")]

    def __init__(self, thread_queue: queue.Queue, midi_io, config, save_callback=None):
        super().__init__()
        self.thread_queue = thread_queue
        self.midi_io = midi_io
        self.config = config
        self.save_callback = save_callback
        self._poller: asyncio.Task | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container():
            yield ListView(id="events")
        yield Footer()

    async def on_mount(self) -> None:
        # Start background task to poll the thread-safe queue
        self._poller = asyncio.create_task(self._poll_thread_queue())

    async def _poll_thread_queue(self) -> None:
        while True:
            try:
                e = self.thread_queue.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.05)
                continue
            await self._push_event(e)

    async def _push_event(self, e) -> None:
        lv = self.query_one("#events", ListView)
        entry = f"{e.timestamp:.3f} {e.message.type} {getattr(e.message, 'channel', '-')}: {str(e.message)}"
        await lv.append(ListItem(Static(entry)))
        # trim
        if len(lv.children) > 300:
            await lv.remove(lv.children[0])

    async def action_ports(self) -> None:
        inputs = self.midi_io.list_inputs()
        await self.push_screen(PortSelector("inputs", inputs, list(self.config.midi.inputs)))

    async def on_message(self, message) -> None:
        if isinstance(message, PortSelected):
            kind, selected, save = message.kind, message.selected, message.save
            try:
                if kind == "inputs":
                    self.config.midi.inputs = selected
                    self.midi_io.open_inputs(selected)
                else:
                    self.config.midi.outputs = selected
                    self.midi_io.open_outputs(selected)
                if save and self.save_callback:
                    try:
                        self.save_callback(self.config)
                    except Exception:
                        pass
            except Exception:
                pass

    async def action_quit(self) -> None:
        if self._poller:
            self._poller.cancel()
        await self.shutdown()


def run_tui(thread_queue: queue.Queue, midi_io, config, save_callback=None):
    app = MidiApp(thread_queue, midi_io, config, save_callback=save_callback)
    app.run()


if __name__ == "__main__":
    import sys

    print("Run via main.py")
    sys.exit(0)
from __future__ import annotations
from typing import List
import asyncio
import queue

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Checkbox, Static, ListView, ListItem
from textual.containers import Vertical, Horizontal, Container
from textual.screen import ModalScreen


class PortSelector(ModalScreen):
    def __init__(self, kind: str, items: List[str], current: List[str]):
        super().__init__()
        self.kind = kind
        self.items = items
        self.current = set(current)

    def compose(self) -> ComposeResult:
        yield Static(f"Select MIDI {self.kind.capitalize()}", id="title")
        with Vertical(id="list"):
            for name in self.items:
                checked = name in self.current
                yield Checkbox(label=name, value=checked, id=name)
        with Horizontal(id="buttons"):
            yield Button("Apply", id="apply", variant="primary")
            yield Button("Save & Apply", id="save")
            yield Button("Cancel", id="cancel", variant="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore
        if event.button.id == "cancel":
            await self.app.pop_screen()
            return
        # gather selections
        selected = []
        for name in self.items:
            cb = self.query_one(f"#{name}", Checkbox)
            if cb.value:
                selected.append(name)

        # send message to app
        await self.app.post_message(
            PortSelected(self.kind, selected, save=(event.button.id == "save"))
        )
        await self.app.pop_screen()


class PortSelected:  # simple message object
    def __init__(self, kind: str, selected: List[str], save: bool = False):
        self.kind = kind
        self.selected = selected
        self.save = save


class MidiApp(App):

            items = self.midi_io.list_inputs()
            current = list(self.config.midi.inputs)
        else:
            items = self.midi_io.list_outputs()
            current = list(self.config.midi.outputs)

        def render_selection():
            table = Table(title=f"Select MIDI {kind.capitalize()}")
            table.add_column("#", width=4)
            table.add_column("Sel", width=4)
            table.add_column("Name")
            for i, name in enumerate(items):
                sel = "[green]●[/green]" if name in current else "[dim]○[/dim]"
                table.add_row(str(i), sel, name)
            console.clear()
            console.print(table)
            console.print(
                "Commands: digits (toggle indices), a=all, n=none, d=done, s=save, q=cancel"
            )

        if not items:
            console.print("No MIDI ports available.")
            return

        while True:
            render_selection()
            cmd = console.input("cmd> ").strip()
            from __future__ import annotations
            from typing import List
            import asyncio
            import queue

            from textual.app import App, ComposeResult
            from textual.widgets import Header, Footer, Button, Checkbox, Static, ListView, ListItem
            from textual.containers import Vertical, Horizontal, Container
            from textual.screen import ModalScreen


            class PortSelector(ModalScreen):
                def __init__(self, kind: str, items: List[str], current: List[str]):
                    super().__init__()
                    self.kind = kind
                    self.items = items
                    self.current = set(current)

                def compose(self) -> ComposeResult:
                    yield Static(f"Select MIDI {self.kind.capitalize()}", id="title")
                    with Vertical(id="list"):
                        for name in self.items:
                            checked = name in self.current
                            yield Checkbox(label=name, value=checked, id=name)
                    with Horizontal(id="buttons"):
                        yield Button("Apply", id="apply", variant="primary")
                        yield Button("Save & Apply", id="save")
                        yield Button("Cancel", id="cancel", variant="error")

                async def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore
                    if event.button.id == "cancel":
                        await self.app.pop_screen()
                        return
                    # gather selections
                    selected = []
                    for name in self.items:
                        cb = self.query_one(f"#{name}", Checkbox)
                        if cb.value:
                            selected.append(name)

                    # send message to app
                    await self.app.post_message(
                        PortSelected(self.kind, selected, save=(event.button.id == "save"))
                    )
                    await self.app.pop_screen()


            class PortSelected:  # simple message object
                def __init__(self, kind: str, selected: List[str], save: bool = False):
                    self.kind = kind
                    self.selected = selected
                    self.save = save


            class MidiApp(App):
                CSS = """
            Screen > Container {
              padding: 1;
            }
            #list {
              height: 1fr;
            }
            """

                BINDINGS = [("q", "quit", "Quit"), ("p", "ports", "Configure Ports")]

                def __init__(self, thread_queue: queue.Queue, midi_io, config, save_callback=None):
                    super().__init__()
                    self.thread_queue = thread_queue
                    self.midi_io = midi_io
                    self.config = config
                    self.save_callback = save_callback
                    self._events: List = []
                    self._poller: asyncio.Task | None = None

                def compose(self) -> ComposeResult:
                    yield Header(show_clock=True)
                    with Container():
                        yield ListView(id="events")
                    yield Footer()

                async def on_mount(self) -> None:
                    # start poller task
                    self._poller = asyncio.create_task(self._poll_thread_queue())

                async def _poll_thread_queue(self) -> None:
                    while True:
                        try:
                            # non-blocking
                            e = self.thread_queue.get_nowait()
                            await self._push_event(e)
                        except queue.Empty:
                            await asyncio.sleep(0.05)

                async def _push_event(self, e) -> None:
                    item = ListItem(
                        Static(
                            f"{e.timestamp:.3f} {e.message.type} {getattr(e.message, 'channel', '-')}: {str(e.message)}"
                        )
                    )
                    lv = self.query_one("#events", ListView)
                    await lv.append(item)
                    # keep size reasonable
                    if len(lv.children) > 200:
                        await lv.remove(lv.children[0])

                async def action_ports(self) -> None:
                    # show inputs selector first
                    inputs = self.midi_io.list_inputs()
                    await self.push_screen(PortSelector("inputs", inputs, list(self.config.midi.inputs)))

                async def on_message(self, message) -> None:  # catch PortSelected
                    if isinstance(message, PortSelected):
                        kind, selected, save = message.kind, message.selected, message.save
                        try:
                            if kind == "inputs":
                                self.config.midi.inputs = selected
                                self.midi_io.open_inputs(selected)
                            else:
                                self.config.midi.outputs = selected
                                self.midi_io.open_outputs(selected)
                            if save and self.save_callback:
                                try:
                                    self.save_callback(self.config)
                                except Exception:
                                    pass
                        except Exception:
                            pass

                async def action_quit(self) -> None:
                    if self._poller:
                        self._poller.cancel()
                    await self.shutdown()


            def run_tui(thread_queue: queue.Queue, midi_io, config, save_callback=None):
                app = MidiApp(thread_queue, midi_io, config, save_callback=save_callback)
                app.run()


            if __name__ == "__main__":
                import sys

                print("Run via main.py")
                sys.exit(0)
