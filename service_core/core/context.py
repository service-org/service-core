#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from service_core.core.as_helper import gen_curr_request_id

from .service import Service
from .decorator import AsLazyProperty
from .service.entrypoint import Entrypoint


class WorkerContext(object):
    """ 工作协程上下文类 """

    def __init__(
            self,
            service: Service,
            entrypoint: Entrypoint,
            *,
            args: t.Optional[t.Sequence] = None,
            kwargs: t.Optional[t.Dict] = None,
            context: t.Optional[t.Dict] = None
    ) -> None:
        """ 初始化实例

        @param service: 当前服务实例
        @param entrypoint: 入口扩展
        @param args  : 扩展的位置参数
        @param kwargs: 扩展的命名参数
        @param context: 上下文, 字典
        """
        self.original_service = service

        if isinstance(kwargs, dict):
            self.original_kwargs = kwargs
        else:
            self.original_kwargs = {}
        if isinstance(args, (tuple, list)):
            self.original_args = args
        else:
            self.original_args = ()
        if isinstance(context, dict):
            self.original_context = context
        else:
            self.original_context = {}

        self.original_entrypoint = entrypoint

    @AsLazyProperty
    def worker_request_id(self) -> t.Text:
        """ 服务调用 - 当前请求ID

        @return: t.Text
        """
        return gen_curr_request_id()

    @AsLazyProperty
    def origin_request_id(self) -> t.Text:
        """ 服务调用 - 源头请求ID

        @return: t.Text
        """
        name, default = 'origin_request_id', self.worker_request_id
        return self.original_context.get(name, default)

    @AsLazyProperty
    def parent_request_id(self) -> t.Text:
        """ 服务调用 - 父级请求ID

        @return: t.Text
        """
        name, default = 'worker_request_id', None
        return self.original_context.get(name, default)

    @AsLazyProperty
    def data(self) -> t.Dict[t.Text, t.Optional[t.Text]]:
        """ 当前服务节点的上下文

        @return: t.Dict[t.Text, t.Optional[t.Text]]
        """
        data = self.original_context.copy()
        return data | {
            'worker_request_id': self.worker_request_id,
            'origin_request_id': self.origin_request_id,
            'parent_request_id': self.parent_request_id,
        }
