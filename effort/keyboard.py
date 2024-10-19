import logging
import time
from typing import Literal

from pynput import keyboard

logger = logging.getLogger(__name__)

State = Literal[
    "NOT_STARTED",
    "RECORDING_STARTING_SEQUENCE",
    "RECORDING_TRIGRAM",
    "RECORDING_FINAL_SEQUENCE",
]


class TrigramTimingRecorder:

    def __init__(self, trigram: str, wait_sequence: str, wait_text: str = ""):
        self.trigram = trigram
        self.sequence = wait_sequence
        self.sequence_keys = list(wait_sequence)
        self.trigram_keys = list(trigram)
        self.delta_time: float = 0
        self.start_time: float = 0
        self.state: State = "NOT_STARTED"
        self.pressed_keys: list[str] = []
        self.wait_text = wait_text
        self.ctrl_pressed = False
        self.asked_quit = False
        self.start_recording_starting_sequence()

    def start_recording_starting_sequence(self):
        if self.wait_text:
            print("\r" + self.wait_text)
        else:
            print(f'\rType sequence "{self.sequence}" to start recording')
        self.restart_recording_sequence("RECORDING_STARTING_SEQUENCE")

    def start_recording_final_sequence(self):
        print(f'\rType sequence "{self.sequence}" to end recording')
        self.restart_recording_sequence("RECORDING_FINAL_SEQUENCE")

    def restart_recording_sequence(self, state: State):
        self.state = state
        self.pressed_keys = []
        self.expected_keys = self.sequence_keys

    def start_recording_trigram(self):
        self.state = "RECORDING_TRIGRAM"
        self.pressed_keys = []
        self.expected_keys = self.trigram_keys
        print(f'\rType: "{self.trigram}":')
        self.start_time = time.monotonic()

    def finalize(self):
        self.delta_time = time.monotonic() - self.start_time
        print(f"\r OK! ({self.delta_time*1000:.0f} ms)")

    def on_press(self, key):
        char = get_char(key)
        self.pressed_keys.append(char)

        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = True
        elif char:
            print(char, end="", flush=True)

        if self.ctrl_pressed and char == "c":
            print("\nCtrl-C pressed, exiting...")
            self.asked_quit = True
            return False

        if self.pressed_keys != self.expected_keys[: len(self.pressed_keys)]:
            self._act_on_error()

    def _act_on_error(self):

        if self.state == "RECORDING_STARTING_SEQUENCE":
            self.restart_recording_sequence("RECORDING_STARTING_SEQUENCE")
        elif (
            self.state == "RECORDING_TRIGRAM"
            or self.state == "RECORDING_FINAL_SEQUENCE"
        ):
            print(
                ' Pressed wrong key! Pressed: "{}", expecting: "{}"'.format(
                    self.pressed_keys, self.expected_keys
                )
            )
            self.start_recording_starting_sequence()

    def on_release(self, key):

        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False

        if self.pressed_keys == self.expected_keys:
            if self.state == "RECORDING_STARTING_SEQUENCE":
                self.start_recording_trigram()
            elif self.state == "RECORDING_TRIGRAM":
                self.start_recording_final_sequence()
            elif self.state == "RECORDING_FINAL_SEQUENCE":
                self.finalize()
                return False  # stop listening


def get_timing_for_trigram(trigram: str, wait_sequence: str, wait_text: str) -> float:
    recorder = TrigramTimingRecorder(trigram, wait_sequence, wait_text)
    with keyboard.Listener(
        on_press=recorder.on_press, on_release=recorder.on_release, suppress=True
    ) as listener:
        listener.join()

    if recorder.asked_quit:
        # Extra step: Pressing Ctrl-C _anywhere_ (in any application) would
        # quit, and since the recording takes a long time, better ask for
        # confirmation.
        if (
            input(
                'Type "quit" + Enter to confirm quitting. Type anything else + Enter to continue:\n'
            )
            == "quit"
        ):
            exit()
        else:
            return get_timing_for_trigram(trigram, wait_sequence, wait_text)
    return recorder.delta_time


def get_char(key) -> str | None:

    try:
        char = key.char.lower()
    except AttributeError:
        logger.warning(
            f"Special key '{key}' pressed! If you did not press a special key, something is wrong."
        )
        return None  # special key

    if len(char) != 1:
        return None  # something is wrong. (should not happen?)

    return char


def estimate_bias(repetitions: int = 10, wait_sequence: str = "lkj"):
    total_time = 0
    for _ in range(repetitions):
        # Divide by two as the time is recorded twice.
        total_time += get_timing_for_trigram(wait_sequence, wait_sequence, "") / 2
    return total_time / repetitions


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    get_timing_for_trigram(
        "lps",
        "lkj",
        "(1/1) Type 'lkj' with RIGHT hand to start the timer for recording the trigram.",
    )
