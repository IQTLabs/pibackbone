
import sys
import fake_rpi

sys.modules['smbus2'] = fake_rpi.smbus
from compass_app import QMC5883L, MMC5883MA, argument_parser


def test_argument_parser():
    argument_parser()


def test_qmc5883L():
    compass = QMC5883L(declination=0)
    compass.get_heading(calibration=0)


def test_mma5883ma():
    compass = MMC5883MA(declination=0)
    compass.get_heading(calibration=0)
