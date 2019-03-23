import json
import os
import uuid


def __project_home():
    return os.path.dirname(os.path.dirname(__file__))


def __project_subdir(path):
    return os.path.join(__project_home(), path)


def get_resource_file(path):
    return os.path.abspath(os.path.join(__project_subdir('tests/resources'), path))


def get_temp_file(path=None, ext=None):
    if not ext:
        ext = '.txt'

    if not path:
        path = '{name}.{ext}'.format(name=uuid.uuid4(), ext=ext)

    return os.path.abspath(os.path.join(__project_subdir('temp'), path))


class config_file:
    def __init__(self, options):
        if not isinstance(options, dict):
            raise Exception('Invalid configuration file')

        self.__temp = get_temp_file(ext='json')

        with open(self.__temp, 'w') as f_out:
            json.dump(options, f_out, indent=4)

    def __enter__(self):
        return self.__temp

    def __exit__(self, type, value, traceback):
        self.unlink()

    def __str__(self):
        return self.__temp

    @property
    def path(self):
        return self.__temp

    def unlink(self):
        if self.__temp:
            os.unlink(self.__temp)

            self.__temp = None
