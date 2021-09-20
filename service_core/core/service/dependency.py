#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from service_core.core.context import WorkerContext

from .extension import Extension


class Dependency(Extension):
    """ 依赖扩展基类 """

    def __init__(self, *args: t.Text, **kwargs: t.Any) -> None:
        """ 初始化实例

        @param skip_inject: 跳过注入
        @param once_inject: 注入一次
        @param skip_loaded: 跳过加载
        """
        super(Dependency, self).__init__(*args, **kwargs)
        self.skip_inject = kwargs.get('skip_inject', False)
        self.once_inject = kwargs.get('once_inject', True)
        self.skip_loaded = kwargs.get('skip_loaded', False)

    def __repr__(self) -> t.Text:
        name = super(Dependency, self).__repr__()
        return f'{self.container.service.name}:{name}'

    def get_instance(self, context: WorkerContext) -> t.Any:
        """ 获取注入对象

        @param context: 上下文对象
        @return: t.Any
        """
        current_instance = self
        return current_instance

    def worker_setups(self, context: WorkerContext) -> None:
        """ 工作协程 - 载入回调

        @param context: 上下文对象
        @return: None
        """
        pass

    def worker_result(self, context: WorkerContext, results: t.Any) -> None:
        """ 工作协程 - 正常回调

        @param context: 上下文对象
        @param results: 执行结果
        @return: None
        """
        pass

    def worker_errors(self, context: WorkerContext, excinfo: t.Any) -> None:
        """ 工作协程 - 异常回调

        @param context: 上下文对象
        @param excinfo: 异常对象
        @return: None
        """
        pass

    def worker_finish(self, context: WorkerContext) -> None:
        """ 工作协程 - 完毕回调

        @param context: 上下文对象
        @return: None
        """
        pass
