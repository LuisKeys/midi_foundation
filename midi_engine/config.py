from dataclasses import dataclass, field
from typing import List
from pathlib import Path
import yaml


@dataclass
class MidiConfig:
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


@dataclass
class Config:
    midi: MidiConfig = field(default_factory=MidiConfig)


DEFAULT_PATH = Path(__file__).resolve().parent / "config.yaml"


def load_config(path: Path | str = DEFAULT_PATH) -> Config:
    p = Path(path)
    if not p.exists():
        return Config()
    data = yaml.safe_load(p.read_text()) or {}
    midi = data.get("midi", {})
    return Config(
        midi=MidiConfig(inputs=midi.get("inputs", []), outputs=midi.get("outputs", []))
    )


def save_config(cfg: Config, path: Path | str = DEFAULT_PATH) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {"midi": {"inputs": cfg.midi.inputs, "outputs": cfg.midi.outputs}}
    # atomic write
    tmp = p.with_suffix(".tmp")
    tmp.write_text(yaml.safe_dump(data))
    tmp.replace(p)
