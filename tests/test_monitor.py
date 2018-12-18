import unittest
from sway_monitors import MonitorMode, Setup, Monitor
import json
from .FakeConnection import FakeConnection

class MonitorTest(unittest.TestCase):
    def setUp(self):
        self.monitors = []
        self.connection = FakeConnection()
        with open('tests/setup.json') as f:
            data = json.loads(f.read())

        for monitor_props in data:
            self.monitors.append(Monitor(monitor_props, self.connection))

    def test_no_modes(self):
        # TODO: Add disabled monitor to setup.json
        pass

    def test_enable(self):
        monitor = self.monitors[0]
        monitor.enable((10, 10), background="./test/ExistingWallpaper.jpg")
        self.assertRegex(self.connection.command_list[0], "output DP-3 position 10 10 resolution 1920x1080 bg \S*/test/ExistingWallpaper.jpg")

        self.connection.clear()
        monitor.enable((10, 10))
        self.assertEqual(self.connection.command_list[0], "output DP-3 position 10 10 resolution 1920x1080")

    def test_enable_disabled(self):
        monitor = self.monitors[2]
        monitor.modes = []
        monitor.enable((10, 10))

    def test_disable(self):
        monitor = self.monitors[0]
        monitor.disable()
        self.assertEqual(self.connection.command_list[0], "output DP-3 disable")

    def test_background_non_existing(self):
        monitor = self.monitors[0]
        with self.assertRaises(Exception):
            monitor.background('NonExistingWallpaper.jpg', 'fill')

    def test_background(self):
        monitor = self.monitors[0]
        monitor.background('./tests/ExistingWallpaper.jpg')
        self.assertRegex(self.connection.command_list[0], "output DP-3 bg \S*/tests/ExistingWallpaper.jpg fill")

        monitor.background('./tests/ExistingWallpaper.jpg', 'fill')
        self.assertRegex(self.connection.command_list[0], "output DP-3 bg \S*/tests/ExistingWallpaper.jpg fill")
