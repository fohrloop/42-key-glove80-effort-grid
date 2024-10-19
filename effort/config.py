from pathlib import Path
from typing import Literal, TypedDict

import yaml

FINGERS = ("index", "middle", "ring", "pinky", "thumb")

Hand = Literal["left", "right"]


class Config(TypedDict):
    left: str
    right: str


def get_chars_for_hand(hand: Hand, config: dict):
    chars_lst = []
    chars_hand = config[hand]
    for finger in FINGERS:
        chars_lst.append(chars_hand[finger])
    return "".join(chars_lst)


def read_config_file(file) -> Config:
    file = Path(file)
    if not file.exists():
        raise FileNotFoundError(f"File {file} not found")
    return parse_config(file.read_text())


def parse_config(config: str) -> Config:
    return yaml.safe_load(config)
