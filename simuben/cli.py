from argparse import ArgumentParser
from pathlib import Path

from config import ExportConfig, SimuBenConfig, SimuBenInput
from verilator.log_export import CSVConfig


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
        required=True,
        help="A paths to source files to run",
    )
    parser.add_argument(
        "--csv-core-number",
        type=int,
        default=0,
        help="A core number for csv output.",
    )
    parser.add_argument(
        "--csv-no-header",
        action="store_true",
        help="Do not show a header for csv output.",
    )

    args = parser.parse_args()

    config = SimuBenConfig.from_yaml_file(args.config)

    config = config._replace(
        export=ExportConfig(
            CSVConfig(
                core_number=args.csv_core_number,
                is_header_hidden=args.csv_no_header,
            )
        )
    )

    return SimuBenInput(
        config=config,
        sources=[Path(_) for _ in args.sources],
    )
