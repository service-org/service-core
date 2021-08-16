#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import pprint
import logging
import typing as t

from logging import getLogger
from collections import namedtuple

from .service import Service
from .configure import Configure
from .spawning import SpawningProxy
from .as_logger import as_timing_logger
from .decorator import AsLazyProperty
from .container import ServiceContainer

logger = getLogger(__name__)

# 连接对象
Connect = namedtuple('Connect', ['host', 'port'])


class ServiceManager(object):
    """ 服务管理类 """

    def __init__(self, config: Configure) -> None:
        """ 初始化实例

        @param config: 配置对象
        """
        # 记录多个服务容器
        self.target = {}
        # 记录多个服务监听
        self.listen = {}
        # 记录服务配置对象
        self.config = config

    def add_service(self, service: Service) -> None:
        """ 容器管理 - 添加服务容器

        @param service: 服务子类
        @return: None
        """
        container = ServiceContainer(service, self.config)
        self.target[service.name] = container
        conn_info = Connect(service.host, service.port)
        self.listen[service.name] = conn_info

    @AsLazyProperty
    def services(self) -> t.List[t.Text]:
        """ 服务管理 - 所有服务名称

        @return: t.List[t.Text]
        """
        return [service for service in self.target.keys()]

    @AsLazyProperty
    def containers(self) -> t.List[ServiceContainer]:
        """ 容器管理 - 所有服务容器

        @return: t.List[ServiceContainer]
        """
        return [container for container in self.target.values()]

    def start(self) -> None:
        """ 容器管理 - 启动所有容器

        @return: None
        """
        services = pprint.pformat(self.services)
        timing_logger = as_timing_logger(logger, level=logging.DEBUG)
        generator = timing_logger(f'services {services} started')
        next(generator)
        SpawningProxy(self.containers).start()
        next(generator)

    def wait(self) -> None:
        """ 容器管理 - 等待容器关闭

        @return: None
        """
        services = pprint.pformat(self.services)
        logger.info(f'all of services {services} is running')
        SpawningProxy(self.containers).wait()

    def stop(self) -> None:
        """ 容器管理 - 停止所有容器

        @return: None
        """
        services = pprint.pformat(self.services)
        timing_logger = as_timing_logger(logger, level=logging.DEBUG)
        generator = timing_logger(f'services {services} stopped')
        next(generator)
        SpawningProxy(self.containers).stop()
        next(generator)

    def kill(self) -> None:
        """ 容器管理 - 强杀所有容器

        @return: None
        """
        services = pprint.pformat(self.services)
        timing_logger = as_timing_logger(logger, level=logging.DEBUG)
        generator = timing_logger(f'services {services} killed')
        next(generator)
        SpawningProxy(self.containers).kill()
        next(generator)
