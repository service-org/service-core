#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from service_core.cli.subctxs import BaseContext
from service_core.core.configure import Configure


class Config(BaseContext):
    """ 用于查询配置文件内容 """

    name: t.Text = 'config'

    def __new__(cls, config: Configure) -> Configure:
        """ 创建配置实例

        @param config: 配置对象
        """
        return config

    def __init__(self, config: Configure) -> None:
        """ 初始化实例

        @param config: 配置对象
        """
        super(Config, self).__init__(config)
