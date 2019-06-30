#!/usr/bin/env python                                                                                  
# -*- coding: utf-8 -*                                                                                 
# Copyright - See LICENSE for details                                                                  
# Authors: Guannan Ma @mythmgn                                                                         
"""                                                                                                    
:description:                                                                                          
    say something here                                                                                 
"""                                                                                                    
                                                                                                       
from __future__ import print_function                                                                  
import os                                                                                              
import sys                                                                                             
                                                                                                       
_TOP = os.path.dirname(os.path.abspath(__file__)) + '/../'                                             
sys.path.insert(0, _TOP)                                                                               
                                                                                                       
from cup.shell import oper                                                                             
from cup.res import linux                                                                              
                                                                                                       
                                                                                                       
def test_get_fd():                                                                                     
    """test get fd"""                                                                                  
    # get_pid 第一个参数是启动程序的路径, 第二个是匹配参数, 比如mysqld                                 
    arrow_pid = oper.get_pid('/home/maguannan/.jumbo/bin/', 'arrow_agent')                             
    print('pid {0}'.format(arrow_pid))                                                                 
    process = linux.Process(arrow_pid)                                                                 
    # 通过 get_open_files 函数获得打开文件数目                                                         
    print('opened fd {0}'.format(process.get_open_files()))                                            
    # linux.Process(pid) 对象可以获取所有该进程的有效信息, 比如open fd, cpu时间                        
                                                                                                       
# vi:set tw=0 ts=4 sw=4 nowrap fdm=indent            