#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from .exception import RemoteError
from .core.as_helper import get_obj_dotted_path
from .core.as_helper import get_obj_string_repr


def gen_exception_description(exception: Exception) -> t.Dict:
    """ 将异常对象转为字典描述

    @param exception: 异常实例
    @return: t.Dict
    """
    exc_type = exception.__class__.__name__
    exc_path = get_obj_dotted_path(exception)
    exc_errs = get_obj_string_repr(exception)
    # 用于定位服务调用链异常源头
    original = getattr(exception, 'original', '')
    return {
        'original': original,
        'exc_type': exc_type,
        'exc_path': exc_path,
        'exc_errs': exc_errs,
    }


def gen_exception_from_result(dict_data: t.Dict) -> Exception:
    """ 从请求结果还原异常对象

    @param dict_data: 字典数据
    @return: Exception
    """
    exc_original = dict_data['original']
    exc_cls_name = dict_data['exc_type']
    exc_cls_type = type(exc_cls_name, (RemoteError,), {})
    exc_cls_errs = dict_data['exc_errs']
    return exc_cls_type(exc_cls_errs, original=exc_original)
