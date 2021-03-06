#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from inspect import getmembers


class Endpoint(object):
    """ 通过端点类托管视图 """

    def router_mapping(self) -> t.Dict[t.Text, t.Callable[..., t.Any]]:
        """ 收集当前端点实例下路由

        主要用于支持基于类的视图

        @return: t.Dict[t.Text, t.Callable[..., t.Any]]
        """
        from .checking import is_entrypoint

        all_mapping = {}
        all_members = getmembers(self, is_entrypoint)
        class_name = self.__class__.__name__
        for method_name, method in all_members:
            module_name = method.__module__.rsplit('.', 1)[-1]
            name = f'{module_name}.{class_name}.{method_name}'
            all_mapping.update({name: method})
        return all_mapping
