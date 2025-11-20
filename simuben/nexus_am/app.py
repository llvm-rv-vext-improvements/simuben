import os
from pathlib import Path
import shutil
import subprocess
from config import NexusAMConfig


class NexusAMApp:
    def __init__(self, config: NexusAMConfig, source_path: Path) -> None:
        self.__config = config
        self.__source_path = source_path

    def __enter__(self) -> "NexusAMApp":
        dir = self.__dir
        dir.mkdir(exist_ok=True)

        source = dir / self.__source
        shutil.copyfile(self.__source_path, source)

        makefile = dir / "Makefile"
        with open(makefile, "w") as f:
            f.write(self.__makefile)

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        shutil.rmtree(self.__dir)

    def build(self) -> None:
        input("Press enter to continue")

        command = ["make", "ARCH=riscv64-xs"]
        os.environ["AM_HOME"] = str(self.__config.path)

        result = subprocess.run(
            command,
            cwd=self.__dir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"{' '.join(command)} returned {result.returncode}: {result.stderr}",
            )

    @property
    def name(self) -> str:
        return self.__source_path.stem

    @property
    def executable(self) -> Path:
        return self.__dir / "build" / f"{self.name}.bin"

    @property
    def __dir(self) -> Path:
        return self.__config.path / "apps" / self.name

    @property
    def __source(self) -> str:
        return self.__source_path.name

    @property
    def __makefile(self) -> str:
        return "\n".join(
            [
                f"NAME = {self.name}",
                f"SRCS = {self.__source}",
                f"include $(AM_HOME)/Makefile.app",
            ],
        )
