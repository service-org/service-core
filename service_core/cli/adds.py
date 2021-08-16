#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import yaml
import typing as t

from yaml.nodes import Node
from functools import partial
from yaml.constructor import BaseConstructor
from service_core.core.envparser import parse_env_contents
from service_core.core.envparser import ENV_VARIABLE_RE_CHECKED


def yaml_env_parser(loader: BaseConstructor,
                    node: Node, raw=False) -> t.Text:
    """ YAML环境变量解析器 """
    source_content = loader.construct_scalar(node)
    # 替换原始数据中的的环境变量
    target_content = parse_env_contents(source_content)
    return target_content if raw else yaml.safe_load(target_content)


def setup_yaml_env_parser() -> None:
    """ YAML加载变量解析器 """
    has_env_variable = ENV_VARIABLE_RE_CHECKED
    tag, regexp = '!env_var', has_env_variable
    yaml.add_implicit_resolver(tag, regexp, Loader=yaml.UnsafeLoader)
    tag, parser = '!env_var', yaml_env_parser
    yaml.add_constructor(tag, parser, Loader=yaml.UnsafeLoader)
    tag, parser = '!raw_env_var', partial(yaml_env_parser, raw=True)
    yaml.add_constructor(tag, parser, Loader=yaml.UnsafeLoader)
