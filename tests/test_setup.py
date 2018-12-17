import unittest
from sway_monitors import MonitorMode, Setup, Monitor
import json
import pprint

class FakeConnection:
    def __init__(self):
        self.command_list = []

    def command(self, command):
        self.command_list.append(command)

    def clear(self):
        self.command_list = []

    def get_outputs(self):
        with open('tests/setup.json') as f:
            data = json.loads(f.read())

        return data


class SetupTest(unittest.TestCase):
    def setUp(self):
        self.connection = FakeConnection()
        self.setup = Setup(connection=self.connection)

    def test_find_monitors(self):
        monitors = self.setup.find_monitors([{'model': 'DELL U2414H'}, {'model': 'DELL U2913WM', 'serial': 'HFDVR4Z0NIRM'}])
        self.assertEqual(len(monitors), 2)
        for monitor in monitors:
            self.assertIsInstance(monitor, Monitor)

    def test_find_monitor(self):
        self.assertIsInstance(self.setup.find_monitor({'model': 'DELL U2414H'}), Monitor)

        # Ambigious Monitor
        with self.assertRaises(Exception):
            self.setup.find_monitor({})

        # Non-existing Monitor
        with self.assertRaises(Exception):
            self.setup.find_monitor({'model': 'DELL U2414'})

    def test_is_connected(self):
        self.assertTrue(self.setup.is_connected({'model': 'DELL U2414H'}))
        #self.assertFalse(self.setup.is_connected({'model': 'DELL U2414'}))

    def test_check_setup(self):
        self.assertTrue(self.setup.check_setup([{'model': 'DELL U2414H'}, {'model':'DELL U2913WM', 'serial':'HFDVR4Z0NIRM'}]))
        self.assertFalse(self.setup.check_setup([{'model': 'DELL U2414'}, {'model':'DELL U2913WM'}]))

    # Big tests
    def test_enable(self):
        self.connection.clear()

        self.setup.enable([
            {'model': 'DELL U2414H'},
            {'model':'DELL U2913WM', 'serial':'HFDVR4Z0NIRM'}
        ])

        self.assertEqual(len(self.connection.command_list), 2)
        self.assertEqual(self.connection.command_list[0], "output DP-3 position 0 0 resolution 1920x1080")
        self.assertEqual(self.connection.command_list[1], "output DP-4 position 1920 0 resolution 2560x1080")


    def test_enable_reversed(self):
        self.connection.clear()

        self.setup.enable([
            {'model':'DELL U2913WM', 'serial':'HFDVR4Z0NIRM'},
            {'model': 'DELL U2414H'}
        ])

        self.assertEqual(len(self.connection.command_list), 2)
        self.assertEqual(self.connection.command_list[0], "output DP-4 position 0 0 resolution 2560x1080")
        self.assertEqual(self.connection.command_list[1], "output DP-3 position 2560 0 resolution 1920x1080")

    def test_enable_disable_monitor(self):
        self.connection.clear()

        self.setup.find_monitor({'model': 'DELL U2913WM', 'serial':'HFDVR4Z0NIRM'}).active = True
        self.setup.enable([
            {'model': 'DELL U2414H'}
        ])

        self.assertEqual(self.connection.command_list[0], "output DP-4 disable")
        self.assertEqual(self.connection.command_list[1], "output DP-3 position 0 0 resolution 1920x1080")


    def test_get_monitors(self):
        pass
