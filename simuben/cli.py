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
        "--source",
        type=str,
        required=True,
        help="A path to source file to run",
    )

    args = parser.parse_args()

    return SimuBenInput(
        config=SimuBenConfig.from_yaml_file(args.config),
        source_path=Path(args.source),
    )
