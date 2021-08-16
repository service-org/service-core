# 运行环境

|system |python | 
|:------|:------|      
|cross platform |3.9.16|

# 组件安装

```shell
pip install -U service-core 
```

# 内置命令

> core --help

```shell
usage: core [-h] [--version] {config,debug,shell,start} ...

positional arguments:
  {config,debug,shell,start}
    config              show rendered yaml config
    debug               remote debug with backdoor
    shell               launch an interactive shell
    start               start one or more services

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```
