#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import json

from argparse import Namespace
from argparse import ArgumentParser
from service_core.cli.subcmds import BaseCommand
from service_core.core.configure import Configure


class Config(BaseCommand):
    """ 打印解析渲染后的配置 """

    name = 'config'
    help = 'show rendered yaml config'
    desc = 'show rendered yaml config'

    @classmethod
    def init_parser(cls, parser: ArgumentParser, config: Configure) -> None:
        """ 自定义子命令

        @param parser: 解析对象
        @param config: 配置字典
        @return: None
        """
        pass

    @classmethod
    def main(cls, namespace: Namespace, *, config: Configure) -> None:
        """ 子命令入口

        @param namespace: 命名空间
        @param config: 配置字典
        @return: None
        """
        print(json.dumps(config.data, indent=4))
