#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import os
import sys
import logging
import warnings
import logging.config

from service_core.core.configure import Configure
from service_core.constants import LOGGING_CONFIG_KEY
from service_core.constants import DEFAULT_LOGGING_LEVEL
from service_core.constants import DEFAULT_LOGGING_FORMAT

from .bugs import bugfix
from .adds import setup_yaml_env_parser
from .load import load_config_from_yaml, load_arguments_parser


def setup_logger_from_conf(conf: Configure) -> None:
    """ 加载logging的配置

    @param conf: 配置字典
    @return: None
    """
    default_config = {'level': DEFAULT_LOGGING_LEVEL, 'format': DEFAULT_LOGGING_FORMAT}
    logging_config = conf.get(LOGGING_CONFIG_KEY, {})
    logging_config and logging.config.dictConfig(logging_config)
    logging_config or logging.basicConfig(**default_config)


def main() -> None:
    """ 命令行管理入口函数

    @return: None
    """
    sys.path.insert(0, '.')
    warnings.warn(bugfix)
    # 扩展YAML - 可环境变量解析
    setup_yaml_env_parser()
    # 读取配置 - 从YAML读取配置
    path = os.path.join('.', 'config.yaml')
    data = load_config_from_yaml(path)
    conf = Configure(data=data)
    # 配置日志 - 配置全局日志器
    setup_logger_from_conf(conf)
    # 命令解析 - 解析命令行参数
    sup_parser = load_arguments_parser(conf)
    namespace = sup_parser.parse_args()
    has_matched = hasattr(namespace, 'main')
    has_matched and namespace.main(namespace)
    has_matched or sup_parser.print_help()
