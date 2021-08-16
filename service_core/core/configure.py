#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t


class Configure(object):
    """ 配置管理类 """

    def __init__(self, data: t.Optional[t.Dict] = None) -> None:
        """ 初始化实例

        config = Configure({'a': {'b': {'c': 'C'}}})
        print(config.get('a.b.c', default=None))

        @param data: 配置字典
        """
        self.data = data or {}

    def __getitem__(self, item: t.Text) -> t.Any:
        """ 获取指定属性值

        @param item: 属性名称
        @return: t.Any
        """
        return self.get(item, raise_exception=True)

    def get(self, item: t.Text, default: t.Optional[t.Any] = None, raise_exception: bool = False) -> t.Any:
        """ 获取指定属性值

        @param item: 属性名称
        @param default: 属性不存在时默认值
        @param raise_exception: 是否抛异常
        @return: t.Any
        """
        result = self.data
        # 支持以点号分割递归读取属性值
        dotted_attrs = item.split('.')
        for attr in dotted_attrs:
            if attr in result:
                result = result[attr]
                continue
            if raise_exception:
                raise KeyError(item)
            return default
        return result
