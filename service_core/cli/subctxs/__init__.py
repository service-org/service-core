#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from service_core.core.configure import Configure


class BaseContext(object):
    """ 上下文扩展基类 """

    # 上下文名称
    name: t.Text = ''

    def __init__(self, config: Configure) -> None:
        """ 初始化实例

        @param config: 配置对象
        """
        pass
