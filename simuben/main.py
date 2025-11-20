#!/usr/bin/env python3

import cli
from nexus_am.app import NexusAMApp
from verilator.core import Verilator

if __name__ == "__main__":
    input = cli.get_input()
    print("[simuben] Input:")
    print(input)

    nexus_am = input.config.nexus_am
    sources = input.sources
    with NexusAMApp(nexus_am, sources) as app:
        app.build()

        print("[simuben] Executable:")
        print(app.executable.stat())

        if verilator := input.config.verilator:
            emu = Verilator(verilator)
            print("[simuben] Running on verilator")
            emu.run(app.executable)

    print("[simuben] OK")
