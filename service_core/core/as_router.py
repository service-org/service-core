#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from functools import partial
from logging import getLogger
from inspect import getmembers
from service_core.core.as_helper import get_fun_dotted_path

logger = getLogger(__name__)


class ApiRouter(object):
    """ 收集视图函数路由类 """

    def __init__(self, name: t.Text) -> None:
        """ 初始化实例

        router = ApiRouter(__name__)

        @router()
        def view_function(self, ...):
            pass

        @param name: 路由名称, 推荐__name__
        """
        self.data = {}
        self.name = name.rsplit('.')[-1]

    def include_router(self, router: ApiRouter) -> None:
        """ 包含子路由

        @param router: 路由实例
        @return: None
        """
        r = router.data.items()
        self.data.update({f'{self.name}.{k}': v for k, v in r})

        # 垃圾回收器标注下级路由失效
        del router

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Callable[..., t.Callable[..., t.Any]]:
        """ 注册装饰器

        @param args  : 命名参数
        @param kwargs: 命名参数
        @return: t.Callable[..., t.Callable[..., t.Any]]
        """

        def handle(cls_args: t.Tuple, cls_kwargs: t.Dict, func: t.Callable[..., t.Any]) -> None:
            """ 装饰器注册

            @param cls_args  : 命名参数
            @param cls_kwargs: 位置参数
            @param func: 修饰的函数或类
            @return: None
            """
            from .checking import is_endpoint
            from .checking import is_entrypoint

            if is_endpoint(func):
                inst = func()
                data = {f'{self.name}.{func.__name__}.{e[0]}': e[1] for e in getmembers(inst, is_entrypoint)}
                self.data.update(data)
            elif is_entrypoint(func):
                ident = f'{self.name}.{func.__name__}'
                self.data[ident] = func
            else:
                dotted_path = get_fun_dotted_path(func)
                ident = f'{dotted_path}.{func.__name__}'
                warns = f'{ident} no entrypoints found'
                logger.warning(warns)

        # 支持带参数和不带参数的入口装饰用法
        no_params = len(args) == 1 and callable(args[0])
        return handle((), {}, args[0]) if no_params else partial(handle, args, kwargs)
