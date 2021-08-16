#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    # 防止存在相互引用
    from service_core.core.container import ServiceContainer


class Extension(object):
    """ 服务扩展基类 """

    # 扩展名称
    name: t.Text = ''

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """ 初始化实例

        @param args  : 位置参数
        @param kwargs: 命名参数
        """
        # 用于指向实际的服务容器
        self.container = None
        # 用于存储属性或方法名称
        self.object_name = None

    def __repr__(self) -> t.Text:
        name = self.name if self.name else self.__class__.__name__
        return f'{self.object_name}:{name}' if name else self.object_name

    def bind(self, container: ServiceContainer, name: t.Text) -> Extension:
        """ 绑定容器和对象名称

        @param container: 容器对象
        @param name: 扩展名称
        @return: Extension
        """
        # 绑定当前函数或属性名
        self.object_name = name
        # 绑定当前实际服务容器
        self.container = container

        current_instance = self
        return current_instance

    def setup(self) -> None:
        """ 生命周期 - 载入阶段

        @return: None
        """
        pass

    def start(self) -> None:
        """ 生命周期 - 启动阶段

        @return: None
        """
        pass

    def stop(self) -> None:
        """ 生命周期 - 关闭阶段

        @return: None
        """
        pass

    def kill(self) -> None:
        """ 生命周期 - 强杀阶段

        @return: None
        """
        pass


class StoreExtension(object):
    """ 存储扩展基类 """

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """ 初始化实例

        @param args  : 位置参数
        @param kwargs: 命名参数
        """
        super(StoreExtension, self).__init__(*args, **kwargs)
        self.all_extensions = set()

    def reg_extension(self, extension: Extension) -> None:
        """ 注册指定扩展

        @param extension: 扩展对象
        @return: None
        """
        self.all_extensions.add(extension)

    def del_extension(self, extension: Extension) -> None:
        """ 删除指定扩展

        @param extension: 扩展对象
        @return: None
        """
        self.all_extensions.discard(extension)


class ShareExtension(object):
    """ 共享扩展基类 """

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """ 初始化实例

        @param args  : 位置参数
        @param kwargs: 命名参数
        """
        super(ShareExtension, self).__init__(*args, **kwargs)

    def bind(self, container: ServiceContainer, name: t.Text) -> Extension:
        """ 绑定容器和对象名称

        @param container: 容器对象
        @param name: 扩展名称
        @return: ...
        """
        # 以当前类名作为标识符存入共享存储区
        ident = self.__class__.__name__
        if ident in container.shared_objects:
            return container.shared_objects[ident]
        else:
            o = super(ShareExtension, self).bind(
                container=container, name=name
            )
            container.shared_objects[ident] = o
            return container.shared_objects[ident]
