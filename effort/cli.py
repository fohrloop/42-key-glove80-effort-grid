from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import Literal

import typer

try:
    from typing import Annotated
except ImportError:
    # For older python versions
    from typing_extensions import Annotated  # type: ignore

from effort import effort_record
from effort.calculate import calculate
from effort.config import read_config_file

ARG_CONFIG_FILE = Annotated[
    Path,
    typer.Argument(
        help="Path to a Effort grid record configuration YAML file.",
        show_default=False,
    ),
]

ARG_OUTPUT_FILE = Annotated[
    Path,
    typer.Argument(
        help="Output file path for the effort grid record (raw output data).",
        show_default=False,
    ),
]


ARG_FORCE = Annotated[
    bool,
    typer.Option(
        "--force",
        help="Override the effort grid record (raw output data) file, if it exists.",
    ),
]


def effort_grid_record(
    config_file: ARG_CONFIG_FILE,
    output_file: ARG_OUTPUT_FILE,
    force: ARG_FORCE = False,
):
    """Records effort grid data."""

    if output_file.exists():
        if not force:
            raise typer.BadParameter(
                f"Output file {output_file} already exists. Use --force to overwrite."
            )
        else:
            output_file.unlink()

    config = read_config_file(config_file)
    effort_record(config, output_file)
    print(f"Done! Raw data saved to {output_file}")


ARG_RAW_EFFORT_GRID_RECORD = Annotated[
    Path,
    typer.Argument(
        help="File path for the effort grid record (raw output data) to use.",
        show_default=False,
    ),
]


class CalculationType(str, Enum):
    model = "model"
    average = "average"
    average_center = "average-center"


ARG_TYPE = Annotated[
    CalculationType,
    typer.Option(
        "--type",
        help="How to calculate the results. 'model' will fit a linear model, 'average' will just average over the trigrams timings, and 'average-center' will average over the trigrams timings where given character is in the middle of the trigram.",
    ),
]


def effort_grid_show(
    config_file: ARG_CONFIG_FILE,
    record_file: ARG_RAW_EFFORT_GRID_RECORD,
    calctype: ARG_TYPE = "model",
):
    """Shows results based on recorded effort grid data."""

    config = read_config_file(config_file)
    calculate(record_file, config, calctype=calctype)


def cli_effort_grid_record():
    setup_logging()
    typer.run(effort_grid_record)


def cli_effort_grid_show():
    setup_logging()
    typer.run(effort_grid_show)


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.WARNING,
    )
