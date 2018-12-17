#!/usr/bin/env python
import sway_monitors
import json
import os

def main():
    setup = sway_monitors.Setup()

    with open(os.path.join(os.path.dirname(__file__), "setup.json")) as f:
        setups = json.loads(f.read())

    setup.check_and_enable_setup(setups["home_setup"])
    setup.check_and_enable_setup(setups["work_setup"])


if __name__ == "__main__":
    main()

