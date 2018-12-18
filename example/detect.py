#!/usr/bin/env python
import sway_monitors
import json
import os

def main():
    setup = sway_monitors.Setup()

    with open(os.path.join(os.path.dirname(__file__), "setup.json")) as f:
        setups = json.loads(f.read())

    try:
        if setup.check_setup(setups['home_setup']):
            setup.enable(setups['home_setup'], direction="right")

        return
    except sway_monitors.CommandError as e:
        fallback_monitor = setup.find_monitor({'name': 'eDP-1'})
        fallback_monitor.enable((0, 0))
        raise


    try:
        if setup.check_setup(setups['work_setup']):
            setup.enable(setups['work_setup'], direction="right")

        return
    except sway_monitors.CommandError as e:
        fallback_monitor = setup.find_monitor({'name': 'eDP-1'})
        fallback_monitor.enable((0, 0))
        raise

    fallback_monitor = setup.find_monitor({'name': 'eDP-1'})
    fallback_monitor.enable((0, 0))


if __name__ == "__main__":
    main()

