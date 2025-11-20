#!/usr/bin/env python3

import re
import argparse
from collections import defaultdict
from typing import List, DefaultDict
from pathlib import Path

Time = int
MetricNamespace = str
MetricName = str
MetricValue = int

NemuLog = DefaultDict[
    Time,
    DefaultDict[
        MetricNamespace,
        DefaultDict[
            MetricName,
            List[MetricValue],
        ],
    ],
]


def argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("file", type=str)

    return parser


def nemu_log_parse(file: Path) -> NemuLog:
    pattern: re.Pattern = re.compile(
        r"\[PERF \]\[time=\s*(\d+)\]\s*([^:]+):\s*([^,]+),\s*(\d+)"
    )

    data: NemuLog = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    with open(file, "r") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if len(line) == 0:
                continue

            match = pattern.match(line)
            if not match:
                raise RuntimeError(f"Warning: Could not parse line {i}: {line}")

            time: Time = int(match.group(1))
            path: MetricNamespace = match.group(2).strip()
            name: MetricName = match.group(3).strip()
            value: MetricValue = int(match.group(4))

            data[time][path][name].append(value)

    return data


def nemu_log_print(log: NemuLog) -> None:
    for _, dct in log.items():
        for path, dct in dct.items():
            for name, lst in dct.items():
                if not any(v != 0 for v in lst):
                    continue

                print(f"{path}.{name}: {lst}")


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparser()
    args: argparse.Namespace = parser.parse_args()

    file: Path = Path(args.file)
    log: NemuLog = nemu_log_parse(file)
    nemu_log_print(log)
