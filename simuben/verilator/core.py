from pathlib import Path
import subprocess

from verilator.log import (
    VerilatorLog,
    verilator_brief_log_parse,
    verilator_perf_log_parse,
)
from verilator.config import VerilatorConfig


class Verilator:
    def __init__(self, config: VerilatorConfig) -> None:
        self.__config = config

    def run(self, executable: Path) -> VerilatorLog:
        command = [
            str(self.__config.executable_path),
            "--no-diff",
            "-i",
            executable,
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(
                f"{' '.join(command)} returned {process.returncode}: {process.stderr}",
            )

        return VerilatorLog(
            brief=verilator_brief_log_parse(stdout.splitlines()),
            perf=verilator_perf_log_parse(stderr.splitlines()),
        )
