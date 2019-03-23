import random
import string
import unittest


class ParserTestItem:
    DEF = 0
    FILE = 1
    ENV = 2
    USER = 3

    def __init__(self, type, default, f_val, e_val, u_val=None):
        self.__type = type
        self.__default = default
        self.__f_val = f_val
        self.__e_val = e_val
        self.__u_val = u_val

        self.__selected = random.randint(0, 2 if not u_val else 3)

        if self.__selected == self.FILE:
            self.__expected = f_val
        elif self.__selected == self.ENV:
            self.__expected = e_val
        elif self.__selected == self.USER:
            self.__expected = u_val
        else:
            self.__expected = default

    def __str__(self):
        return "{}/{}/{}/{} - {}:{}".format(self.__default, self.__f_val,
                                            self.__e_val, self.__u_val,
                                            self.selected, self.expected)

    def __is_choosable(self, val):
        return self.__selected == val \
               or (self.__selected > val and random.choice([True, False]))

    @property
    def is_env_choosable(self):
        return self.__is_choosable(self.ENV)

    @property
    def is_file_choosable(self):
        return self.__is_choosable(self.FILE)

    @property
    def is_user_choosable(self):
        return self.__is_choosable(self.USER)

    @property
    def expected(self):
        return self.__expected

    @property
    def default(self):
        return self.__default

    @property
    def f_val(self):
        return self.__f_val

    @property
    def e_val(self):
        return self.__e_val

    @property
    def u_val(self):
        return self.__u_val

    @property
    def type(self):
        return self.__type

    @property
    def selected(self):
        if self.__selected == self.USER:
            return "User"
        elif self.__selected == self.ENV:
            return "Environ"
        elif self.__selected == self.FILE:
            return "File"
        else:
            return "Default"


class ParserTestCase(unittest.TestCase):
    _APP_NAME = 'TEST'

    @staticmethod
    def __gen_random_case(use_uval=False):
        # 1. String Options
        u_val = ParserTestCase._gen_random_string() if use_uval else None
        s_case = ParserTestItem(str,
                                ParserTestCase._gen_random_string(),
                                ParserTestCase._gen_random_string(),
                                ParserTestCase._gen_random_string(),
                                u_val)

        # 2. Integer option
        u_val = random.randint(300, 399) if use_uval else None
        i_case = ParserTestItem(int,
                                random.randint(0, 99),
                                random.randint(100, 199),
                                random.randint(200, 299),
                                u_val)

        # 3. Float option
        u_val = random.uniform(30, 39) if use_uval else None
        f_case = ParserTestItem(float,
                                random.uniform(0, 9),
                                random.uniform(10, 19),
                                random.uniform(20, 29),
                                u_val)

        # 4. Boolean option
        u_val = random.choice([True, False]) if use_uval else None
        b_case = ParserTestItem(bool,
                                random.choice([True, False]),
                                random.choice([True, False]),
                                random.choice([True, False]),
                                u_val)

        return s_case, i_case, f_case, b_case

    # Test utility functions for OptionManager
    @staticmethod
    def _gen_random_string(prefix='', suffix='', middle='', delimiter='_-'):
        start = prefix + random.choice(string.ascii_letters)
        end = random.choice(string.ascii_letters + string.digits) + suffix

        string_set = string.ascii_letters + string.digits + delimiter
        begin_half = ''.join(random.choices(string_set, k=5))
        last_half = ''.join(random.choices(string_set, k=5))

        return start + begin_half + middle + last_half + end

    @staticmethod
    def _gen_random_name(prefix='', suffix='', middle=''):
        return ParserTestCase._gen_random_string(prefix, suffix, middle, '_')

    @staticmethod
    def _to_env_name(name, sub_name=None):
        if sub_name:
            name = '{}_{}'.format(name, sub_name)

        name = '{}_{}'.format(ParserTestCase._APP_NAME, name)

        return name.replace('-', '_').upper()

    @staticmethod
    def _to_dest_name(name, sub_name=None):
        if sub_name:
            return '{}_{}'.format(name, sub_name).replace('-', '_')

        else:
            return name.replace('-', '_')

    @staticmethod
    def _to_arg_name(name, sub_name=None):
        if sub_name:
            return '--{}-{}'.format(name, sub_name).replace('_', '-')

        else:
            return '--{}'.format(name.replace('_', '-'))

    @staticmethod
    def _gen_random_inputs(count, use_uval=False):
        test_options = {}

        # Build test items
        for _ in range(count):
            s_case, i_case, f_case, b_case = \
                ParserTestCase.__gen_random_case(use_uval)

            test_options.update({
                ParserTestCase._gen_random_name(): {
                    ParserTestCase._gen_random_name(): s_case,
                    ParserTestCase._gen_random_name(): i_case,
                    ParserTestCase._gen_random_name(): f_case,
                    ParserTestCase._gen_random_name(): b_case,
                }
            })

        return test_options

    @staticmethod
    def _gen_random_common_inputs(count, use_uval=False):
        test_options = {}

        # Build test items
        for _ in range(count):
            s_case, i_case, f_case, b_case = \
                ParserTestCase.__gen_random_case(use_uval)

            test_options.update({
                ParserTestCase._gen_random_name(): s_case,
                ParserTestCase._gen_random_name(): i_case,
                ParserTestCase._gen_random_name(): f_case,
                ParserTestCase._gen_random_name(): b_case,
            })

        return test_options
