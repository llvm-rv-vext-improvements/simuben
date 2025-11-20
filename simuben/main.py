#!/usr/bin/env python3

import cli
from nexus_am.app import NexusAMApp


if __name__ == "__main__":
    input = cli.get_input()
    print("[simuben] Input:")
    print(input)

    nexus_am = input.config.nexus_am
    source = input.source_path
    with NexusAMApp(nexus_am, source) as app:
        app.build()

        print("[simuben] Executable:")
        print(app.executable.stat())

    print("[simuben] OK")
