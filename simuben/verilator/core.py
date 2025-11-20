from pathlib import Path
import subprocess
from verilator.config import VerilatorConfig


class Verilator:
    def __init__(self, config: VerilatorConfig) -> None:
        self.__config = config

    def run(self, executable: Path):
        command = [
            str(self.__config.executable_path),
            "--no-diff",
            "-i",
            executable,
        ]

        result = subprocess.run(
            command,
            capture_output=False,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"{' '.join(command)} returned {result.returncode}: {result.stderr}",
            )
