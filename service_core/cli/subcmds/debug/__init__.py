#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import os
import sys

from telnetlib import Telnet
from logging import getLogger
from argparse import Namespace
from argparse import ArgumentParser
from service_core.cli.subcmds import BaseCommand
from service_core.core.configure import Configure

logger = getLogger(__name__)


class Debug(BaseCommand):
    """ 连接指定后门服务调试 """

    name = 'debug'
    help = 'remote debug with backdoor'
    desc = 'remote debug with backdoor'

    @classmethod
    def init_parser(cls, parser: ArgumentParser, config: Configure) -> None:
        """ 自定义子命令

        @param parser: 解析对象
        @param config: 配置字典
        @return: None
        """
        parser.add_argument('--host', action='store', default='127.0.0.1',
                            help='specify the backdoor server host')
        parser.add_argument('--port', action='store', required=True,
                            help='specify the backdoor server port')

    @classmethod
    def main(cls, namespace: Namespace, *, config: Configure) -> None:
        """ 子命令入口

        @param namespace: 命名空间
        @param config: 配置字典
        @return: None
        """
        host = namespace.host
        port = namespace.port
        client = Telnet(host, port)
        try:
            client.interact()
        except BaseException:
            pass
        sys.stdout.write(os.linesep)
        logger.debug(f'good by~')
