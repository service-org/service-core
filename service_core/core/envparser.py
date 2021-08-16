#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import re
import os
import typing as t

# 检查是否存在环境变量
ENV_VARIABLE_RE_CHECKED = re.compile(
    r'''
    .*          # matches any number of any characters
    \$\{.*\}    # matches any number of any characters
                # between `${` and `}` literally
    .*          # matches any number of any characters
    ''', re.VERBOSE
)

# 解析有默认值环境变量
ENV_VARIABLE_RE_MATCHER = re.compile(
    r'''
    \$\{       # match characters `${` literally
    ([^}:\s]+) # 1st group: matches any character except `}` or `:`
    :?         # matches the literal `:` character zero or one times
    ([^}]+)?   # 2nd group: matches any character except `}`
    \}         # match character `}` literally
    ''', re.VERBOSE
)


def parse_env_variable(matcher: t.Match) -> t.Text:
    """ 变量解析 - 解析指定环境变量

    @param matcher: 匹配对象
    @return: t.Text
    """
    variable, default = matcher.groups()
    # TODO: 暂不支持递归解析环境变量,变量值为变量的
    return os.environ.get(variable, default)


def parse_env_contents(content: t.Text) -> t.Text:
    """ 全局替换 - 递归替换环境变量

    @param content: 原始数据
    @return: t.Text
    """
    matcher = ENV_VARIABLE_RE_MATCHER
    return matcher.sub(parse_env_variable, content)
