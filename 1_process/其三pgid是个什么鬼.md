---
layout: post
title: "Python 踩坑之旅进程篇其三pgid是个什么鬼"
categories: 知识积累
tags: Python踩坑之旅,知识积累
toc: true
comments: true
---
[TOC]

# Python 踩坑之旅进程篇其三pgid是个什么鬼

 | 代码示例支持|
|-|
|平台: Centos 6.3| 
|Python: 2.7.14  |
|Github上搜索 **CUP** <br/> ![cup](./cup_github.png)|

## 1.1 踩坑案例

pid, ppid是大家比较常见的术语, 代表进程号,父进程号. 但pgid是个什么鬼?

了解pgid之前, 我们先复习下:

- [进程篇其一](2019-05-05-Python踩坑之旅进程篇其一杀不死的shell子进程.md)
  - 里面场景是: 一个进程通过`os.system`或者`Popen`家族启动子进程
  - 后通过杀死父进程的方式无法杀死它的连带子进程
  - 我们通过其他方式进行了解决

这个场景还有个后续就是:

- 如果这个子进程还有孙子怎么办?
- 它还有孙子的孙子怎么办?

这个就是今天我们遇到的坑, 怎么处理孙子进程. 大家注意, 不仅是Python会遇到这个问题, 其他语言包括 Shell 都一样会遇到这种"孙子"进程怎么进程异常处理的问题.

## 1.2 填坑解法

本期的坑位解法其实有两种, 第一种比较暴力, 简称穷尽搜索孙子法.

a. 穷尽搜索孙子法, 代码示例

关键点:

- 使用cup.res.linux中的Process类, 获得该进程所有的子孙进程
- 使用kill方法全部杀死

```python
from cup.res import linux
pstatus = linux.Process(pid)
for child in pstatus.children(recursive=True):
    os.kill(child, signal.SIGKILL)
```

b. 获得该进程的 PGID, 进行 kill 操作

b1. 先讲个 shell 操作的做法,  使用ps 获取进程的**pgid**, 注意**不是**pid

```bash
# 以mysqld为例, 注意 pgid 项
ps -e -o uid,pid,gid,pgid,cmd|grep mysql
```

结果:

- 注意其中第三列, 该进程和子进程都使用了同样的pgid **9779**

    9790     0  9779 /bin/sh /usr/bin/mysqld_safe --datadir=/home/maguannan/mysql/mysql/....

    10171   501  9779 /home/maguannan/bin/mysqld --basedir=/home/maguannan/mysql/....

- 通过`kill -9 -9779`的方式可以杀死该pgid底下的所有**子孙**进程

b2. 在讲 Python 里的处理方式

```python
import os
import signal
from cup.res import linux
pstatus = linux.Process(pid)
os.killpg(pstatus.getpgid(), signal.SIGKILL)
```

## 1.3 坑位分析

**进程组特性**

a. 在*unix 编程中, 进程组(`man getpgid`)概念是个很重要但容易被忽略的内容

- 进程组ID (pgid) 标记了一系列相关的进程
- 进程组有一个组长进程, 一般组长进程 ID 等于进程组 ID
- 进程组只要任一进程存在, 进程组就存在. 进程组存在与否与组长死活无关
- 可以通过setpgid方式设置一个进程 pgid
  - 一个进程只能为自己或者子进程设置进程组 id
  - 子进程一旦执行了exec函数, 它就不能改变子进程的进程组 id

b. 进程组内的所有成员会收到来自相同的信号

引用 wikipedia 原文:
```
  a process group is used to control the distribution of a signal; when a signal is directed to a process group, the signal is delivered to each process that is a member of the group.
```

**坑位解决**

- 由于进程组拥有以上的特性, 进程组内的进程可以被当做相同的处理单元
  - 默认子进程与父进程拥有同样的进程组
  - 组内每个进程收到相同的信号)
- 使用kill发送信号 SIGKILL 即可满足杀死所有子**孙**进程的目的

### 1.4.1 技术关键字

- pgid 进程组
- pid, ppid  进程ID, 父进程ID

## 下期坑位预告

- 踩坑之旅进程篇其四: 一次性踩透uid, euid, gid, egid的坑坑洼洼


---
Life is short. We use Python.