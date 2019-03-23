from sglove.exception import SGLException, __ErrorCode


SGL_PARSER_UNEXPECTED_MANAGER = __ErrorCode(1, 'Unexpected manager type.')
SGL_PARSER_INVALID_NAME_FORMAT = __ErrorCode(2, 'Invalid name format.')
SGL_PARSER_CONFIG_NOT_EXIST = __ErrorCode(3, 'Config file does not exist.')
SGL_PARSER_UNEXPECTED_ENV_TYPE = __ErrorCode(4, 'Unexpected user defined environment type.')
SGL_PARSER_ABNORMAL_BOOLEAN = __ErrorCode(5, 'Invalid boolean word.')
SGL_PARSER_INVALID_PARSING_ARG = __ErrorCode(6, 'Invalid parsing argument.')
SGL_PARSER_DUPLICATED_NAME = __ErrorCode(7, 'Duplicated argument name.')
SGL_PARSER_INTERNAL_ERROR = __ErrorCode(8, 'Internal module error.')
