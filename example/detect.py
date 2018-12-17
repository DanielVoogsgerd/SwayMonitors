#!/usr/bin/env python
import sway_monitors
import json
import os

def main():
    setup = sway_monitors.Setup()

    with open(os.path.join(os.path.dirname(__file__), "setup.json")) as f:
        setups = json.loads(f.read())


    if setup.check_setup(setups['home_setup']):
        setup.enable(setups['home_setup'], direction="right")

    if setup.check_setup(setups['work_setup']):
        setup.enable(setups['work_setup'], direction="right")


if __name__ == "__main__":
    main()

