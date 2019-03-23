from argparse import Namespace
from collections import defaultdict

from tests.parser import ParserTestCase

import os
import random

import tests.utils as utils

# Test target
from sglove.parser.exception import *
from sglove.parser import SGLParser, _OptionManager


class TestSGLParserBase(ParserTestCase):
    __TEST_COUNT = 300

    def __check_all_values(self, test_case, parsed, func):
        for category, values in test_case.items():
            for name, value in values.items():
                self.assertEqual(parsed[category][name], func(value))

    def __gen_test_inputs(self, test_case):
        manager = _OptionManager(self._APP_NAME)

        configs = defaultdict(dict)
        envs = []
        args = []

        for category, values in test_case.items():
            for name, value in values.items():
                # Environment value injection
                if value.is_env_choosable:
                    key = manager.env_name(category, name)
                    os.environ[key] = str(value.e_val)
                    envs.append(key)

                if value.is_file_choosable:
                    configs[category].update({name: value.f_val})

                if value.is_user_choosable:
                    args.append('{}={}'.format(manager.long_arg(category, name),
                                               value.u_val))

        del manager

        return utils.config_file(configs), envs, args

    @staticmethod
    def __cleanup(conf, envs):
        # Unlink test config file
        conf.unlink()

        # Unset the injected environment values.
        for key in envs:
            del os.environ[key]

    @staticmethod
    def __extract_namespace(namespace):
        return {
            c: {k: v for k, v in vars(s).items()}
            if isinstance(s, Namespace) else s
            for c, s in vars(namespace).items()
        }

    @staticmethod
    def __parser_load(parser, test_case):
        for category, values in test_case.items():
            group = parser.add_argument_group(category)

            for name, value in values.items():
                group.add_argument(name, default=value.default, type=value.type)

    def __test_duplicated_name(self, test_case, func):
        for k, v in test_case.items():
            with self.assertRaises(SGLException) as err:
                func(k, v)

            self.assertEqual(err.exception.code, SGL_PARSER_DUPLICATED_NAME)

    def __test_abnormal_kwargs(self, func):
        # 0. Build test case, for kwargs test generate only 1 argument set
        test_case = self._gen_random_common_inputs(1)

        # 1. Try add all argument options with
        for k, v in test_case.items():
            for key in SGLParser.reserved_option_keywords:
                with self.assertRaises(SGLException) as err:
                    # Don't care about the key's available values. SGLParser
                    # will generate exception before finally insert argument.
                    kwargs = {
                        'default': v.default,
                        'type': v.type,
                        key: self._gen_random_string()
                    }

                    func(k, **kwargs)

                self.assertEqual(err.exception.code,
                                 SGL_PARSER_INVALID_PARSING_ARG)

    def test_normal(self):
        # 0. Build test case
        test_case = self._gen_random_inputs(self.__TEST_COUNT, True)

        conf, envs, args = self.__gen_test_inputs(test_case)

        try:
            parser = SGLParser(self._APP_NAME, conf.path)

            # 1. Add argument group and values
            self.__parser_load(parser, test_case)

            # 2. Parse
            values = self.__extract_namespace(parser.parse_args(args))

            # 3. Check argument values
            self.__check_all_values(test_case, values, lambda v: v.expected)

        finally:
            self.__cleanup(conf, envs)

    def test_duplicated_name_in_parser(self):
        # 0. Build test case
        test_case = self._gen_random_common_inputs(self.__TEST_COUNT)

        parser = SGLParser(self._APP_NAME)

        # 1. Add argument group and values
        for k, v in test_case.items():
            # If true case, use k as the random values, and the other case
            # use as the group name.
            if random.choice([True, False]):
                parser.add_argument(k, default=v.default, type=v.type)
            else:
                parser.add_argument_group(k, desc=self._gen_random_string())

        # 2. Try add arguments using all values
        self.__test_duplicated_name(test_case,
                                    lambda n, _: parser.add_argument(n))

        # 3. Try add argument group using all values
        self.__test_duplicated_name(test_case,
                                    lambda n, _: parser.add_argument_group(n))

    def test_duplicated_name_in_group(self):
        # 0. Build test ase
        test_case = self._gen_random_common_inputs(self.__TEST_COUNT)

        parser = SGLParser(self._APP_NAME)

        group = parser.add_argument_group(self._gen_random_name(),
                                          self._gen_random_string())

        # 1. Add argument values
        for k, v in test_case.items():
            group.add_argument(k, default=v.default, type=v.type)

        # 2. Try add arguments using all values
        self.__test_duplicated_name(test_case,
                                    lambda n, _: group.add_argument(n))

    def test_abnormal_kwargs_in_parer(self):
        parser = SGLParser(self._APP_NAME)

        self.__test_abnormal_kwargs(
            lambda k, **kwargs: parser.add_argument(k, **kwargs)
        )

    def test_abnormal_kwargs_in_group(self):
        parser = SGLParser(self._APP_NAME)

        group = parser.add_argument_group(self._gen_random_name(),
                                          desc=self._gen_random_string())

        self.__test_abnormal_kwargs(
            lambda k, **kwargs: group.add_argument(k, **kwargs)
        )
