#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t


class RemoteError(Exception):
    """ 微服务异常基类 """

    def __init__(self, errormsg: t.Optional[t.Text] = None, original: t.Optional[t.Text] = None) -> None:
        """ 初始化实例

        @param errormsg: 异常消息
        @param original: 消息源头
        """
        self.errormsg = errormsg or ''
        self.original = original or ''
        super(RemoteError, self).__init__(errormsg)

    def __repr__(self) -> t.Text:
        return f'{self.original} - {self.errormsg}' if self.original else self.errormsg


class ReachTiming(RemoteError):
    """ 任务已执行超时 """
    pass
