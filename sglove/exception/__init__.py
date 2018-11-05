from collections import namedtuple

import inspect

__ErrorCode = namedtuple('__ErrorCode', ['no', 'desc'])


class SGLException(Exception):
    @staticmethod
    def __caller_info():
        # 0. Get grand parent name from this function
        p_frame = inspect.currentframe().f_back
        if not p_frame or not p_frame.f_back:
            return ''

        gp_frame = p_frame.f_back
        del p_frame

        names = []
        line_no = gp_frame.f_lineno

        # 2. Get module name if that exists.
        module = inspect.getmodule(gp_frame)
        if module:
            names.append(module.__name__)

        # 3. Get class name if that exists.
        if 'self' in gp_frame.f_locals:
            names.append(gp_frame.f_locals['self'].__class__.__name__)

        # 4. Get caller function name if that exists.
        code_name = gp_frame.f_code.co_name
        if code_name != '<module>':
            names.append(code_name)

        # 5. Clean-up used frame information
        del gp_frame

        return line_no, '.'.join(names)

    def __init__(self, code, *args, **kwargs):
        line_no, caller = self.__caller_info()

        self.__code = code
        self.__message = '{} ({}:L#{})'.format(code.desc, caller, line_no)

        super(self.__class__, self).__init__(self.__message, *args, **kwargs)

    @property
    def code(self):
        return self.__code
