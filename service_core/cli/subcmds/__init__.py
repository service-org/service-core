#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from argparse import Namespace
from argparse import ArgumentParser
from service_core.core.configure import Configure


class BaseCommand(object):
    """ 命令扩展基类 """

    # 子命令名称
    name: t.Text = ''
    # 子命令帮助
    help: t.Text = ''
    # 子命令描述
    desc: t.Text = ''

    @classmethod
    def init_parser(cls, parser: ArgumentParser, config: Configure) -> None:
        """ 自定义子命令

        @param parser: 解析对象
        @param config: 配置对象
        @return: None
        """
        pass

    @classmethod
    def main(cls, namespace: Namespace, *, config: Configure) -> None:
        """ 子命令入口

        @param namespace: 命名空间
        @param config: 配置对象
        @return: None
        """
        pass
