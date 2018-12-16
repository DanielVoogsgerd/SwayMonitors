#!/usr/bin/env python
import sway_monitors
import json


def main():
    setup = sway_monitors.Setup()

    with open("setup.json") as f:
        setups = json.loads(f.read())

    setup.check_and_enable_setup(setups["home_setup"])
    setup.check_and_enable_setup(setups["work_setup"])


if __name__ == "__main__":
    main()

