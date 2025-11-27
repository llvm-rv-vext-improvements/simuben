from pathlib import Path
from typing import NamedTuple
import yaml

from nexus_am.config import NexusAMConfig
from nemu.config import NEMUConfig
from verilator.config import VerilatorConfig


class SimuBenConfig(NamedTuple):
    nexus_am: NexusAMConfig
    verilator: VerilatorConfig | None = None
    nemu: NEMUConfig | None = None

    @classmethod
    def from_yaml_file(cls, path: Path):
        with open(path, "r") as f:
            yml = yaml.safe_load(f)
            return SimuBenConfig(
                nexus_am=NexusAMConfig(
                    path=Path(yml["nexus_am"]["path"]),
                    toolchain_path=Path(yml["nexus_am"]["toolchain_path"]),
                ),
                verilator=(
                    VerilatorConfig(
                        executable_path=Path(yml["verilator"]["path"]),
                    )
                    if "verilator" in yml
                    else None
                ),
                nemu=(
                    NEMUConfig(
                        executable_path=Path(yml["nemu"]["path"]),
                    )
                    if "nemu" in yml
                    else None
                ),
            )


class SimuBenInput(NamedTuple):
    config: SimuBenConfig
    sources: list[Path]
