# -*- coding: utf-8 -*-
import json
import os
from os.path import expanduser


class Settings:
    def __init__(self):
        self._settings = {
            "program_path": "",
            "database_path": "",
        }
        self._home_dir = expanduser("~")

        self._path = self._home_dir + "/.config/examgen.json"

    def set_configuration_file(self, path):
        self._path = path

    def get_configuration_path(self):
        return self._path

    def load_config(self):
        try:
            with open(self._path, 'r') as fp:
                self._settings = json.load(fp)

        except FileNotFoundError as _:
            with open(self._path, 'w') as fp:
                json.dump(self._settings, fp)

        os.chmod(self._path, 0o755)

        if not self._settings['program_path']:
            _path = self._home_dir + "/ExamTool/"

            if not os.path.exists(_path):
                os.makedirs(_path)

            self._settings['program_path'] = _path

    def save_config(self):
        try:
            with open(self._path, 'w') as fp:
                json.dump(self._settings, fp)

        except ValueError:
            print('No configuration file exist')

    def get_program_path(self):
        return self._settings['program_path']

    def set_program_path(self, path):
        self._settings['program_path'] = path
        return True

    def get_database_path(self):
        return self._settings['database_path']

    def set_database_path(self, path):
        self._settings['database_path'] = path
        return True
