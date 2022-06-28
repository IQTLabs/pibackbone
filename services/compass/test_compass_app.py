import sys

import fake_rpi

sys.modules['smbus2'] = fake_rpi.smbus
from campass_app import Heading


def test_compass_heading():
    heading = Heading()
    heading.get_heading()
