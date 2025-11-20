import os
from pathlib import Path
import shutil
import subprocess
from config import NexusAMConfig


class NexusAMApp:
    def __init__(self, config: NexusAMConfig, sources: list[Path]) -> None:
        self.__config = config
        self.__sources = sources

    def __enter__(self) -> "NexusAMApp":
        dir = self.__dir
        dir.mkdir(exist_ok=True)

        for src in self.__sources:
            dst = dir / src.name
            shutil.copyfile(src, dst)

        makefile = dir / "Makefile"
        with open(makefile, "w") as f:
            f.write(self.__makefile)

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        shutil.rmtree(self.__dir)

    def build(self) -> None:
        command = self.__command_clang()
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
        return self.__sources[0].stem

    @property
    def executable(self) -> Path:
        return self.__dir / "build" / f"{self.name}-riscv64-xs.bin"

    def __command_clang(self) -> list[str]:
        flags = " ".join(
            [
                "-target",
                "riscv64-unknown-elf",
                "-nostdlib",
                "-ffreestanding",
                "-Wno-empty-body",
                "-Wno-unused-command-line-argument",
                "-Wno-override-module",
            ],
        )

        r = self.__config.toolchain_path / "bin"

        return [
            f"make",
            f"ARCH=riscv64-xs",
            f"CC={r}/clang {flags}",
            f"AS={r}/clang {flags}",
            f"LD={r}/ld.lld",
            f"OBJDUMP={r}/llvm-objdump",
            f"OBJCOPY={r}/llvm-objcopy",
            f"AR={r}/llvm-ar",
        ]

    @property
    def __dir(self) -> Path:
        return self.__config.path / "apps" / self.name

    @property
    def __makefile(self) -> str:
        return "\n".join(
            [
                f"NAME = {self.name}",
                f"SRCS = {' '.join(map(str, self.__sources))}",
                f"include $(AM_HOME)/Makefile.app",
                f"$(DST_DIR)/%.o: %.ll",
                f"\t@mkdir -p $(dir $@) && echo + CC $<",
                f"\t@$(CC) $(CPPFLAGS) -std=gnu11 $(CFLAGS) -c -o $@ $(realpath $<)",
            ],
        )
