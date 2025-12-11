#!/usr/bin/env python3

import argparse
import csv
import sys
from typing import NamedTuple


class BenchmarkData(NamedTuple):
    instructions: int
    cycles: int


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--old-path",
        required=True,
    )
    parser.add_argument(
        "-n",
        "--new-path",
        required=True,
    )
    return parser.parse_args()


def load_and_validate_csv(file_path: str, key_columns: list) -> dict:
    data = {}
    with open(file_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        try:
            header = next(reader)
        except StopIteration:
            raise ValueError(f"File '{file_path}' is empty or has no header.")

        required_cols = key_columns + ["instructions", "cycles"]
        if not all(col in header for col in required_cols):
            missing = set(required_cols) - set(header)
            raise ValueError(
                f"File '{file_path}' is missing required columns: "
                + f"{sorted(list(missing))}"
            )

        col_indices = {name: header.index(name) for name in required_cols}
        key_indices = [col_indices[name] for name in key_columns]

        for i, row in enumerate(reader, start=2):
            try:
                key = tuple(row[idx] for idx in key_indices)
                instructions = int(row[col_indices["instructions"]])
                cycles = int(row[col_indices["cycles"]])
            except (IndexError, ValueError) as e:
                raise ValueError(
                    f"Malformed data in '{file_path}' on line {i}: {row}. "
                    + f"Error: {e}"
                )

            if key in data:
                raise ValueError(
                    f"Duplicate key {key} found in '{file_path}' on line {i}."
                )

            data[key] = BenchmarkData(instructions, cycles)

    return data


def generate_diff(old_data: dict, new_data: dict) -> list:
    old_keys = set(old_data.keys())
    new_keys = set(new_data.keys())

    if old_keys != new_keys:
        missing_in_new = sorted(list(old_keys - new_keys))
        missing_in_old = sorted(list(new_keys - old_keys))
        error_messages = []
        if missing_in_new:
            error_messages.append(f"Keys in old file but not in new: {missing_in_new}")
        if missing_in_old:
            error_messages.append(f"Keys in new file but not in old: {missing_in_old}")
        raise ValueError("Key mismatch between files.\n" + "\n".join(error_messages))

    output_rows = []
    header = [
        "run_name",
        "test_suite_name",
        "instructions_old",
        "instructions_new",
        "instructions_diff_absolute",
        "instructions_diff_relative",
        "cycles_old",
        "cycles_new",
        "cycles_diff_absolute",
        "cycles_diff_relative",
    ]
    output_rows.append(header)

    sorted_keys = sorted(list(old_keys))

    for key in sorted_keys:
        old_row = old_data[key]
        new_row = new_data[key]

        inst_abs_diff = new_row.instructions - old_row.instructions
        inst_rel_diff = (inst_abs_diff / old_row.instructions) * 100

        cycles_abs_diff = new_row.cycles - old_row.cycles
        cycles_rel_diff = (cycles_abs_diff / old_row.cycles) * 100

        output_rows.append(
            [
                *key,
                old_row.instructions,
                new_row.instructions,
                inst_abs_diff,
                f"{inst_rel_diff:+.2f}%",
                old_row.cycles,
                new_row.cycles,
                cycles_abs_diff,
                f"{cycles_rel_diff:+.2f}%",
            ]
        )

    return output_rows


def write_csv_to_stdout(data: list):
    writer = csv.writer(sys.stdout)
    writer.writerows(data)


if __name__ == "__main__":
    try:
        args = parse_args()

        key_columns = ["test_suite_name"]
        old_data = load_and_validate_csv(args.old_path, key_columns)
        new_data = load_and_validate_csv(args.new_path, key_columns)

        result_data = generate_diff(old_data, new_data)

        write_csv_to_stdout(result_data)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
