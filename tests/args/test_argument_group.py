from sglove.args.parser import ArgumentGroup
from sglove.args.exception import *

import argparse
import unittest


class TestArgumentGroup(unittest.TestCase):
    __ARG_TITLE = 'test'

    def __make_default_arg_group(self):
        # TODO Change argparse to sglove.args.parser.ArgumentParser
        _parser = argparse.ArgumentParser()
        _group = ArgumentGroup(
            self.__ARG_TITLE,
            _parser.add_argument_group(self.__ARG_TITLE.capitalize())
        )

        return _parser, _group

    def __opt_name(self, name):
        return '{}_{}'.format(self.__ARG_TITLE, name)

    def test_invalid_initializing(self):
        _INVALID_TEST_CASE = [
            '',            # Empty string
            'a',           # Single character
            '0Test_Case',  # Start with number
            '#Test_Case',  # Start with symbol
            'Test#Case',   # Invalid symbol 1
            'Test-Case',   # Invalid symbol 2
            'TestCase#',   # Invalid tail character 1
            'TestCase-',   # Invalid tail character 2
        ]

        _parser = argparse.ArgumentParser()

        for item in _INVALID_TEST_CASE:
            with self.assertRaises(SGLException) as error:
                _group = ArgumentGroup(item, _parser)

            self.assertEqual(error.exception.code,
                             SGL_ARGS_ERR_INVALID_NAME_FORMAT)

    def test_invalid_long_name(self):
        _INVALID_TEST_CASE = [
            '',            # Empty string
            'a',           # Single character
            '0Test_Case',  # Start with number
            '#Test_Case',  # Start with symbol
            'Test#Case',   # Invalid symbol 1
            'Test-Case',   # Invalid symbol 2
            'TestCase#',   # Invalid tail character 1
            'TestCase-',   # Invalid tail character 2
        ]

        _parser, _group = self.__make_default_arg_group()

        for item in _INVALID_TEST_CASE:
            with self.assertRaises(SGLException) as error:
                _group.add_argument(item)

            self.assertEqual(error.exception.code,
                             SGL_ARGS_ERR_INVALID_NAME_FORMAT)

    def test_invalid_short_name(self):
        _INVALID_TEST_CASE = [
            ('INVALID_SHORT_TWO_CHAR', 'AA'),  # Two character short name
            ('INVALID_SHORT_SYMBOL', '#'),     # Symbol character short name
        ]

        _parser, _group = self.__make_default_arg_group()

        for long, short in _INVALID_TEST_CASE:
            with self.assertRaises(SGLException) as error:
                _group.add_argument(long, short)

            self.assertEqual(error.exception.code,
                             SGL_ARGS_ERR_INVALID_SHORT_NAME)

    def test_invalid_arg_opts(self):
        _parser, _group = self.__make_default_arg_group()

        with self.assertRaises(SGLException) as error:
            _group.add_argument('valid_name', dest='invalid_dest')

        self.assertEqual(error.exception.code,
                         SGL_ARGS_ERR_INVALID_ARG_OPTS)

    def test_invalid_actions(self):
        _INVALID_TEST_CASE = [
            ('INVALID_APPEND_ARGS', {'action': 'append'}),
            ('INVALID_CONST_APPEND_ARGS', {'action': 'append_const'}),
            ('INVALID_CONST_ARGS', {'action': 'store_const'}),
        ]

        _parser, _group = self.__make_default_arg_group()

        for long, action in _INVALID_TEST_CASE:
            with self.assertRaises(SGLException) as error:
                _group.add_argument(long, **action)

            self.assertEqual(error.exception.code,
                             SGL_ARGS_ERR_UNSUPPORTED_ACTION)

    def test_valid_names(self):
        _VALID_TEST_CASE = [
            # Upper long and short name
            ('CASE_A', 'A', {'type': int, 'default': 1}),

            # Lower long and short name
            ('case_b', 'b', {'type': float, 'default': 1.1}),

            # Mixed long and number short name
            ('cAsE_c', 'C', {'type': str, 'default': '1E'}),

            ('cAsE_d', '0', {'action': 'store_true'}),

            # Two character long and empty short name
            ('cE',     '',  {'action': 'store_false'}),

            ('cF',     '',  {'action': 'count'})
        ]

        _parser, _group = self.__make_default_arg_group()

        for long, short, kwargs in _VALID_TEST_CASE:
            _group.add_argument(long, short, **kwargs)

        values = vars(_parser.parse_args())

        for long, short, _ in _VALID_TEST_CASE:
            name = self.__opt_name(long)

            self.assertIn(name, values)
            self.assertIsNone(values[name])

        # TODO Add value checking logic
        print(_parser.parse_args())
        print(_parser.parse_args(['-0', '--test-cE', '-A', '100',
                                  '--test-case-b', '100.0', '-C', '100E',
                                  '--test-cF', '--test-cF']))
