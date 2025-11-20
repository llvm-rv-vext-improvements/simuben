#!/usr/bin/env python3

import cli
from nexus_am.app import NexusAMApp
from verilator.log import nemu_log_print
from verilator.core import Verilator

if __name__ == "__main__":
    input = cli.get_input()

    nexus_am = input.config.nexus_am
    sources = input.sources
    with NexusAMApp(nexus_am, sources) as app:
        print(f"[simuben] Building the app {app.name}...")
        app.build()

        if verilator := input.config.verilator:
            emu = Verilator(verilator)

            print("[simuben] Running on verilator...")
            log = emu.run(app.executable)

            print("[simuben] Printing the log to /tmp/verilator.log...")
            with open("/tmp/verilator.log", "w") as f:
                nemu_log_print(log, f)

    print("[simuben] OK")
