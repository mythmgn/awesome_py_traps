---
layout: post
title: "[知识积累]Python踩坑之旅其二裸用os.sytem的原罪"
categories: 知识积累
tags: Python踩坑之旅,知识积累
toc: true
comments: true
---
[TOC]

# [知识积累]Python踩坑之旅其二裸用os.sytem的原罪

## 1.1 踩坑案例

今天的坑不仅包括裸用os.system还包括裸用相关的家族:

- os.popen
  - subprocess家族
    - subprocess.call
    - subprocess.Popen
    - subprocess.run
  - commands家族 (py2.6后已不推荐使用， depreciated. Py3删除)
    - commands.getstatusoutput


这些坑是新同学非常容易踩，而且 code review 过程中容易漏掉:

**[1] 长期运行 Service 中裸用以函数家族**

- 裸用以上 shell 执行家族可能出现script 执行 hang 住进而 hang 住逻辑执行线程，长时间积累进而占满所有执行线程而服务宕机情况
- 大内存消耗 service fork 子进程直接执行 script
  - 如果该 script hang 住
  - 并且原进程内存进行频繁修改（或者堆积修改， 虽然有 Copy-On-Write技术），但由于内存巨大，依然有内存风险

**[2] 自动化测试中裸用以上函数家族而不加以保护**

- 单个 case 如果执行 script 脚本 hang 住会导致 hang 掉整个case 集
- 不设计 case 超时机制导致case 集合运行时间不可控

## 1.2 填坑解法

1. 支持超时 kill 策略，禁止任何情况下的 shell 执行裸用家族函数

提供一个作者的代码参考: https://github.com/baidu/CUP/blob/master/cup/shell/oper.py

```python
        from cup import shell
        shellexec = shell.ShellExec()
        # timeout=None will block the execution until it finishes
        shellexec.run('/bin/ls', timeout=None)
        # timeout>=0 will open non-blocking mode
        # The process will be killed if the cmd timeouts
        shellexec.run(cmd='/bin/ls', timeout=100)
```

见ShellExec类的run函数

2. 内存消耗型服务/进程， 长期运行服务进程避免fork 进程执行 shell 命令

## 1.3 坑位分析

建议看下第二章节关于进程和子进程继承类信息，script使用上述家族进行执行时，采用了启动一个子进程的方式

### 1.4.1 技术关键字

- os.system家族
- subprocess家族

## 1.5 填坑总结

Shell执行是个非常常见的操作，所以很多同学特别是新同学，在使用过程中经常不注意而随意使用。 裸用一时爽，进程死亡火葬场

# 2. 前坑回顾

## 2.1 Linux中, 子进程拷贝父进程哪些信息

- 先说与父进程不同的
  - pid, ppid
  - memory locks
  - tms_utime、tms_stime、tms_cutime、tms_ustime
  - pending signals
  - [semaphore adjustments](https://stackoverflow.com/questions/34452654/what-child-does-not-inherit-semaphore-adjustments-from-its-parent-semop2-mea)
  - file lock
  - pending alarms

参考资料来源:  

- Linux Programmer's Manual ( `man fork` )
  - CentOS release 6.3 (Final)
  - Linux Kernel 2.6.32

```bash

fork()  creates a new process by duplicating the calling process.  The new process, referred to as the child, is an exact duplicate of the calling process, referred to as the parent, except for the follow-
ing points:

    *  The child has its own unique process ID, and this PID does not match the ID of any existing process group (setpgid(2)).

    *  The child's parent process ID is the same as the parent's process ID.

    *  The child does not inherit its parent's memory locks (mlock(2), mlockall(2)).

    *  Process resource utilizations (getrusage(2)) and CPU time counters (times(2)) are reset to zero in the child.

    *  The child's set of pending signals is initially empty (sigpending(2)).

    *  The child does not inherit semaphore adjustments from its parent (semop(2)).

    *  The child does not inherit record locks from its parent (fcntl(2)).

    *  The child does not inherit timers from its parent (setitimer(2), alarm(2), timer_create(2)).

    *  The child does not inherit outstanding asynchronous I/O operations from its parent (aio_read(3), aio_write(3)), nor does it inherit any asynchronous I/O contexts from its parent (seeio_setup(2)).

       The process attributes in the preceding list are all specified in POSIX.1-2001.  The parent and child also differ with respect to the following Linux-specific process attributes:

    *  The child does not inherit directory change notifications (dnotify) from its parent (see the description of F_NOTIFY in fcntl(2)).

    *  The prctl(2) PR_SET_PDEATHSIG setting is reset so that the child does not receive a signal when its parent terminates.

    *  Memory mappings that have been marked with the madvise(2) MADV_DONTFORK flag are not inherited across a fork().

    *  The termination signal of the child is always SIGCHLD (see clone(2)).

```

在说继承、拷贝父进程的

- 包括
  - 内部数据空间
  - 堆栈
  - 用户 ID、组 ID、eid 有效用户 id、有效组 id、用户 id 标志和设置组 id 标志
  - 进程组 id
  - 会话 id
  - 终端
  - 当前目录、根目录
  - 文件模式屏蔽字
  - 信号屏蔽设置
  - 打开文件描述符
  - 环境
  - 共享存储段
  - 存储映射
  - 资源限制

此外

- 在父进程创建 (fork) 出一个子进程过程中, 为了加速, 会使用叫做 copy-on-write 的技术. 
  - 这项技术在存储软件领域也经常使用
  - [附上一个关于它的讨论，点击查看](https://unix.stackexchange.com/questions/58145/how-does-copy-on-write-in-fork-handle-multiple-fork)

## 2.2 Agent常驻进程选择>60000端口的意义

在 Linux 系统中， 一般系统会自动替程序选择端口连接到用户指定的目的端口， 而这个端口范围是提前设定好的， 比如作者的 centos：

```bash
$ cat /proc/sys/net/ipv4/ip_local_port_range
10000   60000
```

- 选择 60000 以上的端口可以避免冲突
- [附上一篇讨论该ip_local_port_range的文章，欢迎查看](https://www.cnblogs.com/solohac/p/4154180.html)