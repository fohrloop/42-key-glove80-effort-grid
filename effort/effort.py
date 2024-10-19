from __future__ import annotations

import datetime as dt
import typing
from itertools import zip_longest
from pathlib import Path
from random import choice, sample, shuffle

from effort.config import FINGERS
from effort.keyboard import get_timing_for_trigram

if typing.TYPE_CHECKING:
    from typing import Iterable, Tuple


class TrigramCounter:

    def __init__(self, n_chars, trigrams_per_char: int, trigram_repeat_times: int):
        self.n_chars = n_chars
        self.trigrams_per_char = trigrams_per_char
        self.trigram_repeat_times = trigram_repeat_times
        self.count = 0
        self.n_trigrams = n_chars * trigrams_per_char
        self.n_repeats = self.n_trigrams * trigram_repeat_times

    def increment(self):
        self.count += 1


def effort_record(config: dict, output_file: Path):
    start_time = dt.datetime.now()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    total_chars = get_total_chars(config)
    counter = TrigramCounter(
        total_chars,
        trigram_repeat_times=config["trigram_repeat_times"],
        trigrams_per_char=config["trigrams_per_char"],
    )
    print(
        f"Total characters: {counter.n_chars}, Total trigrams: {counter.n_trigrams}, Total recordings: {counter.n_repeats}"
    )
    home_key_sequence_right = config["home_key_sequence_right"]
    home_key_sequence_left = config["home_key_sequence_left"]

    print("\nUse these home key sequences to start and end recording:")
    print(f"Right: {home_key_sequence_right}", end="  ")
    print(f"Left: {home_key_sequence_left}", end="\n\n")

    print(
        "TIP: If you need to take a break: The timers are not running when waiting for the home key combo."
    )
    for i, (finger, hand, char) in enumerate(iterate_chars_random(config), start=1):
        print(f"(Char {i}/{total_chars}) {hand} {finger}: {char} ")
        record_trigrams_for_char(
            char, hand, finger, config, output_file=output_file, counter=counter
        )

    end_time = dt.datetime.now()
    time_used_min = (end_time - start_time).total_seconds() / 60
    print(f"Total time used: {time_used_min:.2f} minutes")


def record_trigrams_for_char(
    char: str,
    hand: str,
    finger: str,
    config: dict,
    output_file: Path,
    counter: TrigramCounter,
):

    trigrams = get_trigrams(char, hand, finger, config)

    for trigram in trigrams:
        times = get_times_for_trigram(trigram, hand, config, counter=counter)
        with output_file.open("a") as f:
            timestxt = " ".join(str(t) for t in times)
            f.write(f"{trigram} {timestxt}\n")


def get_times_for_trigram(
    trigram: str, hand: str, config: dict, counter: TrigramCounter
):
    combo_left = config["home_key_sequence_right"]
    combo_right = config["home_key_sequence_left"]
    sequence = combo_right if hand == "left" else combo_left
    times = []
    for _ in range(config["trigram_repeat_times"]):
        counter.increment()
        time_seconds = get_timing_for_trigram(
            trigram,
            wait_sequence=sequence,
            wait_text=f'({counter.count}/{counter.n_repeats}) Trigram: {trigram} -- Press "{sequence}"" with {hand.upper()} hand to start the timer for recording the trigram.',
        )
        times.append(time_seconds)
    return times


def get_trigrams(char: str, hand: str, finger: str, config: dict):
    """Gets a list of random trigrams where the char is in the middle.
    Trigrams returned do not contain any Single Finger Bigrams (SFBs)"""

    trigrams = []
    hand_chars = config[hand].copy()
    hand_chars.pop(finger)
    other_fingers = sorted(hand_chars.keys())

    n = config["trigrams_per_char"]

    for _ in range(100_000):  # prevent infinite loop
        fingers = sample(other_fingers, 2)
        char1 = choice(hand_chars[fingers[0]])
        char3 = choice(hand_chars[fingers[1]])
        trigram = "".join((char1, char, char3))
        if trigram in trigrams:
            continue
        trigrams.append(trigram)
        if len(trigrams) >= n:
            break
    else:
        print("WARNING: Could not generate enough trigrams for char:", char)

    return trigrams


def iterate_chars(config: dict) -> Iterable[Tuple[str, str, str]]:
    """Iterate over all characters in the config. The length of the iterable
    is the same as the length of the all characters in the config.

    Each item is a tuple with the <finger>, <hand> and <char>.

    finger is one of "index", "middle", "ring", "pinky", "thumb"
    hand is one of "left" or "right"
    """
    for finger in FINGERS:
        chars_left = list(config["left"][finger])
        chars_right = list(config["right"][finger])

        for char_left, char_right in zip_longest(chars_left, chars_right):
            if char_right is not None:
                yield finger, "right", char_right
            if char_left is not None:
                yield finger, "left", char_left


def iterate_chars_random(config):
    chars = list(iterate_chars(config))
    chars_left = chars[::2]
    chars_right = chars[1::2]

    shuffle(chars_left)
    shuffle(chars_right)
    for left, right in zip_longest(chars_left, chars_right):
        if left is not None:
            yield left
        if right is not None:
            yield right


def get_total_chars(config: dict) -> int:
    left = config["left"]
    right = config["right"]

    total_chars = 0
    for finger in FINGERS:
        total_chars += len(left[finger]) + len(right[finger])
    return total_chars
