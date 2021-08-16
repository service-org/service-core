#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sys
import typing as t

from logging import getLogger
from service_core.core.service import Service
from service_core.core.configure import Configure
from service_core.core.decorator import AsFriendlyFunc
from service_core.core.as_helper import get_accessible_port
from service_core.core.as_finder import find_declare_services

logger = getLogger(__name__)
system_quick_exit = sys.exit


class ServiceRunner(object):
    """ 多服务启动管理程序 """

    def __init__(self, services_dotted_paths: t.List[t.Text], config: Configure, *, debugs: bool = False) -> None:
        """ 初始化实例

        @param services_dotted_paths: 服务列表
        @param config: 配置对象
        @param debugs: 开启调试
        """
        self.debugs = debugs
        self.config = config
        self.services_dotted_paths = services_dotted_paths

    def load_service_from_dotted_paths(self) -> t.Set[Service]:
        """ 查找所有服务

        @return: t.Set[t.Type[Service]]
        """
        available_services = set()
        for dotted_path in self.services_dotted_paths:
            error, services = find_declare_services(dotted_path)
            error_prefix_message = f'load {dotted_path} fail,'
            sys_exit_flag = log_errs_flag = False
            if error is not None:
                sys_exit_flag = log_errs_flag = True
                error = error_prefix_message + error
            if error is None and not services:
                sys_exit_flag = log_errs_flag = True
                error = 'no instance of Service'
                error = error_prefix_message + error
            log_errs_flag and logger.error(error)
            sys_exit_flag and system_quick_exit()
            logger.debug(f'load file {dotted_path}.py succ')
            available_services.update(services)
        return available_services

    @staticmethod
    def spawn_backdoor(context: t.Dict[t.Text, t.Any]) -> None:
        """ 启动后门服务

        @param context: 调试上下文
        @return: None
        """
        # eventlet的事件循环与asyncio不兼容,防止影响其它异步驱动命令
        import eventlet
        from eventlet.backdoor import backdoor_server

        def backdoor_command_exit() -> None:
            """ 后门shell中退出命令 """
            raise UserWarning('this would kill interpreter, use ctrl + c')

        def backdoor_command_quit() -> None:
            """ 后门shell中退出命令 """
            raise UserWarning('this would kill interpreter, use ctrl + c')

        green_socket = eventlet.listen(('127.0.0.1', get_accessible_port()))
        green_socket.settimeout(None)
        # 需要注意的是命令是直接提交给解释器执行的,执行exit退出整个程序
        context['exit'] = backdoor_command_exit
        context['quit'] = backdoor_command_quit
        eventlet.spawn(backdoor_server, green_socket, locals=context)

    def start(self) -> None:
        """ 启动所有服务

        @return: None
        """
        # eventlet的事件循环与asyncio不兼容,防止影响其它异步驱动命令
        from service_core.core.manager import ServiceManager

        sm = service_manager = ServiceManager(self.config)
        self.debugs and self.spawn_backdoor({'s': service_manager})
        for service in self.load_service_from_dotted_paths():
            service_manager.add_service(service)
        else:
            service_manager.start()
        all_exception = (KeyboardInterrupt, Exception)

        def succ_callback(results: t.Any) -> t.Any:
            """ 成功时回调函数

            @param results: 结果对象
            @return: t.Any
            """
            AsFriendlyFunc(sm.stop, all_exception=all_exception)()
            AsFriendlyFunc(sm.kill, all_exception=all_exception)()

        def fail_callback(excinfo: t.Any) -> t.Any:
            """ 失败时回调函数

            @param excinfo: 异常对象
            @return: t.Any
            """
            AsFriendlyFunc(sm.stop, all_exception=all_exception)()
            AsFriendlyFunc(sm.kill, all_exception=all_exception)()

        AsFriendlyFunc(service_manager.wait,
                       succ_callback=succ_callback,
                       fail_callback=fail_callback,
                       all_exception=all_exception
                       )()
        logger.debug(f'all of services {sm.services} shutdown')
