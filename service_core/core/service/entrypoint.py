#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from functools import partial

from .extension import Extension


class Entrypoint(Extension):
    """ 入口扩展基类 """

    def __init__(self, *args: t.Text, **kwargs: t.Text) -> None:
        """ 初始化实例

        @param exec_timing: 执行限时
        """
        super(Entrypoint, self).__init__(*args, **kwargs)
        # 支持设置协程的执行时间,防止协程长时间驻留导致内存溢出
        self.exec_timing = kwargs.get('exec_timing', None)

    def __repr__(self) -> t.Text:
        name = super(Entrypoint, self).__repr__()
        return f'{self.container.service.name}:{name}'

    @classmethod
    def as_decorators(cls, *args: t.Any, **kwargs: t.Any) -> t.Callable[..., t.Callable[..., t.Any]]:
        """ 挂载入口扩展装饰

        @param args  : 位置参数
        @param kwargs: 命名参数
        @return: t.Callable[..., t.Callable[..., t.Any]]
        """

        def register(cls_args: t.Tuple, cls_kwargs: t.Dict, func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
            """ 注册入口扩展

            @param cls_args  : 位置参数
            @param cls_kwargs: 命名参数
            @param func: 目标视图函数
            @return: t.Callable[..., t.Any]
            """
            entrypoint = cls(*cls_args, **cls_kwargs)
            entrypoints = getattr(func, 'entrypoints', set())
            entrypoints.add(entrypoint)
            # 将当前入口扩展实例注入到当前方法的entrypoints上
            setattr(func, 'entrypoints', entrypoints)
            return func

        # 支持带参数和不带参数的入口扩展用法
        no_params = len(args) == 1 and callable(args[0])
        return register((), {}, args[0]) if no_params else partial(register, args, kwargs)
