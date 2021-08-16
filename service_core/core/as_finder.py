#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from functools import partial
from logging import getLogger
from inspect import getmembers
from importlib import import_module

from .service import Service
from .checking import is_service
from .as_helper import get_obj_string_repr
from .as_loader import load_dot_path_colon_obj

logger = getLogger(__name__)


def find_declare_services(dotted_path: t.Text) -> t.Tuple[t.Optional[t.Text], t.List[Service]]:
    """ 获取声明的所有服务

    @param dotted_path: 点分路径
    @return: t.Tuple
    """
    all_parts = dotted_path.split(':', 1)
    # 是否是合法导入路径?
    if len(all_parts) == 2:
        m_name, o_name = all_parts
    else:
        m_name, o_name = dotted_path, None
    # 是否存在可导入对象?
    if o_name is not None:
        errors, obj = load_dot_path_colon_obj(dotted_path)
        return errors, [obj] if is_service(obj) else []
    # 尝试按路径导入模块!
    try:
        module = import_module(m_name)
    except ImportError as e:
        logger.error(f'load {dotted_path}', exc_info=True)
        errors = get_obj_string_repr(e)
        return errors, []
    # 读取模块中服务对象!
    find = partial(getmembers, predicate=is_service)
    return None, [obj for _, obj in find(module)]
