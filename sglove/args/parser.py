from collections import namedtuple
from sglove.args.exception import *

import abc
import re


class __ArgumentCore(abc.ABC):
    __RESERVED_ARGS = [
        'config'
    ]

    __UNSUPPORTED_ACTION = [
        'append', 'append_const', 'store_const'
    ]

    @abc.abstractmethod
    def add_argument(self, name, short, **kwargs):
        pass

    def _is_reserved(self, name):
        return name in self.__RESERVED_ARGS

    def _has_unsupported_action(self, kwargs):
        return 'action' in kwargs and \
               kwargs['action'] in self.__UNSUPPORTED_ACTION


class ArgumentGroup(__ArgumentCore):
    __ENV_HEADER = 'SGL'
    __REGEX_LONG_NAME = r'^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$'
    __REGEX_SHORT_NAME = r'^[a-zA-Z0-9]$'

    __OptItem = namedtuple('__OptItem', ['arg', 'env', 'default', 'type'])

    #
    # Private methods
    #
    def __arg_name(self, name):
        return '{0}_{1}'.format(self.__name, name)

    def __env_name(self, name):
        return '{0}_{1}_{2}'.format(self.__header, self.__name, name).upper()

    def __long_name(self, name):
        return '--{}'.format(self.__arg_name(name).replace('_', '-'))

    @staticmethod
    def __short_name(name):
        return '-{}'.format(name)

    @staticmethod
    def __update_action(kwargs):
        if 'action' not in kwargs:
            kwargs.update({'action': 'store'})

            if 'type' not in kwargs:
                kwargs.update({'type': str})

        else:
            '''
            store_true and store_false store only true and false value not null.
            Checking the argument value has been inserted from CLI, change the
            action from store_true/false to store_const. For this case, set the
            true/false value into 'const' kwargs.
            '''
            if kwargs['action'] in ['store_true', 'store_false']:
                kwargs.update({
                    'action': 'store_const',
                    'const': kwargs['action'] == 'store_true',
                })

            elif kwargs['action'] == 'count':
                pass

            elif 'type' not in kwargs:
                kwargs.update({'type': str})

    @staticmethod
    def __arg_type(kwargs):
        return kwargs.get('type',
                          bool if kwargs['action'] == 'store_const' else int)

    #
    # Constructor
    #
    def __init__(self, name, parser, env_header=__ENV_HEADER):
        if not re.fullmatch(self.__REGEX_LONG_NAME, name):
            raise SGLException(SGL_ARGS_ERR_INVALID_NAME_FORMAT)

        self.__parser = parser

        self.__name = name
        self.__header = env_header

        self.__args = dict()

    #
    # Public methods
    #
    @property
    def name(self):
        return self.__name

    def add_argument(self, name, short=None, **kwargs):
        # 1. Check valid name format
        if not re.fullmatch(self.__REGEX_LONG_NAME, name):
            raise SGLException(SGL_ARGS_ERR_INVALID_NAME_FORMAT)

        if short and not re.fullmatch(self.__REGEX_SHORT_NAME, short):
            raise SGLException(SGL_ARGS_ERR_INVALID_SHORT_NAME)

        if self._is_reserved(name):
            raise SGLException(SGL_ARGS_ERR_RESERVED_NAME)

        # 2. Check invalid kwargs
        if 'dest' in kwargs:
            raise SGLException(SGL_ARGS_ERR_INVALID_ARG_OPTS)

        if self._has_unsupported_action(kwargs):
            raise SGLException(SGL_ARGS_ERR_UNSUPPORTED_ACTION)

        try:
            _kwargs = kwargs.copy()

            self.__update_action(_kwargs)

            # 1. Get argument name
            _arg_name = self.__arg_name(name)

            _kwargs.update({'dest': _arg_name})

            # 2. Extract default value from kwargs
            _default = None

            if 'default' in _kwargs:
                _default = _kwargs.get('default', None)
                del _kwargs['default']

            # 3. Register argument in __parser and __args
            if short:
                self.__parser.add_argument(self.__short_name(short),
                                           self.__long_name(name),
                                           **_kwargs)
            else:
                self.__parser.add_argument(self.__long_name(name),
                                           **_kwargs)

            self.__args.update({
                name: self.__OptItem(self.__env_name(name), _arg_name,
                                     _default, self.__arg_type(_kwargs))
            })

        except Exception as exc:
            raise SGLException(SGL_ARGS_ERR_INVALID_ARG_OPTS) from exc
