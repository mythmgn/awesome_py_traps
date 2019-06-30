#!/bin/bash                                                                                                                                                                                                   
# ##########################################################################                           
# Author: Guannan Ma

# Arguments:                                                                                           
#   None                                                                                               
#                                                                                                      
# Returns:                                                                                             
#   succ: 0                                                                                            
#   fail: not 0                                                                                        
# ##########################################################################   
sudo rm -f ./euid_cp
sudo gcc euid_cp.c -o euid_cp
# 设置文件owner为root
sudo chown root euid_cp
# 设置a. 非root只读  b. 增加执行权限
sudo chmod 755 euid_cp
# 设置stick bit, 执行euid_cp即可短暂获取root 权限, 执行任务
sudo chmod +s euid_cp
