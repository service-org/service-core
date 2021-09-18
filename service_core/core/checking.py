#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import inspect
import typing as t

from .service import Service
from .endpoint import Endpoint
from .service.extension import Extension
from .service.dependency import Dependency


def is_endpoint(obj: t.Any) -> bool:
    """ 是否为约定端点实例

    @param obj: 任意对象
    @return: bool
    """
    is_cls = inspect.isclass(obj)
    return is_cls and issubclass(obj, Endpoint)


def is_extension(obj: t.Any) -> bool:
    """ 是否是约定扩展实例

    @param obj: 任意对象
    @return: bool
    """
    return isinstance(obj, Extension)


def is_dependency(obj: t.Any) -> bool:
    """ 是否是约定依赖实例

    @param obj: 任意对象
    @return: bool
    """
    return isinstance(obj, Dependency)


def is_entrypoint(obj: t.Any) -> bool:
    """ 是否是约定入口实例

    @param obj: 任意对象
    @return: bool
    """
    # 1. 是否是可调用对象?
    can_call = callable(obj)
    # 2. 有entrypoints?
    was_regs = hasattr(obj, 'entrypoints')
    return can_call and was_regs


def is_service(obj: t.Any) -> bool:
    """ 是否是约定服务实例

    @param obj: 任意对象
    @return: bool
    """
    # 1. 是否是Service实例?
    was_ins = isinstance(obj, Service)
    # 2. 且至少存在一个路由?
    return was_ins and obj.router_mapping
