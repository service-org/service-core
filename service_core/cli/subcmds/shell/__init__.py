#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import os
import sys
import inspect
import builtins
import typing as t

from types import ModuleType
from logging import getLogger
from argparse import Namespace
from argparse import ArgumentParser
from service_core.cli.subctxs import BaseContext
from service_core.cli.subcmds import BaseCommand
from service_core.core.configure import Configure
from service_core.constants import CONTEXT_CONFIG_KEY
from service_core.constants import DEFAULT_CONTEXT_LOADED
from service_core.core.as_loader import load_dot_path_colon_obj

from .runner import ShellRunner

logger = getLogger(__name__)
Module = ModuleType('Service')

# 上下文列表类型
ContextList = t.List[t.Tuple[t.Text, t.Tuple[t.Optional[t.Text], t.Type[BaseContext]]]]


class Shell(BaseCommand):
    """ 启动一个交互式的Shell """

    name = 'shell'
    help = 'launch an interactive shell'
    desc = 'launch an interactive shell'

    @classmethod
    def load_subctx_from_conf(cls, conf: Configure) -> ContextList:
        """ 载入所有上下文

        @param conf: 配置字典
        @return: t.List
        """
        contexts = DEFAULT_CONTEXT_LOADED
        contexts.update(conf.get(CONTEXT_CONFIG_KEY, []))
        return [(c, load_dot_path_colon_obj(c)) for c in contexts]

    @classmethod
    def generate_init_context(cls, conf: Configure) -> t.Dict[t.Text, t.Any]:
        """ 生成默认上下文

        @param conf: 配置字典
        @return: t.Dict
        """
        sub_contexts = cls.load_subctx_from_conf(conf)
        for dotted_path, (error, context) in sub_contexts:
            context_obj = context(config=conf)
            error_prefix_message = f'load {dotted_path} fail,'
            if error is not None or context is None:
                logger.error(error_prefix_message + error)
                continue
            if not inspect.isclass(context):
                error = 'no subclass of BaseContext'
                logger.error(error_prefix_message + error)
                continue
            if not issubclass(context, BaseContext):
                error = 'no subclass of BaseContext'
                logger.error(error_prefix_message + error)
                continue
            logger.debug(f'load subctx {dotted_path} succ')
            setattr(Module, context.name, context_obj)
        return {'s': Module, '__builtins__': builtins}

    @classmethod
    def init_parser(cls, parser: ArgumentParser, config: Configure) -> None:
        """ 自定义子命令

        @param parser: 解析对象
        @param config: 配置字典
        @return: None
        """
        parser.add_argument('--shell', action='store',
                            choices=ShellRunner.support_shell,
                            help='specify an interactive shell')

    @classmethod
    def main(cls, namespace: Namespace, *, config: Configure) -> None:
        """ 子命令入口

        @param namespace: 命名空间
        @param config: 配置字典
        @return: None
        """
        shell_name = namespace.shell
        welcome = sys.version.replace(os.linesep, '')
        context = cls.generate_init_context(config)
        ShellRunner(welcome=welcome, context=context).start(shell_name)
