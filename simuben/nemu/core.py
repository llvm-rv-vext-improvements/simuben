from pathlib import Path
import subprocess

from nemu.config import NEMUConfig


class NEMU:
    def __init__(self, config: NEMUConfig) -> None:
        self.__config = config

    def run(self, executable: Path) -> list[str]:
        command = [
            str(self.__config.executable_path),
            executable,
            "--batch",
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            text=True,
        )

        stdout, _ = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(
                f"{' '.join(command)} returned {process.returncode}: {process.stderr}",
            )

        return stdout.splitlines()
