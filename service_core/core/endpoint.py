#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from inspect import getmembers

from .decorator import AsLazyProperty


class Endpoint(object):
    """ 通过端点类托管视图 """

    @AsLazyProperty
    def router_mapping(self) -> t.Dict[t.Text, t.Callable[..., t.Any]]:
        """ 收集当前端点类下的路由

        主要用于支持基于类的视图

        @return: t.Dict[t.Text, t.Callable[..., t.Any]]
        """
        from .checking import is_entrypoint

        # 自动收集端点类下的所有存在entrypoints的可调用对象作为视图函数
        all_members = getmembers(self.__class__, is_entrypoint)
        return {name: obj for name, obj in all_members}
