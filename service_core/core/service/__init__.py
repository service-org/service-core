#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from inspect import getmembers
from service_core.core.as_router import ApiRouter
from service_core.core.decorator import AsLazyProperty
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
        pass

    def __getattribute__(self, item: t.Text) -> t.Any:
        """ 协程安全的获取依赖对象

        解决协程竞争覆盖苏醒值问题

        @param item: 属性名称
        @return: t.Ant
        """
        green_local = self.container.green_local
        if hasattr(green_local, item): return getattr(green_local, item)
        return super(Service, self).__getattribute__(item)

    def include_router(self, router: ApiRouter) -> None:
        """ 加载汇总多文件中的路由

        主要用于创建大型多文件应用

        @param router: 路由实例
        @return: None
        """
        # 将子路由由下而上自动收集的路由信息注入到当前router_mapping
        self.router_mapping.update(router.data)

    @AsLazyProperty
    def router_mapping(self) -> t.Dict[t.Text, t.Callable[..., t.Any]]:
        """ 收集当前服务实例下路由

        主要用于创建小型单文件应用

        @return: t.Dict[t.Text, t.Callable]
        """
        from service_core.core.checking import is_entrypoint

        # 自动收集当前服务类下的所有可调用对象的entrypoints作为视图函数
        all_members = getmembers(self.__class__, is_entrypoint)
        return {name: obj for name, obj in all_members}
