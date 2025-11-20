from pathlib import Path
import subprocess

from verilator.log import NemuLog, nemu_log_parse
from verilator.config import VerilatorConfig


class Verilator:
    def __init__(self, config: VerilatorConfig) -> None:
        self.__config = config

    def run(self, executable: Path) -> NemuLog:
        command = [
            str(self.__config.executable_path),
            "--no-diff",
            "-i",
            executable,
        ]

        process = subprocess.Popen(
            command,
            stderr=subprocess.PIPE,
            text=True,
        )

        _, stderr = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(
                f"{' '.join(command)} returned {process.returncode}: {process.stderr}",
            )

        return nemu_log_parse(stderr.splitlines())
