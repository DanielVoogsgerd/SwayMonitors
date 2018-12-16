import unittest
from sway_monitors import MonitorMode


class MonitorModeTest(unittest.TestCase):
    def setUp(self):
        self.smallSlowMode = MonitorMode({'width': 1920, 'height': 1080, 'refresh': 30000})
        self.smallFastMode = MonitorMode({'width': 1920, 'height': 1080, 'refresh': 60000})
        self.largeSlowMode = MonitorMode({'width': 2560, 'height': 1440, 'refresh': 30000})
        self.largeFastMode = MonitorMode({'width': 2560, 'height': 1440, 'refresh': 60000})

        self.orderedModes = [self.smallSlowMode, self.smallFastMode, self.largeSlowMode, self.largeFastMode]
        self.unorderedModes = [self.largeSlowMode, self.smallFastMode, self.smallSlowMode, self.largeFastMode]

    def test_only_width(self):
        with self.assertRaises(Exception):
            MonitorMode({'width': 1920})

    def test_only_height(self):
        with self.assertRaises(Exception):
            MonitorMode({'height': 1080})

    def test_only_refresh(self):
        with self.assertRaises(Exception):
            MonitorMode({'refresh': 60000})


    def test_no_width(self):
        with self.assertRaises(Exception):
            MonitorMode({'height': 1080, 'refresh': 60000})

    def test_no_height(self):
        with self.assertRaises(Exception):
            MonitorMode({'width': 1920, 'refresh': 60000})

    def test_no_refresh(self):
        with self.assertRaises(Exception):
            MonitorMode({'width': 1920, 'height': 1080})

    def test_dimensions(self):
        self.assertEqual(self.smallSlowMode.get_dimensions(), (1920, 1080))

    def test_has_dimensions(self):
        self.assertTrue(self.smallSlowMode.has_dimensions({'width': 1920, 'height': 1080}))
        self.assertFalse(self.smallSlowMode.has_dimensions({'width': 1920, 'height': 1200}))

    # Magic methods tests
    def test_greater(self):
        self.assertGreater(self.smallFastMode, self.smallSlowMode)
        self.assertGreater(self.largeSlowMode, self.smallFastMode)
        self.assertGreater(self.largeFastMode, self.largeSlowMode)

    def test_less(self):
        self.assertLess(self.smallSlowMode, self.smallFastMode)
        self.assertLess(self.smallFastMode, self.largeSlowMode)
        self.assertLess(self.largeSlowMode, self.largeFastMode)

    def test_greater_equal(self):
        self.assertGreaterEqual(self.smallFastMode, self.smallSlowMode)
        self.assertGreaterEqual(self.largeSlowMode, self.smallFastMode)
        self.assertGreaterEqual(self.largeFastMode, self.largeSlowMode)

        self.assertGreaterEqual(self.largeFastMode, self.largeFastMode)

    def test_smaller_equal(self):
        self.assertLessEqual(self.smallSlowMode, self.smallFastMode)
        self.assertLessEqual(self.smallFastMode, self.largeSlowMode)
        self.assertLessEqual(self.largeSlowMode, self.largeFastMode)

        self.assertLessEqual(self.largeFastMode, self.largeFastMode)

    def test_equal(self):
        self.assertEqual(self.smallFastMode, self.smallFastMode)

    def test_not_equal(self):
        self.assertNotEqual(self.smallFastMode, self.smallSlowMode)
        self.assertNotEqual(self.largeSlowMode, self.smallSlowMode)

    def test_sorted(self):
        self.assertEqual(sorted(self.unorderedModes), self.orderedModes)

    def test_min(self):
        self.assertEqual(min(self.unorderedModes), self.smallSlowMode)

    def test_max(self):
        self.assertEqual(max(self.unorderedModes), self.largeFastMode)
