#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sys
import typing as t


class AsLazyProperty(object):
    """ 惰性计算修饰类

    https://docs.python.org/zh-cn/3.9/howto/descriptor.html
    """

    def __init__(self, func: t.Callable[..., t.Any]) -> None:
        """ 初始化实例

        @param func: 待修饰函数
        """
        self.func = func

    def __get__(self, instance: type, owner: t.Type[type]) -> t.Any:
        """ 获取指定属性的值

        @param instance: 被修饰类实例
        @param owner: 被修饰类
        @return: t.Any
        """
        n = self.func.__name__
        result = self.func(instance)
        setattr(instance, n, result)
        return getattr(instance, n)


class AsSingletonCls(object):
    """ 单例模式修饰类 """

    def __init__(self, klass: t.Type) -> None:
        """ 初始化实例

        @param klass: 待修饰类
        """
        self.klass = klass

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Type[type]:
        """ 调用时执行的方法

        @param args  : 位置参数
        @param kwargs: 命名参数
        @return: t.Type[type]
        """
        ident = '_instance'
        if hasattr(self.klass, ident):
            return getattr(self.klass, ident)
        else:
            result = self.klass(*args, **kwargs)
            setattr(self.klass, ident, result)
            return getattr(self.klass, ident)


class AsFriendlyFunc(object):
    """ 忽略异常修饰类 """

    def __init__(
            self,
            func: t.Callable,
            *,
            succ_callback: t.Optional[t.Callable] = None,
            fail_callback: t.Optional[t.Callable] = None,
            all_exception: t.Optional[t.Tuple] = None
    ) -> None:
        """ 初始化实例

        @param func: 原始函数
        @param succ_callback: 成功回调函数
        @param fail_callback: 失败回调函数
        @param all_exception: 要忽略的异常
        @return: ...
        """
        self.func = func
        self.succ_callback = succ_callback
        self.fail_callback = fail_callback
        self.all_exception = all_exception or (BaseException,)

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        """ 调用时执行的方法

        @param args  : 位置参数
        @param kwargs: 命名参数
        @return: t.Any
        """
        try:
            s = self.succ_callback
            result = self.func(*args, **kwargs)
            return s(result) if callable(s) else result
        except self.all_exception:
            f = self.fail_callback
            result = sys.exc_info()
            return f(result) if callable(f) else result
