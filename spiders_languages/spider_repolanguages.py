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

import GithubApispiderSupport_languages as gasl
import GLOBAL


def run(taskque,crawlerbody,errortasks):
    #从队列中获取任务，编写与该任务相关的信息提取代码
    
    conn=crawlerbody.conn
    
    #从队列中读取1个任务
    task=taskque.get()
    
    if GLOBAL.newtask_open==1 and GLOBAL.finishedcount%GLOBAL.batchsize==0:
        new_tasks=LoadTasks(GLOBAL.batchsize)
        for task in new_tasks:
            taskque.put(task)
        new_tasks_count=len(new_tasks)
        print "%s new tasks loaded"%(new_tasks_count)
        if new_tasks_count<GLOBAL.batchsize:
            GLOBAL.newtask_open=0
    
    
    try:
        language=gasl.GrabLanguages(crawlerbody,'/'.join([task[1],task[2]]))
        Tools.SaveData.UpdateData(conn,[language],"user_has_repo",["language"],"id=%s"%(task[0]))
        print("successfully updated api details of repo %s"%(task[0]))
        
    except SystemExit,e:
        pass
    except Exception,e:
        traceback.print_exc()
        if 404 in e and hasattr(e,'data') and 'Not Found' in e.data['message']:
            Tools.SaveData.UpdateData(conn,['Not Found'],"user_has_repo",["language"],"id=%s"%(task[0]))
            return
        if 451 in e:
            Tools.SaveData.UpdateData(conn,['Access Blocked'],"user_has_repo",["language"],"id=%s"%(task[0]))
            return
        if 403 in e and hasattr(e,'data') and 'blocked' in e.data['message']:
            Tools.SaveData.UpdateData(conn,['Access Blocked'],"user_has_repo",["language"],"id=%s"%(task[0]))
            return
        if 403 in e and hasattr(e,'data') and 'abuse' in e.data['message']:
            errortasks.append(task)
            #print "abuse error."
            time.sleep(random()*5+5)
            print("abuse stop finished")
        else:
            errortasks.append(task)
            print("unexpected error(run). error task %s has been put back to taskque"%(task[0]))
    
    GLOBAL.finishedcount+=1

    
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
    paras["threadnumber"]=30
    
    #不开启webdriver
    paras["webdriver"]=None
    paras["loadimage"]=False
    
    #使用github账号
    paras["github_account"]=True
    
    #是否自动创建表单，paras["conn_settings"]为None时必须设为None
    paras["db_construction"]=None
         
    #Crawler对象的其他初始化操作(登陆之类的)
    paras["crawler_initialize"]=CrawlerInitialize
    
    return paras

def create_queue():
    
    GLOBAL.newtask_open=1
    GLOBAL.batchsize=1000
    GLOBAL.finishedcount=0
    GLOBAL.nextbatchbegin=1
    #读取任务信息
    tasks=LoadTasks(GLOBAL.batchsize+100)
    #构建任务队列
    que=Queue.Queue()
    loaded_items_count=0
    for task in tasks:
        que.put(task)
        loaded_items_count+=1
    print loaded_items_count,"items has been loaded"
    del tasks
    
    return que


def CrawlerInitialize(crawlerbody):
    pass

def LoadTasks(batchsize=10000):
    conn=Tools.DatabaseSupport.GenerateConn(dbname=GLOBAL.dbname,host=GLOBAL.host,user=GLOBAL.user,passwd=GLOBAL.passwd,port=GLOBAL.port,charset=GLOBAL.charset)
    tasks=Tools.LoadData.LoadDataByCmd(conn,"select id,name,owned_repo from user_has_repo where id>=%s and language is null limit %s"%(GLOBAL.nextbatchbegin,batchsize))
    conn.close()
    
    GLOBAL.nextbatchbegin=tasks[-1][0]+1
    return tasks


def main():
    Spider.main(get_paras(),create_queue,run,mode=1)

main()