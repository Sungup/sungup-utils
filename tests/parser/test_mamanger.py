import os
import re
import string

from collections import namedtuple, defaultdict
from tests import utils
from tests.parser import ParserTestCase

from sglove.parser.exception import *
from sglove.parser import _OptionManager


class TestOptionManager(ParserTestCase):
    __TEST_COUNT = 50

    def __test_invalid_naming(self, str_func, str_list):
        manager = _OptionManager(self._APP_NAME)
        name_t = namedtuple('name_t', ('name', 'sub'))

        for _ in range(self.__TEST_COUNT):
            invalid_strings = [str_func(c) for c in str_list]

            # 1. Try constructor's name format check
            for case in invalid_strings:
                with self.assertRaises(SGLException) as err:
                    _OptionManager(case)

                self.assertEqual(err.exception.code,
                                 SGL_PARSER_INVALID_NAME_FORMAT)

            # 2. Try each member function's name format check
            valid = self._gen_random_string()

            test_case = [
                (name_t(invalid, valid), name_t(valid, invalid))
                for invalid in invalid_strings
            ]

            for case in [v for sub in test_case for v in sub]:
                for func in (manager.dest_name,
                             manager.env_name,
                             manager.long_arg):
                    with self.assertRaises(SGLException) as err:
                        func(case.name, case.sub)

                    self.assertEqual(err.exception.code,
                                     SGL_PARSER_INVALID_NAME_FORMAT)

    def test_invalid_naming(self):
        # 1. Contain invalid characters
        punctuation = re.sub(r'[_\-]', '', string.punctuation)
        self.__test_invalid_naming(lambda c: self._gen_random_string(middle=c),
                                   punctuation)

        # 2. Consisted with valid character but not started with alphabet
        invalid_first = string.digits + '_-'
        self.__test_invalid_naming(lambda c: self._gen_random_string(prefix=c),
                                   invalid_first)

        # 3. Not ended with alphabet and numbers
        invalid_last = '_-'
        self.__test_invalid_naming(lambda c: self._gen_random_string(suffix=c),
                                   invalid_last)

    def test_valid_naming(self):
        manager = _OptionManager(self._APP_NAME)
        test_case = {self._gen_random_string(): self._gen_random_string()
                     for _ in range(self.__TEST_COUNT)}

        for k, v in test_case.items():
            self.assertEqual(manager.env_name(k, v), self._to_env_name(k, v))
            self.assertEqual(manager.long_arg(k, v), self._to_arg_name(k, v))
            self.assertEqual(manager.dest_name(k, v), self._to_dest_name(k, v))

    def test_invalid_initialization(self):
        # 1. Enter invalid type.
        with self.assertRaises(SGLException) as err:
            _OptionManager(self._APP_NAME, [self._APP_NAME])

        self.assertEqual(err.exception.code, SGL_PARSER_UNEXPECTED_ENV_TYPE)

        # 2. Enter dict converted os.environ as environ target
        _OptionManager(self._APP_NAME, dict(os.environ))

    def test_invalid_loading(self):
        manager = _OptionManager(self._APP_NAME)

        with self.assertRaises(SGLException) as err:
            manager.load(utils.get_temp_file('invalid_path'))

        self.assertEqual(err.exception.code, SGL_PARSER_CONFIG_NOT_EXIST)

    def test_normal(self):
        test_options = self._gen_random_inputs(self.__TEST_COUNT)

        # This is the temporal manager to call the env_name().
        manager = _OptionManager(self._APP_NAME)

        env_dict = {}
        conf_dict = defaultdict(dict)

        for category, values in test_options.items():
            for name, value in values.items():
                if value.is_env_choosable:
                    env_dict.update({
                        manager.env_name(category, name): str(value.e_val)
                    })

                if value.is_file_choosable:
                    conf_dict[category].update({name: value.f_val})

        del manager

        # Run normal valid test
        with utils.config_file(conf_dict) as temp_file:
            manager = _OptionManager(self._APP_NAME, environ=env_dict)

            manager.load(temp_file)

            for category, values in test_options.items():
                for name, value in values.items():
                    default = manager.default_value(category, name,
                                                    default=value.default,
                                                    type=value.type)

                    self.assertEqual(default, value.expected)
