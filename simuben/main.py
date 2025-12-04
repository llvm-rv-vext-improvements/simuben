#!/usr/bin/env python3

import cli
from nexus_am.app import NexusAMApp
from nemu.core import NEMU
from verilator.log import verilator_log_print
from verilator.core import Verilator

if __name__ == "__main__":
    input = cli.get_input()

    nexus_am = input.config.nexus_am
    sources = input.sources
    with NexusAMApp(nexus_am, sources) as app:
        print(f"[simuben] Building the app {app.name}...")
        app.build()

        if nemu := input.config.nemu:
            emu = NEMU(nemu)

            print("[simuben] Running on the NEMU...")
            log = emu.run(app.executable)
            print()

            print("[simuben] Printing the log to /tmp/nemu.log...")
            with open("/tmp/nemu.log", "w") as f:
                f.writelines(line + '\n' for line in log)

        if verilator := input.config.verilator:
            emu = Verilator(verilator)

            print("[simuben] Running on the Verilator...")
            log = emu.run(app.executable)
            print()

            print("[simuben] Printing the log to /tmp/verilator.log...")
            with open("/tmp/verilator.log", "w") as f:
                verilator_log_print(log, f)

    print("[simuben] OK")
