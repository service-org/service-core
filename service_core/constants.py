#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import logging

# 工作协程数
WORKERS_CONFIG_KEY = 'WORKERS'
DEFAULT_WORKERS_NUMBER = 65535

# 上下文配置
CONTEXT_CONFIG_KEY = 'CONTEXT'
DEFAULT_CONTEXT_LOADED = {
    'service_core.cli.subctxs.config:Config',
}

# 子命令配置
COMMAND_CONFIG_KEY = 'COMMAND'
DEFAULT_COMMAND_LOADED = {
    'service_core.cli.subcmds.start:Start',
    'service_core.cli.subcmds.shell:Shell',
    'service_core.cli.subcmds.debug:Debug',
    'service_core.cli.subcmds.config:Config'
}

# 日志的配置
LOGGING_CONFIG_KEY = 'LOGGING'
DEFAULT_LOGGING_LEVEL = logging.DEBUG
DEFAULT_LOGGING_FORMAT = '%(asctime)s - %(process)d - %(levelname)s - %(message)s'
