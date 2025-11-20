from pathlib import Path
from typing import NamedTuple
import yaml

from nexus_am.config import NexusAMConfig
from verilator.config import VerilatorConfig


class SimuBenConfig(NamedTuple):
    nexus_am: NexusAMConfig
    verilator: VerilatorConfig | None = None

    @classmethod
    def from_yaml_file(cls, path: Path):
        with open(path, "r") as f:
            dictionary = yaml.safe_load(f)
            return SimuBenConfig(
                nexus_am=NexusAMConfig(
                    path=Path(dictionary["nexus_am"]["path"]),
                ),
                verilator=None,
            )


class SimuBenInput(NamedTuple):
    config: SimuBenConfig
    source_path: Path
