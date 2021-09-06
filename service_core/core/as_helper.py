#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import uuid
import inspect
import typing as t

from logging import getLogger
from pydantic import ValidationError

logger = getLogger(__name__)


def get_obj_string_repr(obj: t.Any) -> t.Text:
    """ 获取对象字符串表示

    @param obj: 任意对象
    @return: t.Text
    """
    # 当对象为字符串对象
    obj_type = str
    if isinstance(obj, obj_type):
        return obj
    # 当对象为字节串对象
    obj_type = bytes
    if isinstance(obj, obj_type):
        return obj.decode('utf-8')
    # 当对象为验证异常时
    obj_type = ValidationError
    if isinstance(obj, obj_type):
        return obj.json()
    # 当对象为异常类对象
    obj_type = Exception
    if not isinstance(obj, obj_type):
        return repr(obj)
    # 当对象不含message
    if not hasattr(obj, 'message'):
        return repr(obj)
    # 防止类似requests库
    error = obj.message
    return get_obj_string_repr(error)


def gen_curr_primary_id() -> t.Text:
    """ 生成数据库的主键ID

    @return: t.Text
    """
    return str(uuid.uuid4())


def gen_curr_request_id() -> t.Text:
    """ 生成调用链此节点ID

    @return: t.Text
    """
    return uuid.uuid4().hex


def get_obj_dotted_path(obj: t.Any) -> t.Text:
    """ 获取对象的点分路径

    @param obj: 任意对象
    @return: t.Text
    """
    m = inspect.getmodule(obj)
    return m.__name__ if m else ''


def get_fun_dotted_path(obj: t.Callable[..., t.Any]) -> t.Text:
    """ 获取函数的点分路径

    @param obj: 任意对象
    @return: t.Text
    """
    return obj.__module__


def get_accessible_port() -> int:
    """ 获取随机可用的端口

    @return: int
    """
    from eventlet.green import socket

    args = (socket.AF_INET, socket.SOCK_STREAM)
    sock = socket.socket(*args)
    # bind端口0表示系统随机分配可用端口
    sock.bind(('', 0))
    return sock.getsockname()[1]


def get_accessible_host() -> t.Text:
    """ 获取当前可用的地址

    @return: t.Text
    """
    from eventlet import patcher
    from eventlet.green import socket

    hostname = socket.gethostname()
    # fix mac系统eventlet dnspython解析bug
    socket = patcher.original('socket')
    return socket.gethostbyname(hostname)
