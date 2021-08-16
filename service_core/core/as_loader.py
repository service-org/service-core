#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from logging import getLogger
from importlib import import_module

from .as_helper import get_obj_string_repr

logger = getLogger(__name__)


def load_dot_path_colon_obj(dotted_path: t.Text, default: t.Any = None) -> t.Tuple[t.Optional[t.Text], t.Any]:
    """ 加载点分路径对象

    @param dotted_path: 点分路径
    @param default: 默认值
    @return: t.Tuple[t.Optional[t.Text], t.Any]
    """
    all_parts = dotted_path.split(':', 1)
    if len(all_parts) == 2:
        m_name, o_name = all_parts
    else:
        m_name, o_name = dotted_path, None
    # 是否存在导入对象?
    if o_name is None:
        errors = f'{dotted_path} ≠ <module>:<attribute>'
        return errors, default
    # 尝试导入模块对象?
    try:
        m_name = m_name[0:]
        module = import_module(m_name)
    except ImportError as e:
        logger.error(f'load {dotted_path}', exc_info=True)
        errors = get_obj_string_repr(e)
        return errors, default
    # 是否存在模块属性?
    if not hasattr(module, o_name):
        errors = f'{m_name} has not attr {o_name}'
        return errors, default
    # 存在模块以及属性!
    return None, getattr(module, o_name)
