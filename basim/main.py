#!/usr/bin/env python3

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, NamedTuple


class Config(NamedTuple):
    simuben_executable: Path
    config_path: Path
    run_name: str
    tests_dir: Path


class TestSuite(NamedTuple):
    name: str
    source_absolute_paths: List[Path]


TEMP_DIR = Path("/tmp")
BASIM_OUTPUT_DIR = TEMP_DIR / "basim"

SIMUBEN_TEMP_FILES = {
    "nemu.log": TEMP_DIR / "nemu.log",
    "verilator.log": TEMP_DIR / "verilator.log",
    "verilator.brief.csv": TEMP_DIR / "verilator.brief.csv",
}


def parse_arguments() -> Config:
    parser = argparse.ArgumentParser(
        description="A wrapper tool to run simuben on multiple test suites."
    )
    parser.add_argument(
        "-r",
        "--run-name",
        type=str,
        help="A unique name for this execution run.",
    )
    parser.add_argument(
        "-d",
        "--dir",
        type=Path,
        help="Path to the root directory containing test suites.",
    )
    parser.add_argument(
        "-s",
        "--simuben",
        type=Path,
        help="Path to the simuben executable (e.g., ./simuben/main.py).",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help="Path to the simuben.yml configuration file.",
    )
    args = parser.parse_args()

    return Config(
        tests_dir=args.dir.resolve(),
        config_path=args.config.resolve(),
        run_name=args.run_name,
        simuben_executable=args.simuben.resolve(),
    )


def discover_test_suites(tests_dir: Path) -> List[TestSuite]:
    print(f"[basim] Discovering test suites in '{tests_dir}'...")

    if not tests_dir.is_dir():
        raise FileNotFoundError(f"Provided test directory does not exist: {tests_dir}")

    suites = []
    for suite_dir in tests_dir.iterdir():
        if not suite_dir.is_dir():
            continue

        sources = [
            f.resolve()
            for f in suite_dir.rglob("*")
            if f.is_file() and f.suffix in {".c", ".cpp", ".cc", ".cxx", ".ll"}
        ]

        if len(sources) == 0:
            raise FileNotFoundError(f"No sources was found at {tests_dir}")

        suites.append(TestSuite(name=suite_dir.name, source_absolute_paths=sources))
        print(
            f"[basim]   - Found suite '{suite_dir.name}' "
            + f"with {len(sources)} source file(s)."
        )

    suites.sort(key=lambda s: s.name)
    return suites


def run_simuben(test_suite: TestSuite, config: Config):
    print(f"[basim] Running simuben for test suite '{test_suite.name}'...")

    cmd = [
        str(config.simuben_executable),
        "--sources",
        *[str(p) for p in test_suite.source_absolute_paths],
        "--config",
        str(config.config_path),
    ]

    subprocess.run(cmd, check=True, text=True, encoding="utf-8")
    print(f"[basim]   - Simuben finished successfully.")


def copy_artifacts(test_suite: TestSuite, config: Config) -> Path:
    print(f"[basim] Copying artifacts for '{test_suite.name}'...")

    dest_dir = BASIM_OUTPUT_DIR / config.run_name / test_suite.name
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied_csv_log_path = None

    for artifact in SIMUBEN_TEMP_FILES.keys():
        src = SIMUBEN_TEMP_FILES[artifact]
        dst = dest_dir / artifact

        if not src.exists():
            print(f"[basim]   - Artifact '{src}' not found, skipping.")
            continue

        print(f"[basim]   - Copying '{src}' to '{dst}'")
        shutil.copy(src, dst)

        if artifact == "verilator.brief.csv":
            copied_csv_log_path = dst

    assert copied_csv_log_path is not None
    return copied_csv_log_path


def merge_csvs(individual_log_paths: List[Path], run_name: str, output_dir: Path):
    print("[basim] Merging all 'verilator.brief.log' files (as CSV)...")
    output_path = output_dir / "verilator.brief.merged.csv"

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)

        header_written = False
        for log_path in individual_log_paths:
            test_suite_name = log_path.parent.name
            print(f"[basim]   - Processing '{log_path}' for suite '{test_suite_name}'")

            with open(log_path, "r", newline="", encoding="utf-8") as infile:
                reader = csv.reader(infile)

                try:
                    original_header = next(reader)
                except StopIteration:
                    raise ValueError(f"CSV-formatted log file is empty: {log_path}")

                if not header_written:
                    new_header = ["run_name", "test_suite_name"] + original_header
                    writer.writerow(new_header)
                    header_written = True

                rows_processed = 0
                for row in reader:
                    if len(row) == 0:
                        continue

                    writer.writerow([run_name, test_suite_name] + row)
                    rows_processed += 1

                if rows_processed == 0:
                    raise ValueError(
                        f"CSV-formatted log file contains only a header: {log_path}"
                    )

    print(f"[basim] Merge complete. Output written to '{output_path}'.")


def main():
    config = parse_arguments()
    run_output_dir = BASIM_OUTPUT_DIR / config.run_name

    try:
        if run_output_dir.exists():
            print(
                f"[basim] [!] Warning: Output directory '{run_output_dir}' already exists. Overwriting."
            )
            shutil.rmtree(run_output_dir)

        run_output_dir.mkdir(parents=True, exist_ok=True)
        print(
            f"[basim] Starting basim run '{config.run_name}'. Output will be in '{run_output_dir}'"
        )

        test_suites = discover_test_suites(config.tests_dir)
        if not test_suites:
            raise FileNotFoundError(
                f"No valid test suites with source files found in '{config.tests_dir}'"
            )

        generated_csv_logs = []
        for suite in test_suites:
            print("-" * 50)
            run_simuben(suite, config)
            csv_log_path = copy_artifacts(suite, config)
            generated_csv_logs.append(csv_log_path)

        print("-" * 50)
        merge_csvs(generated_csv_logs, config.run_name, run_output_dir)

        print("\n[basim] [+] Basim run completed successfully.")

    except Exception as e:
        print(f"\n[basim] [!] An error occurred: {e}", file=sys.stderr)
        print(
            f"[basim] [!] Cleaning up failed run directory: '{run_output_dir}'",
            file=sys.stderr,
        )
        shutil.rmtree(run_output_dir, ignore_errors=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
