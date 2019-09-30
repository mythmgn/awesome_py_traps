**Awesome Py Traps 的初衷**
1. 梳理自己的 python 知识树, 总结在使用 python 编程过程中的经验教训
2. 让 Unix-Like 系统知识 和 python代码实现/试验 相结合, 互相印证 


- 文档更新:
  - 欢迎感兴趣的朋友一起写稿填坑
  - 发起人预计每周更新一篇, 持续至 100 篇
  - 已有章目但未有链接的代表还在撰写 pending list 中

- 发起人简介
  - 某厂专有云测试开发负责人, 十年分布式存储\计算项目经验
  - Python 开源基础库负责人和主要作者: https://github.com/baidu/CUP
  - 微信公众号: 程序员的梦呓指南 ![](weixin_nosign.png)


# 1. Python 踩坑之旅

## 进程篇

- [1. 杀不死的 Shell 子进程.md](./1_process/其一杀不死的shell子进程.md)
- [2. 裸用 os.system 类函数的原罪.md](./1_process/其二裸用类os.system函数的原罪.md)
- [3. 进程 pgid 是个什么鬼.md](./1_process/其三pgid是个什么鬼.md)
- [4. 一次性踩透 uid_euid_gid_egid 的坑坑洼洼.md](./1_process/其四一次性踩透uid_euid_gid_egid的坑坑洼洼.md)
- [5. 为啥打不开新文件](./1_process/其五为啥打不开新文件.md)
- [6. PyDaemon 进程长什么样]()

## 线程篇

- [Python 线程是摆设吗 (GIL 问题)]
- [线程是越多越好还是越少越好]


## 日志篇

## Pythonic 特色篇


# 2. 系统知识 坑洼之旅

## 文件系统篇

- **[文件夹也是 File Object](./2_filesystem/其一目录也是个文件.md) <-------- (新增2019.9.20)**
- [Umask 到底影响了谁]
- [一次性搞清楚文件目录权限判定]
- [慎用软硬链接]
- [Readonly 数据恢复小窍门]


## 输入输出IO篇

- [你不知道的File Open]
- [读写的几种口味]
- [论游标的重要性]
- [谁打开谁关闭]
- [谁动了我的数据缓存]
- [为什么你要关心编码]
- [临时文件也疯狂]

## 网络篇

- [服务器端为什么非得绑定端口]
- [tcp 为什么不一定比 udp 好]
- [链接池越大越好么]
- [非阻塞一定比阻塞好吗]
- [epoll的几种坏味道]
- [上下文管理在管理什么]
- [心跳机制解决了什么问题]
- [网络传输数据为什么要序列化和反序列化]
- [该死的wait_time_out]


