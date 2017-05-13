import unittest

from utils import from_bokeh_timestamp, to_bokeh_timestamp


class test_bokeh_timestamp(unittest.TestCase):
    timestamp = 730101212300
    new_date = from_bokeh_timestamp(730101212300, time_unit="milliseconds")
    new_timestamp = to_bokeh_timestamp(new_date, time_unit="milliseconds")

    def test_bokeh_timestamp(self):
        self.assertEqual(self.timestamp, self.new_timestamp)


if __name__ == '__main__':
    unittest.main()
