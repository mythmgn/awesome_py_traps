[TOC]

 | 代码示例支持|
|-|
|平台: Centos 6.3| 
|Python: 2.7.14  |
|代码示例: code_demo目录|

## 1.1 踩坑案例

小明是个服务器管理员, 他从老管理员手里接手了一个非常繁琐的运维工作: 短暂授权root 账号给不同的 team 接口人运行备份任务

该运维任务有几个特点:

1. 任务需且仅需运行在 root 下
    - root 账号只能短暂授权给各个小组
    - 通过账号管理平台, 提前申请一段时间的临时密码
    - 将临时密码提供给小组接口人
    - 时间超时后密码自动变更
2. 不同 team 分时使用, 无法并发使用

小明非常烦躁, 为了填上这个坑, 他调研了填坑解法.

## 1.2 填坑解法

填坑解法满足:

- 短时出借权限
  - (在权限范围内)执行该任务时才能使用 root 权限
  - 做完任务立即失去 root 权限
- 权限范围必须清晰
  - 能做什么
    - 能做数据备份
  - 不能做什么
    - 除了数据备份其他什么都不在 root 权限下做

**具体做法:**

1. 利用c/c++程序出借部分 root 权限  (完整代码关注公号点击菜单查看)

    - 该c程序限定执行的备份操作为 python 代码 euid_backup.py
    ```c
    int main(int argc, char **argv){
        if(0==isRunUnderRoot()){
            fprintf(stderr,"does not run under +S attribute. Exiting....\n");
            return EXIT_FAILURE;
        }
        exit(runNewProcess("./", "/usr/bin/backup/secured/python /usr/bin/backup/secured/euid_backup.py"));
    }
    ```
    - euid_backup.py owner 为 root, 非 root 用户不准更改备份操作内容

2. 为生成的执行文件euid_cp及euid_backup.py 设置root权限借用

    ```bash
    sudo rm -f /usr/bin/backup/secured/euid_cp
    sudo gcc euid_cp.c -o /usr/bin/backup/secured/euid_cp
    # 设置文件owner为root, 非root用户无法更改执行内容
    sudo chown root /usr/bin/backup/secured/*
    # 设置a. 非root只读  b. 增加执行权限
    sudo chmod 755 /usr/bin/backup/secured/euid_cp
    # 设置stick bit, 执行euid_cp即可短暂获取root 权限, 执行任务
    sudo chmod +s /usr/bin/backup/secured/euid_cp
    ```

- /usr/bin/backup/secured/euid_backup.py Python 代码执行具体的备份任务
  
    ```python
    from __future__ import print_function
    import os
    import time

    print('euid is {0}'.format(os.geteuid()))

    if os.geteuid() == 0:
        print('start to copy under root')
        print('do some operations here')
        time.sleep(2)
        print('end copying things')
        print('drop privileges from root')
    else:
        print('non-root, euid {0} will exit'.format(os.geteuid()))
    ```

运行试验:
1. 通过 /usr/bin/backup/secured/euid_cp 执行, 可以在非 root 下执行 root 权限才能执行的备份任务(euid_backup.py)

2. 直接执行备份任务(/usr/bin/backup/secured/euid_backup.py) 会失败, 没有权限

## 1.3 坑位分析

1. uid / euid / suid 是什么

   - uid 是用户的 userid
     - 登陆后, 在不切换用户情况下 uid 一般不变
   - euid 是用户的有效 id
     - euid 在正常执行情况下一般等于uid
     - euid 一般决定了用户对系统中存储介质的access (访问) 权限
   - suid (saved uid) 是文件在被访问过程中的短暂切换用户euid的属性设置
     - 简单来说, suid让本没有权限的用户可以短暂访问这些资源
     - suid 在执行过程中进行了权限切换
       - 执行之初, 切换到这个saved uid(文中为 root)
       - fork执行过程中, euid == suid
       - 执行完成后, euid 在切换回 uid

2. gid, egid 等同理, [*]uid的判断优先

## 1.4 技术关键字

- uid euid suid
- gid egid sgid

## 1.5 坑后思考

1. 为什么本文没有直接对euid_backup.py文件进行设置+s操作, 而是用可执行的c/c++程序做执行器

2. Linux 系统里的passwd 程序是否也是这个原理?  它跟哪些文件/命令相关

## 下期坑位预告

进程篇其五之眼花缭乱的进程间通信

---
Life is short. We use Python.
