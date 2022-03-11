"""
PiBackbone module for install the basic required subsystems on a Pi-based project
"""
import logging
import os


level_int = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20,
             'DEBUG': 10}
level = level_int.get(os.getenv('LOGLEVEL', 'INFO').upper(), 0)
logging.basicConfig(level=level)


class PiBackbone():
    """
    Main PiBackbone class for install the basic required subsystems on a Pi-based project
    """
    def __init__(self):
        pass

    def main(self):
        logging.info("running main")
        return
