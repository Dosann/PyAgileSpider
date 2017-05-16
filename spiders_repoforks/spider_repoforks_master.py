# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 14:24:55 2017
@author: duxin
Email: duxin_be@outlook.com

"""

from sys import path
path.append("../")
from core import Tools
from core import Spider
import Queue
import traceback
import time
import random
from core import RedisSupport

import GLOBAL


def run(taskque,crawlerbody,errortasks):
    #从队列中获取任务，编写与该任务相关的信息提取代码
    time.sleep(180)
    print('has passed %s seconds'%(180),time.ctime)

    
def get_paras():
    #设置参数
    paras={}
    #数据库访问设置
    paras["conn_settings"]={"dbname":GLOBAL.dbname,
                             'host':GLOBAL.host,
                             'user':GLOBAL.user,
                             'passwd':GLOBAL.passwd,
                             'port':GLOBAL.port,
                             'charset':GLOBAL.charset}
    
    #线程数
    paras["threadnumber"]=20
    
    #不开启webdriver
    paras["webdriver"]=None
    paras["loadimage"]=False
    
    #使用github账号
    paras["github_account"]=True
    
    #是否自动创建表单，paras["conn_settings"]为None时必须设为None
    paras["db_construction"]=True
         
    #Crawler对象的其他初始化操作(登陆之类的)
    paras["crawler_initialize"]=CrawlerInitialize
    
    #是否在redis中读写队列
    #paras["taskque_format"]=None
    paras["taskque_format"]="redis"
    paras["redis_settings"]={"dbname":GLOBAL.redis_dbname,
                             "host":GLOBAL.redis_host,
                             "port":GLOBAL.redis_port}
    
    return paras

def create_queue():
    
    #读取任务信息
    startid=int(raw_input("input startid:"))
    endid=int(raw_input("input endid:"))
    LoadTasks(startid,endid)
    
    return 'taskque'


def CrawlerInitialize(crawlerbody):
    pass

def LoadTasks(startid,endid):
    conn=Tools.DatabaseSupport.GenerateConn(dbname=GLOBAL.dbname,host=GLOBAL.host,user=GLOBAL.user,passwd=GLOBAL.passwd,port=GLOBAL.port,charset=GLOBAL.charset)
    finished_task_ids=set(map(lambda x:x[0],Tools.LoadData.LoadDataByCmd(conn,"select id from repo_relas_fork_finished_tasks where status=1")))
    finishing_task_ids=set(map(lambda x:x[0],Tools.LoadData.LoadDataByCmd(conn,"select id from repo_relas_fork_finished_tasks where status=0")))
    all_tasks=Tools.LoadData.LoadDataByCmd(conn,"select id,user,repo from repo_active_20170508 where id>=%s and id<=%s"%(startid,endid))
    
    red_temp=RedisSupport.RedisSupport.GenerateRedisConnection(host=GLOBAL.redis_host,port=GLOBAL.redis_port,dbname=GLOBAL.redis_dbname)
    pipe=red_temp.pipeline()
    
    ommited_items_count=0
    loaded_items_count=0
    for task in all_tasks:
        if task[0] in finished_task_ids:
            ommited_items_count+=1
        elif task[0] in finishing_task_ids:
            loaded_items_count+=1
            forkers_number=Tools.LoadData.LoadDataByCmd(conn,"select forker_count from repo_relas_fork_finished_tasks where id=%s"%(task[0]))[0]
            if type(forkers_number)==tuple:
                forkers_number=forkers_number[0]
            pipe.rpush('taskque',[task[0],'/'.join(task[1:3]),forkers_number])
            if loaded_items_count%1000==0:
                pipe.execute()
        else:
            loaded_items_count+=1
            pipe.rpush('taskque',[task[0],'/'.join(task[1:3]),0])
    pipe.execute()
    
    print("loaded items count: %s"%(loaded_items_count))
    print("ommited items count: %s"%(ommited_items_count))
    
    del(finished_task_ids)
    del(finishing_task_ids)
    del(all_tasks)
    


def main():
    Spider.main(get_paras(),create_queue,run,mode=2)

main()
