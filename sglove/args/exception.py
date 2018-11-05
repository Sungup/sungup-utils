from sglove.exception import SGLException, __ErrorCode


SGL_ARGS_ERR_INVALID_SHORT_NAME = __ErrorCode(1, 'Invalid short name format.')
SGL_ARGS_ERR_INVALID_NAME_FORMAT = __ErrorCode(2, 'Invalid name format.')
SGL_ARGS_ERR_RESERVED_NAME = __ErrorCode(3, 'Reserved argument name.')
SGL_ARGS_ERR_INVALID_ARG_OPTS = __ErrorCode(4, 'Invalid argument options.')
SGL_ARGS_ERR_UNSUPPORTED_ACTION = __ErrorCode(5, 'Unsupported argument action.')
