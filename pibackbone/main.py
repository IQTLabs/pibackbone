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
from plumbum import FG  # pytype: disable=import-error
from plumbum import local  # pytype: disable=import-error
from plumbum import TF  # pytype: disable=import-error
from plumbum.cmd import docker_compose  # pytype: disable=import-error # pylint: disable=import-error
from plumbum.cmd import reboot  # pytype: disable=import-error # pylint: disable=import-error
from plumbum.cmd import sudo  # pytype: disable=import-error # pylint: disable=import-error
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

    def quit(self):
        """Reset the working directory and exit the program"""
        self.reset_cwd()
        sys.exit(1)

    @staticmethod
    def _check_conf_dir(conf_dir):
        """Check the conf directory is valid"""
        realpath = os.path.realpath(conf_dir)
        if not realpath.endswith('/pibackbone'):
            raise ValueError(
                f'last element of conf_dir must be pibackbone: {realpath}')
        for valid_prefix in ('/usr/local', '/opt', '/home', '/Users'):
            if realpath.startswith(valid_prefix):
                return realpath
        raise ValueError(f'conf_dir root may not be safe: {realpath}')

    def set_config_dir(self, conf_dir='/opt/pibackbone'):
        """Set the current working directory to where the configs are"""
        try:
            realpath = self._check_conf_dir(
                os.path.dirname(__file__).split('lib')[0] + conf_dir)
            os.chdir(realpath)
        except Exception as err:  # pragma: no cover
            logging.error(
                'Unable to find config files, exiting because: %s', err)
            self.quit()

    def reset_cwd(self):
        """Set the current working directory back to what it was originally"""
        os.chdir(self.previous_dir)

    def get_definitions(self):
        """Get definitions of services and projects"""
        with open('definitions.json', 'r') as file_handler:
            self.definitions = json.load(file_handler)
            self.services = self.definitions['services']
            self.projects = list(self.definitions['projects'])
            self.projects.append('None')

    def menu(self):
        """Drive the menu interface"""
        answer = self.execute_prompt(self.initial_question())
        if 'existing_project' in answer and answer['existing_project']:
            answer = self.execute_prompt(self.project_question())
        else:
            answer = self.execute_prompt(self.services_question())
        return answer

    @staticmethod
    def reboot_question():
        """Ask if they would like to reboot the machine"""
        return [
            {
                'type': 'confirm',
                'name': 'reboot_machine',
                'message': 'Do you want to reboot this machine now? (Recommended as some changes require a reboot to take effect)',
                'default': True,
            },
        ]

    def parse_answer(self, answer):
        """Parse out answer"""
        print(answer)
        services = []
        project = ""
        if 'project' in answer:
            if answer['project'] == 'None':
                logging.info("Nothing chosen, quitting.")
                self.quit()
            # TODO get services in project and add to list
            project = answer['project']
            print(self.definitions['projects'][answer['project']])
        elif 'services' in answer:
            if not answer['services']:
                logging.info("Nothing chosen, quitting.")
                self.quit()
            for service in answer['services']:
                services.append(service)
        else:
            logging.error('Invalid choices in answer: %s', answer)
            self.quit()
        return services, project

    def install_requirements(self, services):
        """Install requirements of choices made"""
        # TODO install things to config.txt
        pass

    def apply_secrets(self):
        """Set secret information specific to the deployment"""
        # TODO if s3, ask for aws creds
        # TODO for line in .env ask to apply a value
        pass

    def start_services(self):
        """Start services that were requested"""
        # TODO collect required compose files, and start with compose
        # TODO ask if you want watchtower to do automatic updates for you
        pass

    def output_notes(self):
        """Output any notes if a project was chosen and has notes"""
        pass

    @staticmethod
    def restart():
        """Restart the machine"""
        sudo[reboot]()

    def main(self):
        """Main entrypoint to the class, parse args and main program driver"""
        parser = argparse.ArgumentParser(prog='PiBackbone',
                                         description='PiBackbone - A tool for installing the basic required subsystems on a Pi-based project')
        # TODO add option to self update pibackbone
        parser.add_argument('--version', '-V', action='version',
                            version=f'%(prog)s {__version__}')
        args = parser.parse_args(self.raw_args)
        self.set_config_dir()
        self.get_definitions()
        services, project = self.parse_answer(self.menu())
        self.install_requirements(services)
        self.apply_secrets()
        self.start_services()
        if project:
            self.output_notes(project)
        self.reset_cwd()

        answer = self.execute_prompt(self.reboot_question())
        if 'reboot_machine' in answer and answer['reboot_machine']:
            self.restart()
