---
layout: post
title: "[知识积累]Python踩坑之旅其一杀不死的Shell子进程"
categories: 知识积累
tags: Python踩坑之旅,知识积累
toc: true
comments: true
---
[TOC]
  
# Python踩坑之旅其一杀不死的Shell子进程

## 1.1 踩坑案例

踩坑的程序是个常驻的Agent类管理进程, 包括但不限于如下类型的任务在执行:

- a. 多线程的网络通信包处理
  - 和控制Master节点交互
  - 有固定Listen端口
- b. 定期作业任务, 通过subprocess.Pipe执行shell命令
- c. etc

发现坑的过程很有意思:

- **a.重启Agent发现Port被占用了**
  - => 立刻**想到可能进程没被杀死, 是不是停止脚本出问题**
    - => 排除发现不是, Agent进程确实死亡了
    - => 通过 `netstat -tanop|grep port_number` 发现端口确实有人占用
  - => 调试环境, **直接杀掉占用进程了之, 错失首次发现问题的机会**
- **b.问题**在一段时间后**重现**， 重启后Port还是被占用
  - 定位问题出现在一个叫做xxxxxx.sh的脚本, 该脚本占用了Agent使用的端口
    - => 奇了怪了, 一个xxx.sh脚本使用这个奇葩Port干啥(大于60000的Port, 有兴趣的砖友可以想下为什么Agent默认使用6W+的端口)
    - => review**该脚本并没有进行端口监听的代码**
- 一拍脑袋, **c.进程共享了父进程资源**了
  - => 溯源该脚本,发现确实是Agent启动的任务中的脚本之一
  - => 问题基本定位, 该脚本属于Agent调用的脚本
  - => 该Agent继承了Agent原来的资源FD, 也就是这个port
  - => 虽然该脚本由于超时被动触发了terminate机制, 但terminate并没有干掉这个子进程
  - => 该脚本进程的父进程(ppid) 被重置为了1
- **d.问题****出在脚本进程超时kill逻辑**

## 1.2 填坑解法

通过代码review, 找到shell具体执行的库代码如下:

```python
self._subpro = subprocess.Popen(
    cmd, shell=True, stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    preexec_fn=_signal_handle
)
# 重点是shell=True !
```

把上述代码改为:

```python
self._subpro = subprocess.Popen(
    cmd.split(), stdout=subprocess.PIPE,
    stderr=subprocess.PIPE, preexec_fn=_signal_handle
)
# 重点是去掉了shell=True
```

## 1.3 坑位分析

Agent会在一个新创建的threading线程中执行这段代码, 如果线程执行时间超时(xx seconds), 会调用 ```self._subpro.terminate()```终止该脚本.

表面正常:

- 启用新线程执行该脚本
- 如果出现问题,执行超时防止hang住其他任务执行调用terminate杀死进程

深层问题:

- Python 2.7.x中subprocess.Pipe 如果shell=True, 会默认把相关的pid设置为shell(sh/bash/etc)本身(执行命令的shell父进程), 并非执行cmd任务的那个进程
- 子进程由于会复制父进程的opened FD表, 导致即使被杀死, 依然保留了拥有这个Listened Port FD

这样虽然杀死了shell进程(未必死亡, 可能进入defunct状态), 但实际的执行进程确活着. 于是`1.1`中的坑就被结实的踩上了.

## 1.4 坑后扩展

### 1.4.1 扩展知识

本节扩展知识包括二个部分:

- Linux系统中, 子进程一般会继承父进程的哪些信息
- Agent这种常驻进程选择>60000端口的意义

扩展知识留到下篇末尾讲述, 感兴趣的可以自行搜索

### 1.4.1 技术关键字

- Linux系统进程
- Linux随机端口选择
- 程序多线程执行
- Shell执行

## 1.5 填坑总结

1. 子进程会继承父进程的资源信息
2. 如果只kill某进程的父进程, 集成了父进程资源的子进程会继续占用父进程的资源不释放, 包括但不限于

    - listened port
    - opened fd
    - etc
  
3. Python Popen使用上, shell的bool状态决定了进程kill的逻辑, 需要根据场景选择使用方式