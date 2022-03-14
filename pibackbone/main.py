"""
PiBackbone module for install the basic required subsystems on a Pi-based project
"""
import argparse
import json
import logging
import os
import sys

#import docker
from examples import custom_style_2
#from plumbum import FG  # pytype: disable=import-error
#from plumbum import local  # pytype: disable=import-error
#from plumbum import TF  # pytype: disable=import-error
#from plumbum.cmd import docker_compose  # pytype: disable=import-error
from PyInquirer import prompt

from pibackbone import __file__
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
        self.previous_dir = os.getcwd()
        self.definitions = {}
        self.services = []
        self.projects = []

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

    def project_question(self):
        """Ask which project to start"""
        return [
            {
                'type': 'list',
                'name': 'project',
                'message': 'What project would you like to build?',
                'choices': self.projects,
                'filter': lambda val: val.lower(),
            },
        ]

    def services_question(self):
        """Ask which services to start"""
        service_choices = []
        for service in self.services:
            service_choices.append({'name': service})
        return [
            {
                'type': 'checkbox',
                'name': 'services',
                'message': 'What services would you like to start?',
                'choices': service_choices,
            },
        ]

    @staticmethod
    def _check_conf_dir(conf_dir):
        realpath = os.path.realpath(conf_dir)
        if not realpath.endswith('/pibackbone'):
            raise ValueError(
                'last element of conf_dir must be pibackbone: %s' % realpath)
        for valid_prefix in ('/usr/local', '/opt', '/home', '/Users'):
            if realpath.startswith(valid_prefix):
                return realpath
        raise ValueError('conf_dir root may not be safe: %s' % realpath)

    def set_config_dir(self, conf_dir='/opt/pibackbone'):
        """Set the current working directory to where the configs are"""
        try:
            realpath = self._check_conf_dir(
                os.path.dirname(__file__).split('lib')[0] + conf_dir)
            os.chdir(realpath)
        except Exception as err:  # pragma: no cover
            logging.error(
                'Unable to find config files, exiting because: %s', err)
            sys.exit(1)

    def reset_cwd(self):
        """Set the current working directory back to what it was originally"""
        os.chdir(self.previous_dir)

    def get_definitions(self):
        with open('definitions.json', 'r') as f:
            self.definitions = json.load(f)
            self.services = self.definitions['services']
            self.projects = list(self.definitions)
            self.projects.remove('services')
            self.projects.append('None')

    def menu(self):
        """Drive the menu interface"""
        answer = self.execute_prompt(self.initial_question())
        if 'existing_project' in answer and answer['existing_project']:
            answer = self.execute_prompt(self.project_question())
        else:
            answer = self.execute_prompt(self.services_question())

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
        # TODO do something with args
        self.set_config_dir()
        self.get_definitions()
        self.menu()
        self.reset_cwd()
