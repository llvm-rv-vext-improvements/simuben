from dataclasses import asdict, dataclass
from io import StringIO
import yaml
import csv


from verilator.log import VerilatorLog


@dataclass
class CSVConfig:
    core_number: int = 0
    is_header_hidden: bool = False


def verilator_brief_to_yml(brief: VerilatorLog.Brief) -> str:
    return yaml.dump(asdict(brief))


def verialtor_brief_to_csv(brief: VerilatorLog.Brief, cfg: CSVConfig) -> str:
    output = StringIO()
    writer = csv.writer(output)

    if not cfg.is_header_hidden:
        writer.writerow(["Instructions", "Cycles"])

    cores = [core for core in brief.cores if core.core_number == cfg.core_number]
    for core in cores:
        writer.writerow([core.instrunctions_count, core.cycles_count])

    return output.getvalue()
