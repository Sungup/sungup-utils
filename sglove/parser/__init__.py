import argparse
import json
import os
import re
import sys

from sglove.parser.exception import *
from sglove.utils import classproperty


# ===========================
# String manipulate functions
# ===========================
__true_candidates = ['on', 'yes', 'y', 'true', 't', '1']
__false_candidates = ['off', 'no', 'n', 'false', 'f', '0', 'none']


def _to_bool(value):
    """
    Change object to boolean value.
    :param value: value to change boolean
    :return: True/False
    """
    # 1. Check value is string and change string to boolean
    if isinstance(value, str):
        value = value.strip().lower()

        if value in __true_candidates:
            return True

        elif value in __false_candidates:
            return False

    # 2. Check
    elif isinstance(value, bool) or value is None:
        return bool(value)

    raise SGLException(SGL_PARSER_ABNORMAL_BOOLEAN)


def _to_str(string):
    return str(string).strip() if string else ''


def _to_obj(value, type):
    if type is str:
        return _to_str(value)

    elif type is bool:
        return _to_bool(value)

    else:
        return type(value)


# ==========================================
# Option management class using env and file
# ==========================================
class _OptionManager:
    class __OptionName:
        """
        Reformatting class for OptionManager.
        """
        __REGEX_NAME = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]$')

        def __is_valid(self, name):
            return isinstance(name, str) and self.__REGEX_NAME.fullmatch(name)

        def __init__(self, name, sub=None, delimiter='_'):
            """
            Constructor

            :param name: Option name. If the option has two depth name,
                         group or category will use this field.
            :param sub: Optional sub name. If name has two depth name,
                        real variable name use this field.
            :param delimiter: Delimiter between name and sub.
            """
            if (not self.__is_valid(name)) \
                    or (sub and not self.__is_valid(sub)) \
                    or (delimiter not in '_-'):
                raise SGLException(SGL_PARSER_INVALID_NAME_FORMAT)

            if not sub:
                self.__name = name
            else:
                self.__name = '{name}{delimiter}{sub}'.format(
                    name=name, sub=sub, delimiter=delimiter
                )

        def upper_form(self):
            """
            Upper form name.

            :return: Upper case name. If name contain the hyphen,
                     that character will be changed to under bar.
            """
            return self.__name.upper().replace('-', '_')

        def arg_form(self):
            """
            Argument form name

            :return: Two hyphens prefix name. If name contains the under bar,
                     that character will be changed to hyphen.
            """
            return '--{}'.format(self.__name.replace('_', '-'))

        def dest_form(self):
            """
            Destination field form name

            :return: Simply return its name. If name contains the hyphen,
                     that character will be changed to under bar.
            """
            return self.__name.replace('-', '_')

    def __init__(self, name, environ=None):
        """
        Constructor

        :param name: Application name
        :param environ: User specified environ dictionary. If not specified it,
                        use system environment dictionary
        """

        if environ and not isinstance(environ, dict):
            raise SGLException(SGL_PARSER_UNEXPECTED_ENV_TYPE)

        self.__app_name = name
        self.__env_header = self.__OptionName(name).upper_form()
        self.__file_opts = None
        self.__environ = environ if environ else os.environ

    def dest_name(self, name, sub_name=None):
        """
        Get destination field form name.

        :param name: main name
        :param sub_name: sub optional name
        :return: new formed name to use in Namespace type object of argparse
        """
        return self.__OptionName(name, sub_name).dest_form()

    def env_name(self, name, sub_name=None):
        """
        Environment name.

        :param name: Main name
        :param sub_name: Sub optional name
        :return: Upper case name to use in system environment. To avoid system
                 corruption, all environment name has the upper case app name
                 as a prefix.
        """
        return '{}_{}'.format(self.__env_header,
                              self.__OptionName(name, sub_name).upper_form())

    def long_arg(self, name, sub_name=None):
        """
        Get long argument name

        :param name: Main name
        :param sub_name: Sub optional name
        :return: New formed name for program argument field
        """
        return self.__OptionName(name, sub_name).arg_form()

    def load(self, path):
        """
        Load configuration file. Configuration file must be consisted with the
        two depth dictionary JSON script file.

        :param path: Configuration file.
        """
        if not path or not os.path.exists(path):
            raise SGLException(SGL_PARSER_CONFIG_NOT_EXIST)

        with open(path, 'r') as f_in:
            self.__file_opts = json.load(f_in)

    def default_value(self, category, name, env=None, default=None, type=str):
        """
        Retrieve the default variable from the configuration file or
        environment.

        :param category: Configuration file's first depth category name.
        :param name: Configuration file's second depth variable name.
        :param env: Environment variable name.
        :param default: Default value if there is no value from file and env.
        :param type: Variable's type name
        :return: Default value from the configuration file or environment.
        """
        # 1. First check environment value.
        if not env:
            env = self.env_name(category, name)

        if env in self.__environ:
            return _to_obj(self.__environ.get(env), type)

        # 2. If there is no environment value, check __file_opts
        if self.__file_opts \
                and category in self.__file_opts \
                and name in self.__file_opts[category]:
            return _to_obj(self.__file_opts[category].get(name), type)

        # 3. If there is no values from file and env,
        #    return "default" as default value
        return _to_obj(default, type)


# =======================
# Argument action classes
# =======================
class _FileEnvAction(argparse.Action):
    def __init__(self, manager, category, name,
                 default=None,
                 type=str,
                 choices=None,
                 required=False,
                 **kwargs):

        if not isinstance(manager, _OptionManager):
            raise SGLException(SGL_PARSER_UNEXPECTED_MANAGER)

        if 'nargs' in kwargs and kwargs['nargs'] != 1:
            raise SGLException(SGL_PARSER_INVALID_PARSING_ARG,
                               'Nargs should be 1.')
        else:
            kwargs.pop('nargs', None)

        if 'const' in kwargs:
            raise SGLException(SGL_PARSER_INVALID_PARSING_ARG,
                               'Const cannot be supported.')

        # 1. Remove 'const' option because of the inversion-revoke case from
        #    env and file. If the value already selected from 'env' and 'file',
        #    users can't revoke to the default values from a single argument.
        #    Also if this action use this option reverting the 'env' or 'file'
        #    driven value not default, it can make confusions about the meaning
        #    of that arguments.
        #    Anyway FileEnvAction should have values in case about the store_*.
        #    (store_true, store_false, store_const, and so on.)
        kwargs.pop('const', None)

        default = manager.default_value(category, name,
                                        default=default, type=type)

        # Store type to convert from string to the wanted value type at the
        # parsing phase.
        self.__type = type

        if self.__type is bool:
            choices = None
            default = False if default is None else default

        # If already has default value, remove required field.
        if required and default is not None:
            required = False

        super(_FileEnvAction, self).__init__(nargs=None,
                                             const=None,
                                             default=default,
                                             type=str,
                                             choices=choices,
                                             required=required,
                                             **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, _to_obj(values, self.__type))


# ===========================
# Parse and its group classes
# ===========================
class _SGLParserBase:
    __RESERVED_KEYWORD = ['manager', 'category', 'dest']

    def __init__(self, parser, name, manager, reserved=None):
        if reserved and not isinstance(reserved, list):
            raise SGLException(SGL_PARSER_INTERNAL_ERROR)

        self.__manager = manager
        self.__parser = parser
        self.__category = name
        self.__arguments = reserved if reserved else []

    def _has_duplicate(self, name):
        return name in self.__arguments

    @classproperty
    def reserved_option_keywords(self):
        return self.__RESERVED_KEYWORD

    @property
    def _manager(self):
        return self.__manager

    def _add_argument_group(self, name, desc=None):
        return self.__parser.add_argument_group(name, desc)

    def _parse_args(self, args=None, namespace=None):
        return self.__parser.parse_args(args, namespace)

    def _parse_local(self, opts):
        return {
            name: opts.get(self.__manager.dest_name(self.__category, name))
            for name in self.__arguments
        }

    def add_argument(self, name, short=None, default=None, type=str, **kwargs):
        # 1. Check arguments

        # Manager, category and dest can't use for add_argument because of
        # the internal uses.
        for reserved in self.__RESERVED_KEYWORD:
            if reserved in kwargs:
                raise SGLException(SGL_PARSER_INVALID_PARSING_ARG)

        if self._has_duplicate(name):
            raise SGLException(SGL_PARSER_DUPLICATED_NAME)

        # 2. Add arguments
        short = '-{}'.format(short) if isinstance(short, str) else None
        long = self.__manager.long_arg(self.__category, name)

        args = [short, long] if short else [long]
        kwargs.update({
            'dest': self.__manager.dest_name(self.__category, name),
            'action': _FileEnvAction,
            'manager': self.__manager,
            'category': self.__category,
            'name': name,
            'default': default,
            'type': type
        })

        self.__parser.add_argument(*args, **kwargs)

        # 3. Register argument name in reserved field
        self.__arguments.append(name)


class _SGLGroup(_SGLParserBase):
    def __init__(self, parser, name, manager):
        super(_SGLGroup, self).__init__(parser=parser,
                                        name=name,
                                        manager=manager)

    def parse_group(self, opts):
        return self._parse_local(opts)


class SGLParser(_SGLParserBase):
    def __init__(self, app_name, default_config=None):
        parser = argparse.ArgumentParser()
        manager = _OptionManager(app_name)

        self.__groups = {}

        # 1. Append initial options for config file
        parser.add_argument(
            '-c', '--config',
            action='store', default=default_config, type=str, dest='config',
            help='Configuration file path for {}'.format(app_name)
        )

        # 2. Initial parser to get the config file path
        loading_args = sys.argv[1:]

        if '-h' in loading_args:
            loading_args.remove('-h')

        if '--help' in loading_args:
            loading_args.remove('--help')

        config_path = parser.parse_args(loading_args).config
        if config_path and os.path.exists(config_path):
            manager.load(config_path)

        super(SGLParser, self).__init__(parser=parser,
                                        name='core',
                                        manager=manager,
                                        reserved=['config'])

    def _has_duplicate(self, name):
        return super(SGLParser, self)._has_duplicate(name) \
               or name in self.__groups

    def add_argument_group(self, name, desc=None):
        if self._has_duplicate(name):
            raise SGLException(SGL_PARSER_DUPLICATED_NAME)

        group = _SGLGroup(self._add_argument_group(name, desc=desc),
                          name=name, manager=self._manager)

        self.__groups.update({name: group})

        return group

    def parse_args(self, args=None, namespace=None):
        # 1. Get 1 dimensional dictionary
        opts = vars(self._parse_args(args=args, namespace=namespace))

        # 2. Parse core arguments
        kwargs = self._parse_local(opts)

        # 3. Parse group arguments
        kwargs.update({
            name: argparse.Namespace(**group.parse_group(opts))
            for name, group in self.__groups.items()
        })

        # 4. Return re-constructed namespace
        return argparse.Namespace(**kwargs)
