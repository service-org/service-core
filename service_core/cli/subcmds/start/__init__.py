#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import argparse

from logging import getLogger
from argparse import Namespace
from argparse import ArgumentParser
from service_core.cli.subcmds import BaseCommand
from service_core.core.configure import Configure

from .runner import ServiceRunner

logger = getLogger(__name__)


class Start(BaseCommand):
    """ 启动一个或多个服务  """

    name = 'start'
    help = 'start one or more service'
    desc = 'start one or more service'

    @classmethod
    def load_eventlet_monkey_patch(cls) -> None:
        """ 载入事件循环

        @return: None
        """
        import eventlet.debug

        # 打印hub的异常
        eventlet.debug.hub_exceptions()
        # 打印tpool异常
        eventlet.debug.tpool_exceptions(True)
        # 全局打猴子补丁
        eventlet.monkey_patch()

    @classmethod
    def init_parser(cls, parser: ArgumentParser, config: Configure) -> None:
        """ 自定义子命令

        @param parser: 解析对象
        @param config: 配置对象
        @return: None
        """
        parser.add_argument('services', nargs='+', metavar='module dotted_path',
                            help='one or more dot path service classes to run')
        parser.add_argument('--debug', action=argparse.BooleanOptionalAction,
                            help='inspect the state of a long-running process')

    @classmethod
    def main(cls, namespace: Namespace, *, config: Configure) -> None:
        """ 子命令入口

        @param namespace: 命名空间
        @param config: 配置对象
        @return: None
        """
        services = namespace.services
        cls.load_eventlet_monkey_patch()
        ServiceRunner(services, config, debugs=namespace.debug).start()
