from collections import defaultdict
from typing import Callable, Iterable

import numpy as np
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_hex
from sklearn.linear_model import LinearRegression

from effort.config import get_chars_for_hand


def read_xy_data(
    file, n_best: int, hand_chars: str, average: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    """
    Parameters
    ----------
    average : bool
        If True, the timings will be averaged over the n_best timings.
    """

    y_all = []
    x_all = []

    for chars, best_timings in iterate_trigrams(file, n_best):
        if average:
            y_all.append(np.mean(best_timings))
        else:
            y_all.extend(best_timings)
        x = []

        for char in hand_chars:
            is_used = 1 if char in chars else 0
            x.append(is_used)

        number_of_x = 1 if average else len(best_timings)
        for _ in range(number_of_x):
            x_all.append(x)

    return np.array(x_all), np.array(y_all)


def read_trigram_timings(file, n_best: int) -> tuple[list[str], list[float]]:
    timings = []
    trigrams = []
    for chars, best_timings in iterate_trigrams(file, n_best):
        timings.append(sum(best_timings) / len(best_timings))
        trigrams.append(chars)
    return trigrams, timings


def iterate_trigrams(file, n_best: int) -> Iterable[tuple[str, list[float]]]:
    with open(file, "r") as f:
        data = f.readlines()
    for line in data:
        chars, *timings = line.strip().split()
        best_timings = sorted(float(timing) for timing in timings)[: int(n_best)]
        yield chars, best_timings


def calculate(file, config: dict, calctype="model"):
    if calctype in ("average", "average-center"):
        show_averages(file, config, center=calctype == "average-center")
    elif calctype == "model":
        show_model(file, config)


def show_model(file, config: dict):
    models = {}
    for hand in ("left", "right"):
        chars = get_chars_for_hand(hand, config)
        X, y = read_xy_data(file, n_best=config["trigram_use_n_best"], hand_chars=chars)
        bias = (
            config["home_key_sequence_timing_left"]
            if hand == "left"
            else config["home_key_sequence_timing_right"]
        )
        y = y - bias

        model = LinearRegression(fit_intercept=False)
        model.fit(X, y)
        models[hand] = (model, chars)

    mineffort = min(min(models["left"][0].coef_), min(models["right"][0].coef_))
    maxeffort = max(max(models["left"][0].coef_), max(models["right"][0].coef_))
    get_color = get_hex_func(1.0, maxeffort / mineffort)
    print("Effort scale: ", mineffort)

    for hand, (model, chars) in models.items():
        print(f"\nHand: {hand}")
        coefs = model.coef_
        coefs = coefs / mineffort
        for i, coef in enumerate(coefs):
            print(f"Char {chars[i]}: {coef:.2f}   color: {get_color(coef)}")


def show_averages(file, config: dict, center: bool = False):
    data = defaultdict(lambda: defaultdict(int))
    trigrams, timings = read_trigram_timings(file, config["trigram_use_n_best"])

    for hand in ("left", "right"):
        chars = get_chars_for_hand(hand, config)
        for char in chars:
            char_timings = []
            for trigram, timing in zip(trigrams, timings):
                if not center and char in trigram:
                    char_timings.append(timing)
                elif center and char == trigram[1]:
                    char_timings.append(timing)
            char_ave_timing = sum(char_timings) / len(char_timings)
            bias = (
                config["home_key_sequence_timing_left"]
                if hand == "left"
                else config["home_key_sequence_timing_right"]
            )
            char_ave_timing -= bias
            data[hand][char] = char_ave_timing

    mineffort = min(min(data["left"].values()), min(data["right"].values()))
    maxeffort = max(max(data["left"].values()), max(data["right"].values()))
    get_color = get_hex_func(1.0, maxeffort / mineffort)
    print("Effort scale: ", mineffort)

    for hand, char_data in data.items():
        print(f"\nHand: {hand}")
        for char, char_ave_timing in char_data.items():
            effort = char_ave_timing / mineffort
            print(f"Char {char}: {effort:.2f}  color: {get_color(effort)}")


def get_hex_func(
    min_value: float,
    max_value: float,
    min_color=(1, 1, 1),
    max_color=(0.542, 0.211, 0.973),
    n_bins=100,
) -> Callable[[float], str]:
    colors = [min_color, max_color]
    custom_cmap = LinearSegmentedColormap.from_list(
        "custom_color_map", colors, N=n_bins
    )

    norm = Normalize(vmin=min_value, vmax=max_value)

    return lambda x: to_hex(custom_cmap(norm(x)))
