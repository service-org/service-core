#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import os
import sys
import pprint
import inspect
import logging
import eventlet
import typing as t

from logging import getLogger
from eventlet.event import Event
from greenlet import GreenletExit
from eventlet.greenpool import GreenPool
from eventlet.greenthread import GreenThread
from service_core.exception import ReachTiming
from service_core.constants import WORKERS_CONFIG_KEY
from service_core.constants import DEFAULT_WORKERS_NUMBER

from .service import Service
from .configure import Configure
from .context import WorkerContext
from .checking import is_dependency
from .spawning import SpawningProxy
from .decorator import AsFriendlyFunc
from .decorator import AsLazyProperty
from .as_logger import as_timing_logger
from .service.extension import Extension
from .service.dependency import Dependency
from .service.entrypoint import Entrypoint

logger = getLogger(__name__)


class ServiceContainer(object):
    """ 服务容器类 """

    def __init__(self, service: Service, config: Configure) -> None:
        """ 初始化实例

        @param service: 服务子类
        @param config : 配置对象
        """
        self.config = config
        self.service = service
        # 停止信号 - 标识容器停止
        self.stop_event = Event()
        # 存储共享 - 用于共享扩展
        self.shared_objects = {}
        # 工作协程 - 受限于协程池
        self.worker_threads = {}
        # 分离协程 - 独立于协程池
        self.splits_threads = {}
        # 池子大小 - 防止内存溢出
        key, default = WORKERS_CONFIG_KEY, DEFAULT_WORKERS_NUMBER
        worker_pool_size = config.get(key, default=default)
        splits_pool_size = config.get(key, default=default)
        self.worker_pool = GreenPool(size=worker_pool_size)
        self.splits_pool = GreenPool(size=splits_pool_size)
        # 依赖注入 - 强制注入一次
        for p in self.no_skip_inject_dependencies: setattr(service, p.object_name, p.get_instance())

    @AsLazyProperty
    def entrypoints(self) -> t.Set[Entrypoint]:
        """ 入口收集 - 所有入口扩展

        @return: t.Set[Entrypoint]
        """
        predicate = lambda obj: isinstance(obj, Entrypoint)
        entrypoints = self._find_all_entrypoint(self.service, predicate)
        return {provider for provider in entrypoints}

    @AsLazyProperty
    def dependencies(self) -> t.Set[Dependency]:
        """ 依赖收集 - 所有依赖扩展

        @return: t.Set[Dependency]
        """
        dependencies = self._find_all_dependency(self.service, is_dependency)
        return {provider for provider in dependencies}

    @AsLazyProperty
    def no_skip_loaded_dependencies(self) -> t.Set[Dependency]:
        """ 依赖收集 - 需setup扩展

        @return: t.Set[Dependency]
        """
        return {provider for provider in self.dependencies if not provider.skip_loaded}

    @AsLazyProperty
    def no_skip_inject_dependencies(self) -> t.Set[Dependency]:
        """ 依赖收集 - 需依赖注入的

        @return: t.Set[Dependency]
        """
        return {provider for provider in self.no_skip_loaded_dependencies if not provider.skip_inject}

    @AsLazyProperty
    def no_skip_callme_dependencies(self) -> t.Set[Dependency]:
        """ 依赖收集 - 声明周期执行

        @return: t.Set[Dependency]
        """
        return {provider for provider in self.no_skip_inject_dependencies if not provider.skip_callme}

    def _kill_worker_threads(self) -> None:
        """ 协程管理 - 杀掉工作协程

        @return: None
        """
        base_func = SpawningProxy(self.worker_threads.keys()).kill
        # 优雅退出 - 工作协程调用kill会抛出异常
        exception = (GreenletExit,)
        kill_func = AsFriendlyFunc(base_func, all_exception=exception)
        return kill_func()

    def _kill_splits_threads(self) -> None:
        """ 协程管理 - 杀掉分离协程

        @return: None
        """
        base_func = SpawningProxy(self.splits_threads.keys()).kill
        # 优雅退出 - 分离协程调用kill会异常中断
        exception = (GreenletExit,)
        kill_func = AsFriendlyFunc(base_func, all_exception=exception)
        return kill_func()

    def _find_all_dependency(self, obj: Service, predicate: t.Callable[..., bool]) -> t.Iterable[Extension]:
        """ 扩展管理 - 获取所有依赖

        @param obj: 任意对象
        @param predicate: 过滤函数
        @return: t.Iterable[BaseExtension]
        """
        # 首次过滤器依据传入的为准
        all_members = inspect.getmembers(obj, predicate)
        for name, provider in all_members:
            # 绑定容器对象和属性名
            provider = provider.bind(self, name)
            setattr(obj, name, provider)
            yield provider
            # 递归获取此扩展的子扩展
            sub_members = self._find_all_dependency(provider, is_dependency)
            for sub_provider in sub_members:
                yield sub_provider

    def _find_sub_entrypoint(self, obj: Extension, predicate: t.Callable[..., bool]) -> t.Iterable[Extension]:
        """ 扩展管理 - 递归获取入口

        @param obj: 任意对象
        @param predicate: 过滤函数
        @return: t.Iterable[BaseExtension]
        """
        all_members = inspect.getmembers(obj, predicate)
        for name, provider in all_members:
            # 绑定容器对象和属性名
            yield provider.bind(self, name)
            # 递归获取此扩展的子扩展
            sub_members = self._find_sub_entrypoint(provider, predicate)
            for sub_provider in sub_members:
                yield sub_provider

    def _find_all_entrypoint(self, obj: Service, predicate: t.Callable[..., bool]) -> t.Iterable[Extension]:
        """ 扩展管理 - 获取所有入口

        @param obj: 任意对象
        @param predicate: 过滤函数
        @return: t.Iterable[BaseExtension]
        """
        all_members = obj.router_mapping
        for name, view in all_members.items():
            # 递归获取此扩展的子扩展
            for provider in view.entrypoints:
                # 绑定容器对象和属性名
                yield provider.bind(self, name)
                sub_members = self._find_sub_entrypoint(provider, predicate)
                for sub_provider in sub_members:
                    yield sub_provider

    @AsLazyProperty
    def _all_entrypoint_strs(self) -> t.Text:
        """ 格式输出 - 显示所有入口

        @return: None
        """
        return os.linesep + pprint.pformat(self.entrypoints) if self.entrypoints else '{}'

    @AsLazyProperty
    def _all_dependency_strs(self) -> t.Text:
        """ 格式输出 - 显示所有依赖

        @return: None
        """
        return os.linesep + pprint.pformat(self.dependencies) if self.dependencies else '{}'

    def start(self) -> None:
        """ 扩展管理 - 启动所有扩展

        @return: None
        """
        timing_logger = as_timing_logger(logger, level=logging.DEBUG)
        generator = timing_logger(f"service {self.service.name}'s dependencies {self._all_dependency_strs} started")
        next(generator)
        # 无序加载 - 调用所有依赖对象的setup方法
        SpawningProxy(self.no_skip_loaded_dependencies).setup()
        # 无序加载 - 调用所有依赖对象的start方法
        SpawningProxy(self.no_skip_loaded_dependencies).start()
        next(generator)
        generator = timing_logger(f"service {self.service.name}'s entrypoints {self._all_entrypoint_strs} started")
        next(generator)
        # 无序加载 - 调用所有入口对象的setup方法
        SpawningProxy(self.entrypoints).setup()
        # 无序启动 - 调用所有入口对象的start方法
        SpawningProxy(self.entrypoints).start()
        next(generator)

    def wait(self) -> None:
        """ 扩展管理 - 等待扩展关闭

        @return: None
        """
        host = self.service.host
        port = self.service.port
        host and port and logger.info(f"service {self.service.name} listen on {host}:{port}")
        self.stop_event.wait()

    def stop(self) -> None:
        """ 扩展管理 - 停止所有扩展

        @return: None
        """
        # 强制关闭 - 分离协程可能死循环无法优雅
        self._kill_splits_threads()
        timing_logger = as_timing_logger(logger, level=logging.DEBUG)
        generator = timing_logger(f"service {self.service.name}'s dependencies {self._all_dependency_strs} stopped")
        next(generator)
        # 无序停止 - 调用所有依赖对象的stop方法
        SpawningProxy(self.no_skip_loaded_dependencies).stop()
        next(generator)
        generator = timing_logger(f"service {self.service.name}'s entrypoints {self._all_entrypoint_strs} stopped")
        next(generator)
        # 无顺停止 - 调用所有依赖对象的stop方法
        SpawningProxy(self.entrypoints).stop()
        # 优雅停止 - 等待所有工作协程处理完成后
        self.worker_pool.waitall()
        next(generator)

        # 发送信号 - 表示从服务对应的容器已关闭
        self.stop_event.ready() or self.stop_event.send()

    def kill(self) -> None:
        """ 扩展管理 - 强杀所有扩展

        @return: None
        """
        # 强制关闭 - 分离协程可能死循环无法优雅
        self._kill_splits_threads()
        timing_logger = as_timing_logger(logger, level=logging.DEBUG)
        generator = timing_logger(f"service {self.service.name}'s dependencies {self._all_dependency_strs} killed")
        next(generator)
        # 无序停止 - 调用所有依赖对象的kill方法
        SpawningProxy(self.no_skip_loaded_dependencies).kill()
        next(generator)
        generator = timing_logger(f"service {self.service.name}'s entrypoints {self._all_entrypoint_strs} killed")
        next(generator)
        # 无顺强杀 - 调用所有依赖对象的kill方法
        SpawningProxy(self.entrypoints).kill()
        # 强制杀死 - 不等所有工作协程处理完成后
        self._kill_worker_threads()
        next(generator)

    def _link_worker_results(self, gt: GreenThread, generator: t.Generator) -> None:
        """ 协程管理 - 工作协程回调

        @param gt: 协程对象
        @param: generator: 耗时日志生成器
        @return: None
        """
        # 耗时记录 - 等待到执行完毕时输出耗时
        next(generator)
        # 垃圾回收 - 防止大量请求时的内存溢出
        self.worker_threads.pop(gt, None)

    def _call_worker_setups(self, context: WorkerContext) -> None:
        """ 工作协程 - 调用载入方法

        @param context: 上下文对象
        @return: None
        """
        SpawningProxy(self.no_skip_callme_dependencies).worker_setups(context)

    def _call_worker_result(self, context: WorkerContext, results: t.Any) -> None:
        """ 工作协程 - 调用结果方法

        @param context: 上下文对象
        @param results: 执行结果
        @return: None
        """
        SpawningProxy(self.no_skip_callme_dependencies).worker_result(context, results)

    def _call_worker_errors(self, context: WorkerContext, excinfo: t.Tuple) -> None:
        """ 工作协程 - 调用异常方法

        @param context: 上下文对象
        @param excinfo: 执行异常
        @return: None
        """
        SpawningProxy(self.no_skip_callme_dependencies).worker_errors(context, excinfo)

    def _call_worker_finish(self, context: WorkerContext) -> None:
        """ 工作协程 - 调用完成方法

        @param context: 上下文对象
        @return: None
        """
        SpawningProxy(self.no_skip_callme_dependencies).worker_finish(context)

    def _get_target_method(self, context: WorkerContext) -> t.Tuple[t.Callable[..., t.Any], t.Tuple, t.Dict]:
        """ 获取目标执行方法以及参数

        @param context: 上下文对象
        @return: t.Tuple[t.Callable[..., t.Any], t.Tuple, t.Dict]
        """
        entrypoint = context.original_entrypoint
        method_name = entrypoint.object_name
        kwargs = context.original_kwargs
        # 从router_mapping查找entrypoint名称对应目标视图~
        method = self.service.router_mapping[method_name]
        # 判断是服务对象本身的方法还是来自于路由自动收集的方法?
        args = context.original_args if hasattr(
            self.service, method_name
        ) else (
            self.service, *context.original_args
        )
        return method, args, kwargs

    def _run_timing_method(
            self,
            method: t.Callable[..., t.Any],
            *,
            args: t.Optional[t.Tuple[...]] = None,
            kwargs: t.Optional[t.Dict[t.Text, t.Any]] = None,
            timeout: t.Optional[t.Union[int, float]] = None
    ) -> t.Any:
        """ 调用目标函数并加入限时

        @param method: 目标方法
        @param args  : 位置参数
        @param kwargs: 命名参数
        @param timeout: 超时时间
        @return: t.Any
        """
        args, kwargs = args or (), kwargs or {}
        is_numeric = isinstance(timeout, (int, float))
        if is_numeric and timeout:
            unit = 'seconds' if timeout > 1 else 'second'
            errs = f'reach timeout({timeout} {unit})'
            exception = ReachTiming(errormsg=errs)
            exception.original = self.service.name
            timer = eventlet.Timeout(timeout, exception)
            try:
                return method(*args, **kwargs)
            finally:
                timer.cancel()
        return method(*args, **kwargs)

    def start_worker_thread(self, context: WorkerContext) -> t.Any:
        """ 工作协程 - 启动工作协程

        @param context: 上下文对象
        @return: None
        """
        results, excinfo = None, None
        self.no_skip_callme_dependencies and self._call_worker_setups(context)
        method, args, kwargs = self._get_target_method(context)
        # 针对每个入口扩展都可以设置它执行超时时间防止阻塞
        timeout = context.original_entrypoint.exec_timing
        try:
            results = self._run_timing_method(
                method, args=args, kwargs=kwargs, timeout=timeout
            )
        except BaseException:
            message = (f'call worker thread '
                       f'{context.original_entrypoint} '
                       f'args={args} kwargs={kwargs}')
            logger.error(message, exc_info=True)
            excinfo = sys.exc_info()
            self.no_skip_callme_dependencies and self._call_worker_errors(context, excinfo)
        finally:
            if excinfo is None:
                self.no_skip_callme_dependencies and self._call_worker_result(context, results)
                self.no_skip_callme_dependencies and self._call_worker_finish(context)
            else:
                self.no_skip_callme_dependencies and self._call_worker_finish(context)
        return context, results, excinfo

    def spawn_worker_thread(
            self,
            entrypoint: Entrypoint,
            args: t.Optional[t.Sequence] = None,
            kwargs: t.Optional[t.Dict] = None,
            context: t.Optional[t.Dict] = None,
            *,
            tid: t.Text
    ) -> GreenThread:
        """ 协程管理 - 创建工作协程

        @param entrypoint: 入口, 指定的entrypoint实例
        @param args  : 位置参数, entrypoint的位置参数
        @param kwargs: 命名参数, entrypoint的命名参数
        @param context:上下文集, 上游服务传递下的上下文
        @param tid: 协程唯一标识, 当前协程的类型标注
        @return: GreenThread
        """
        kwargs = kwargs if isinstance(kwargs, dict) else {}
        args = args if isinstance(args, (tuple, list)) else ()
        context = context if isinstance(context, dict) else {}
        message = f'{tid} args={args} kwargs={kwargs} context={context}'
        logger.debug(f'spawn worker thread {message}')
        timing_logger = as_timing_logger(logger, level=logging.DEBUG)
        generator = timing_logger(f'call worker thread {message}')
        next(generator)
        context = WorkerContext(self.service, entrypoint, args=args, kwargs=kwargs, context=context)
        green_thread = self.worker_pool.spawn(self.start_worker_thread, context)
        green_thread.__dict__['context'] = context
        self.worker_threads[green_thread] = tid
        green_thread.link(self._link_worker_results, generator)
        return green_thread

    def _link_splits_results(self, gt: GreenThread, generator: t.Generator) -> None:
        """ 协程管理 - 分离协程回调

        @param gt: 协程对象
        @param generator: 耗时日志生成器
        @return: None
        """
        # 耗时记录 - 等待到执行完毕时输出耗时
        next(generator)
        # 垃圾回收 - 防止大量请求时的内存溢出
        self.splits_threads.pop(gt, None)

    def spawn_splits_thread(
            self,
            func: t.Callable,
            args: t.Optional[t.Sequence] = None,
            kwargs: t.Optional[t.Dict] = None,
            *, tid: t.Text
    ) -> GreenThread:
        """ 协程管理 - 创建分离协程

        @param func: 目标函数体, 用于非工作协程管理
        @param args  : 位置参数, 目标函数的位置参数
        @param kwargs: 命名参数, 目标函数的命名参数
        @param tid: 协程类型标识, 当前协程的类型标注
        @return: GreenThread
        """
        kwargs = kwargs if isinstance(kwargs, dict) else {}
        args = args if isinstance(args, (tuple, list)) else ()
        green_thread = self.splits_pool.spawn(func, *args, **kwargs)
        message = f'{tid} args={args} kwargs={kwargs}'
        logger.debug(f'spawn splits thread {message}')
        timing_logger = as_timing_logger(logger, level=logging.DEBUG)
        generator = timing_logger(f'call splits thread {message}')
        next(generator)
        self.splits_threads[green_thread] = tid
        green_thread.link(self._link_splits_results, generator)
        return green_thread
