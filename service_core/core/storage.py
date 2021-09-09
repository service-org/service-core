#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from eventlet.corolocal import local

# 保证线程安全
green_thread_local = local()
