"""
PiBackbone module for install the basic required subsystems on a Pi-based project
"""
import argparse
import logging
import os

import docker
from examples import custom_style_2
from plumbum import FG  # pytype: disable=import-error
from plumbum import local  # pytype: disable=import-error
from plumbum import TF  # pytype: disable=import-error
from plumbum.cmd import docker_compose  # pytype: disable=import-error
from PyInquirer import prompt

from pibackbone import __version__


level_int = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20,
             'DEBUG': 10}
level = level_int.get(os.getenv('LOGLEVEL', 'INFO').upper(), 0)
logging.basicConfig(level=level)


class PiBackbone():
    """
    Main PiBackbone class for install the basic required subsystems on a Pi-based project
    """
    def __init__(self, raw_args=None):
        self.raw_args = raw_args

    @staticmethod
    def execute_prompt(questions):
        """
        Run end user prompt with supplied questions and return the selected
        answers
        """
        answers = prompt(questions, style=custom_style_2)
        return answers

    @staticmethod
    def initial_question():
        """Ask which if starting a project"""
        return [
            {
                'type': 'confirm',
                'name': 'existing_project',
                'message': 'Do you want to run a pre-existing project?',
                'default': False,
            },
        ]

    @staticmethod
    def project_question():
        """Ask which project to start"""
        return [
            {
                'type': 'list',
                'name': 'project',
                'message': 'What project would you like to start?',
                'choices': ['PiBuoy'],
                'filter': lambda val: val.lower(),
            },
        ]

    @staticmethod
    def core_question():
        """Ask which core services to start"""
        return [
            {
                'type': 'checkbox',
                'name': 'core_services',
                'message': 'What core services would you like to start?',
                'choices': [
                    {'name': 'PiJuice',
                     'checked': True},
                    {'name': 'Sense HAT',
                     'checked': True},
                ],
            },
        ]

    def main(self):
        """Main entrypoint to the class, parse args and main program driver"""
        parser = argparse.ArgumentParser(prog='PiBackbone',
                                         description='PiBackbone - A tool for installing the basic required subsystems on a Pi-based project')
        # TODO set log level
        parser.add_argument('--verbose', '-v', choices=[
                            'DEBUG', 'INFO', 'WARNING', 'ERROR'],
                            default='INFO',
                            help='logging level (default=INFO)')
        parser.add_argument('--version', '-V', action='version',
                            version=f'%(prog)s {__version__}')
        args = parser.parse_args(self.raw_args)
        answer = self.execute_prompt(self.initial_question())
        if 'existing_project' in answer and answer['existing_project']:
            answer = self.execute_prompt(self.project_question())
        else:
            answer = self.execute_prompt(self.core_question())
