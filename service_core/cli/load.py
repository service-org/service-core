#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import yaml
import inspect
import typing as t

from functools import partial
from logging import getLogger
from argparse import ArgumentParser
from pkg_resources import get_distribution
from service_core.core.configure import Configure
from service_core.constants import COMMAND_CONFIG_KEY
from service_core.constants import DEFAULT_COMMAND_LOADED
from service_core.core.as_loader import load_dot_path_colon_obj

from .subcmds import BaseCommand

logger = getLogger(__name__)
version = get_distribution('service_core').version

# 子命令列表类型
CommandList = t.List[t.Tuple[t.Text, t.Tuple[t.Optional[t.Text], t.Type[BaseCommand]]]]


def load_config_from_yaml(path: t.Text) -> t.Dict[t.Text, t.Any]:
    """ 从YAML读取配置

    @param path: 文件路径
    @return: t.Dict
    """
    return yaml.unsafe_load(open(path)) or {}


def load_subcmd_from_conf(conf: Configure) -> CommandList:
    """ 加载所有子命令

    @param conf: 配置字典
    @return: t.List
    """
    commands = DEFAULT_COMMAND_LOADED
    commands.update(conf.get(COMMAND_CONFIG_KEY, []))
    return [(c, load_dot_path_colon_obj(c)) for c in commands]


def load_arguments_parser(conf: Configure) -> ArgumentParser:
    """ 加载参数解析器

    @param conf: 配置字典
    @return: ArgParser
    """
    command_line_parser = ArgumentParser()
    command_line_parser.add_argument('--version',
                                     action='version',
                                     version=version)
    sub_parsers = command_line_parser.add_subparsers()
    sub_commands = load_subcmd_from_conf(conf)
    for dotted_path, (error, command) in sub_commands:
        error_prefix_message = f'load {dotted_path} fail,'
        if error is not None or command is None:
            logger.error(error_prefix_message + error)
            continue
        if not inspect.isclass(command):
            err = 'no subclass of BaseCommand'
            logger.error(error_prefix_message + err)
            continue
        if not issubclass(command, BaseCommand):
            err = 'no subclass of BaseCommand'
            logger.error(error_prefix_message + err)
            continue
        logger.debug(f'load subcmd {dotted_path} succ')
        name, help, desc = (
            command.name, command.help, command.desc
        )
        cur_parser = sub_parsers.add_parser(
            name, help=help, description=desc
        )
        # 提供自定义扩展子命令参数或下级命令能力
        command.init_parser(cur_parser, config=conf)
        sub_runner = partial(command.main, config=conf)
        cur_parser.set_defaults(main=sub_runner)
    return command_line_parser
