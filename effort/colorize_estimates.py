from typing import Callable, Iterable

from matplotlib.colors import LinearSegmentedColormap, Normalize, to_hex, to_rgb


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
    import sys

    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = "effort-grid-estimates.txt"
    try:
        color_min = to_rgb(sys.argv[2])
        color_max = to_rgb(sys.argv[3])
    except IndexError:
        color_min = (1, 1, 1)
        color_max = (0.542, 0.211, 0.973)
    efforts = {}
    with open(file) as f:
        for line in f:
            char, effort = line.split()
            effort = float(effort)
            efforts[char] = effort

    mineffort = min(efforts.values())
    maxeffort = max(efforts.values())
    get_color = get_hex_func(
        mineffort, maxeffort, min_color=color_min, max_color=color_max
    )

    for char, effort in efforts.items():
        print(f"Char {char}: {effort:.2f}  color: {get_color(effort)}")
