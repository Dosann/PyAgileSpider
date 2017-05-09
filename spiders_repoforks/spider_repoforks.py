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

import GLOBAL


def run(taskque,crawlerbody,errortasks):
    #从队列中获取任务，编写与该任务相关的信息提取代码
    
    conn=crawlerbody.conn
    g=crawlerbody.g
    
    #从队列中读取1个任务
    task=taskque.get()
    
    
    try:
        repo=g.get_repo(task[1])
        forks=repo.get_forks()
        
        forkers=[]
        current=0
        status=1
        for fo in forks[task[2]:]:
            current+=1
            forkers.append([task[1],unicode(fo)[22:-2]])
            if current>=1000:
                status=0
                break
        Tools.SaveData.SaveData(conn,forkers,"repo_relas_fork",["reponame","forker"])
        Tools.SaveData.SaveData(conn,[[task[0],current,status]],"repo_relas_fork_finished_tasks",["id","forker_count","status"])
        
        print("successfully updated forkers of repo %s"%(task[0]))
        
    except SystemExit,e:
        pass
    except Exception,e:
        print e
        #traceback.print_exc()
        if hasattr(e,'message') and 'list index out of range' in e.message:
            Tools.SaveData.SaveData(conn,[[task[0],0,1]],"repo_relas_fork_finished_tasks",["id","forker_count","status"])
            return
        elif 500 in e:
            Tools.SaveData.SaveData(conn,[[task[0],0,1]],"repo_relas_fork_finished_tasks",["id","forker_count","status"])
            return
        elif 404 in e and hasattr(e,'data') and 'Not Found' in e.data['message']:
            Tools.SaveData.SaveData(conn,[[task[0],0,1]],"repo_relas_fork_finished_tasks",["id","forker_count","status"])
            return
        elif 451 in e:
            Tools.SaveData.SaveData(conn,[[task[0],0,1]],"repo_relas_fork_finished_tasks",["id","forker_count","status"])
            return
        elif 403 in e and hasattr(e,'data') and 'too large' in e.data['message']:
            Tools.SaveData.SaveData(conn,[[task[0],0,1]],"repo_relas_fork_finished_tasks",["id","forker_count","status"])
            return
        elif 403 in e and hasattr(e,'data') and 'blocked' in e.data['message']:
            Tools.SaveData.SaveData(conn,[[task[0],0,1]],"repo_relas_fork_finished_tasks",["id","forker_count","status"])
            return
        elif 403 in e and hasattr(e,'data') and 'abuse' in e.data['message']:
            errortasks.append(task)
            print "abuse error."
            time.sleep(random.Random()*5+5)
            print("abuse stop finished")
            return
        else:
            errortasks.append(task)
            print("unexpected error(run). error task %s has been put back to taskque"%(task[0]))

    
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
    
    return paras

def create_queue():
    
    #读取任务信息
    startid=int(raw_input("input startid:"))
    endid=int(raw_input("input endid:"))
    que=LoadTasks(startid,endid)
    
    return que


def CrawlerInitialize(crawlerbody):
    pass

def LoadTasks(startid,endid):
    conn=Tools.DatabaseSupport.GenerateConn(dbname=GLOBAL.dbname,host=GLOBAL.host,user=GLOBAL.user,passwd=GLOBAL.passwd,port=GLOBAL.port,charset=GLOBAL.charset)
    finished_task_ids=set(map(lambda x:x[0],Tools.LoadData.LoadDataByCmd(conn,"select id from repo_relas_fork_finished_tasks where status=1")))
    finishing_task_ids=set(map(lambda x:x[0],Tools.LoadData.LoadDataByCmd(conn,"select id from repo_relas_fork_finished_tasks where status=0")))
    all_tasks=Tools.LoadData.LoadDataByCmd(conn,"select id,user,repo from repo_active_20170508 where id>=%s and id<=%s"%(startid,endid))
    
    taskque=Queue.Queue()
    ommited_items_count=0
    loaded_items_count=0
    for task in all_tasks:
        if task[0] in finished_task_ids:
            ommited_items_count+=1
        elif task[0] in finishing_task_ids:
            loaded_items_count+=1
            forkers_number=Tools.LoadData.LoadDataByCmd(conn,"select forker_count from repo_relas_fork_finished_tasks where id=%s"%(task[0]))[0]
            taskque.put([task[0],'/'.join(task[1:3]),forkers_number])
        else:
            loaded_items_count+=1
            taskque.put([task[0],'/'.join(task[1:3]),0])
    
    print("loaded items count: %s"%(loaded_items_count))
    print("ommited items count: %s"%(ommited_items_count))
    
    del(finished_task_ids)
    del(finishing_task_ids)
    del(all_tasks)
    
    return taskque


def main():
    Spider.main(get_paras(),create_queue,run,mode=1)

main()
