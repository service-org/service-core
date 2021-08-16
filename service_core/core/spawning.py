#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from eventlet import GreenPool


class SpawningProxy(object):
    """ 协程并发处理类 """

    def __init__(self, items: t.Sized, ignore_results: bool = True) -> None:
        """ 初始化实例

        @param items: 存在__len__属性的对象
        @param ignore_results: 是否忽略执行结果?
        """
        self.items = items
        self.ignore_results = ignore_results

    def __getattr__(self, attr: t.Text) -> t.Callable[..., t.Optional[t.List]]:
        """ 获取属性值

        SpawningProxy(...).setup()
        SpawningProxy(...).start()

        @param attr: 属性名称
        @return: t.Callable[..., t.Optional[t.List]]
        """

        def handle(*args: t.Any, **kwargs: t.Any) -> t.Optional[t.List]:
            """ 调用属性时执行的函数

            @param args  : 位置参数
            @param kwargs: 命名参数
            @return: t.Optional[t.List]
            """
            results = None
            # 防止items为空导致size=0时pool被阻塞
            if not self.items:
                return results
            else:
                results = []
            pool = GreenPool(size=len(self.items))

            def process(item: t.Any) -> t.Any:
                """ 每个协程执行的函数

                @param item: items每个对象
                @return: t.Any
                """
                func = getattr(item, attr)
                return func(*args, **kwargs)

            for result in pool.imap(process, self.items):
                if not self.ignore_results:
                    continue
                results.append(result)
            else:
                results = results or None
            return results

        return handle
