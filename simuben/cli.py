from argparse import ArgumentParser
from pathlib import Path

from config import SimuBenConfig, SimuBenInput


def get_input() -> SimuBenInput:
    parser = ArgumentParser(
        prog="simuben",
        description="A tool for benchmarking on XiangShan simulators",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=False,
        default=f"{parser.prog}.yml",
        help="A path to configuration file",
    )
    parser.add_argument(
        "-s",
        "--sources",
        type=str,
        nargs="+",
        help="A paths to source files to run",
    )

    args = parser.parse_args()

    return SimuBenInput(
        config=SimuBenConfig.from_yaml_file(args.config),
        sources=[Path(_) for _ in args.sources],
    )
