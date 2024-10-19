from typing import Callable, Iterable

from matplotlib.colors import LinearSegmentedColormap, Normalize, to_hex


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


if __name__ == "__main__":
    efforts = {}
    with open("effort-grid-estimates.txt") as f:
        for line in f:
            char, effort = line.split()
            effort = float(effort)
            efforts[char] = effort

    mineffort = min(efforts.values())
    maxeffort = max(efforts.values())
    get_color = get_hex_func(1.0, maxeffort / mineffort)

    for char, effort in efforts.items():
        print(f"Char {char}: {effort:.2f}  color: {get_color(effort)}")
