import argparse

from collections import defaultdict

from tests import utils
from tests.parser import ParserTestCase
from sglove.parser.exception import *
from sglove.parser import _OptionManager, _FileEnvAction


class TestFileEnvAction(ParserTestCase):
    __TEST_COUNT = 50

    @staticmethod
    def __build_parser(manager, test_case):
        parser = argparse.ArgumentParser()

        for category, values in test_case.items():
            for name, value in values.items():
                parser.add_argument(manager.long_arg(category, name),
                                    dest=manager.dest_name(category, name),
                                    action=_FileEnvAction,
                                    manager=manager,
                                    category=category,
                                    name=name,
                                    default=value.default,
                                    type=value.type)

        return parser

    def __check_all_values(self, manager, test_case, func, args=None):
        opts = vars(self.__build_parser(manager, test_case).parse_args(args))

        for category, values in test_case.items():
            for name, value in values.items():
                self.assertEqual(opts.get(manager.dest_name(category, name)),
                                 func(value))

    def test_abnormal_action(self):
        manager = _OptionManager(self._APP_NAME)
        parser = argparse.ArgumentParser()

        category = self._gen_random_string()
        name = self._gen_random_string()

        # 1. Try invalid manager
        with self.assertRaises(SGLException) as err:
            parser.add_argument(self._gen_random_string(),
                                action=_FileEnvAction,
                                manager=None,
                                category=category,
                                name=name)

        self.assertEqual(err.exception.code,
                         SGL_PARSER_UNEXPECTED_MANAGER)

        # 2. Use invalid nargs
        for nargs in ['*', '?', '+', argparse.REMAINDER, 2]:
            opt_strings = [self._gen_random_string(),
                           self._to_arg_name(self._gen_random_string())]

            for opt in opt_strings:
                with self.assertRaises(SGLException) as err:
                    parser.add_argument(opt,
                                        action=_FileEnvAction,
                                        manager=manager,
                                        category=category,
                                        name=name,
                                        nargs=nargs)

                self.assertEqual(err.exception.code,
                                 SGL_PARSER_INVALID_PARSING_ARG)

        # 3. Use const option
        for _, item in self._gen_random_inputs(1).popitem()[-1].items():
            opt_strings = [self._gen_random_string(),
                           self._to_arg_name(self._gen_random_string())]

            for opt in opt_strings:
                with self.assertRaises(SGLException) as err:
                    parser.add_argument(opt,
                                        action=_FileEnvAction,
                                        manager=manager,
                                        category=category,
                                        name=name,
                                        const=item.u_val)

                self.assertEqual(err.exception.code,
                                 SGL_PARSER_INVALID_PARSING_ARG)

    def test_default_value_action(self):
        manager = _OptionManager(self._APP_NAME)

        test_case = self._gen_random_inputs(self.__TEST_COUNT, False)

        self.__check_all_values(manager, test_case,
                                lambda value: value.default)

    def test_env_value_action(self):
        manager = _OptionManager(self._APP_NAME)

        test_case = self._gen_random_inputs(self.__TEST_COUNT, False)

        environs = {
            manager.env_name(category, name): str(value.e_val)
            for category, values in test_case.items()
            for name, value in values.items()
        }

        del manager

        manager = _OptionManager(self._APP_NAME, environ=environs)

        self.__check_all_values(manager, test_case,
                                lambda value: value.e_val)

    def test_file_value_action(self):
        manager = _OptionManager(self._APP_NAME)

        test_case = self._gen_random_inputs(self.__TEST_COUNT, False)

        configs = {
            category: {name: value.f_val for name, value in values.items()}
            for category, values in test_case.items()
        }

        with utils.config_file(configs) as temp_file:
            manager.load(temp_file)

            self.__check_all_values(manager, test_case,
                                    lambda value: value.f_val)

    def test_user_value_action(self):
        manager = _OptionManager(self._APP_NAME)

        test_case = self._gen_random_inputs(self.__TEST_COUNT, True)

        args = [
            '{}={}'.format(manager.long_arg(category, name), value.u_val)
            for category, values in test_case.items()
            for name, value in values.items()
        ]

        self.__check_all_values(manager, test_case,
                                lambda value: value.u_val, args)

    def test_random_normal(self):
        manager = _OptionManager(self._APP_NAME)

        test_case = self._gen_random_inputs(self.__TEST_COUNT, True)

        environs = {}
        configs = defaultdict(dict)
        args = []

        for category, values in test_case.items():
            for name, value in values.items():
                if value.is_env_choosable:
                    environs.update({
                        manager.env_name(category, name): str(value.e_val)
                    })

                if value.is_file_choosable:
                    configs[category].update({name: value.f_val})

                if value.is_user_choosable:
                    args.append('{}={}'.format(manager.long_arg(category, name),
                                               value.u_val))

        del manager

        with utils.config_file(configs) as temp_file:
            manager = _OptionManager(self._APP_NAME, environ=environs)
            manager.load(temp_file)

            self.__check_all_values(manager, test_case,
                                    lambda v: v.expected, args)
