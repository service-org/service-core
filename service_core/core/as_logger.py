#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import time
import logging
import typing as t

from logging import Logger
from datetime import timedelta

from .as_helper import get_obj_string_repr


def as_timing_logger(logger: Logger, level: t.Optional[int] = None) -> t.Callable[..., t.Generator]:
    """ 生成耗时日志logger

    @param logger: 日志对象
    @param level: 默认日志级别
    @return: t.Callable
    """

    level = level or logging.DEBUG

    def handle(msg: t.Text, *args: t.Any) -> t.Generator:
        """ 作为日志记录生成器

        @param msg : 日志消息
        @param args: 位置参数
        @return: None
        """
        # fix log某些非字符串对象时%s的bug
        msg = get_obj_string_repr(msg)
        msg = msg.replace('%', r'%%')
        start = time.time()
        yield  # 首先记录当前时间, next(...)
        msg = f'{msg} in %s'
        duration = time.time() - start
        duration = timedelta(seconds=duration)
        args += (str(duration),)
        logger.log(level, msg, *args)
        yield  # 然后记录执行时间, next(...)

    return handle
