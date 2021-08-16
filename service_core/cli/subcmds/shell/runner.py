#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import logging
import typing as t

from logging import getLogger
from service_core.core.as_helper import get_obj_string_repr

logger = getLogger(__name__)


class ShellRunner(object):
    """ 交互式的Shell生成类 """

    default_shell: t.Text = 'cpython'
    support_shell: t.Tuple[t.Text] = 'ipython', 'bpython', 'ptpython', default_shell

    def __init__(self, *, welcome: t.Optional[t.Text] = None, context: t.Optional[t.Dict] = None) -> None:
        """ 初始化实例

        @param welcome: 欢迎的信息
        @param context: 上下文信息
        """
        self.welcome = welcome or ''
        self.context = context or {}

    def ipython(self) -> None:
        """ 创建ipython交互式shell

        pip install -U ipython

        @return: None
        """
        from IPython import start_ipython as embed
        from traitlets.config.loader import Config

        logging.disable(logging.DEBUG)

        config = Config()
        params = ['--confirm-exit']
        print(f'IPython - {self.welcome}')
        config.TerminalInteractiveShell.banner1 = ''
        embed(argv=params, config=config, user_ns=self.context)

    def bpython(self) -> None:
        """ 创建bpython交互式shell

        pip install -U bpython

        @return: None
        """
        from bpython.curtsies import main as embed

        logging.disable(logging.DEBUG)

        params = ['--quiet']
        print(f'BPython - {self.welcome}')
        embed(args=params, banner='', locals_=self.context)

    def ptpython(self) -> None:
        """ 创建ptpython交互式shell

        pip install -U ptpython

        @return: None
        """
        from ptpython.repl import embed

        logging.disable(logging.DEBUG)

        print(f'PtPython - {self.welcome}')
        embed(title='', globals=self.context)

    def cpython(self) -> None:
        """ 创建python交互shell

        @return: None
        """
        from code import interact as embed

        logging.disable(logging.DEBUG)

        print(f'CPython - {self.welcome}')
        embed(banner='', local=self.context)

    def start(self, name: t.Optional[t.Text] = None) -> None:
        """ 启动一个指定的shell

        @param name: shell名称
        @return: None
        """
        embed, error = False, ''
        if name not in self.support_shell:
            available_shells = self.support_shell
        else:
            available_shells = (name,)
        for shell_name in available_shells:
            try:
                shell = getattr(self, shell_name)
                shell()
                embed = True
                break
            except Exception as e:
                error = get_obj_string_repr(e)
        not embed and logger.error(error, exc_info=True)
