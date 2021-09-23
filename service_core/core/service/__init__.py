#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from inspect import getmembers
from service_core.core.as_router import ApiRouter
from service_core.core.as_helper import get_accessible_host
from service_core.core.as_helper import get_accessible_port


class Service(object):
    """ 服务声明基类 """

    # 微服务名称
    name: t.Text = ''
    # 微服务描述
    desc: t.Text = ''
    # 微服务地址
    host: str = get_accessible_host()
    # 微服务端口
    port: int = get_accessible_port()

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """ 初始化实例

        @param args  : 位置参数
        @param kwargs: 命名参数
        """
        from service_core.core.checking import is_entrypoint

        all_members = getmembers(self, is_entrypoint)
        self.router_mapping = {name: obj for name, obj in all_members}

    def include_router(self, router: ApiRouter) -> None:
        """ 加载汇总多文件中的路由

        主要用于创建大型多文件应用

        @param router: 路由实例
        @return: None
        """
        # 将子路由由下而上自动收集的路由信息注入到当前router_mapping
        self.router_mapping.update(router.data)
