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
    
    
    try:
        language=gasl.GrabLanguages(crawlerbody,'/'.join([task[1],task[2]]))
        Tools.SaveData.SaveData(conn,[[task[0],language]],"repo_language_27w",["id","language"])
        print("successfully updated api details of repo %s"%(task[0]))
        
    except SystemExit,e:
        pass
    except Exception,e:
        traceback.print_exc()
        if 404 in e and hasattr(e,'data') and 'Not Found' in e.data['message']:
            Tools.SaveData.SaveData(conn,[[task[0],'*Error: Not Found*']],"repo_language_27w",["id","language"])
            return
        if 451 in e:
            Tools.SaveData.SaveData(conn,[[task[0],'*Error: Access Blocked*']],"repo_language_27w",["id","language"])
            return
        if 403 in e and hasattr(e,'data') and 'blocked' in e.data['message']:
            Tools.SaveData.SaveData(conn,[[task[0],'*Error: Access Blocked*']],"repo_language_27w",["id","language"])
            return
        if 403 in e and hasattr(e,'data') and 'abuse' in e.data['message']:
            errortasks.append(task)
            #print "abuse error."
            time.sleep(random()*5+5)
            print("abuse stop finished")
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
    paras["threadnumber"]=40
    
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
    
    #构建任务队列
    taskque=LoadTaskque()
    return taskque


def CrawlerInitialize(crawlerbody):
    pass

def LoadTaskque():
    startid=int(raw_input('input startid: '))
    endid=int(raw_input('input endid: '))
    conn=Tools.DatabaseSupport.GenerateConn(dbname=GLOBAL.dbname,host=GLOBAL.host,user=GLOBAL.user,passwd=GLOBAL.passwd,port=GLOBAL.port,charset=GLOBAL.charset)
    tasks=Tools.LoadData.LoadDataByCmd(conn,"select id,user,repo from repo_active_20170508 where id>=%s and id<=%s"%(startid,endid))
    tasks_finished=set(map(lambda x:x[0],Tools.LoadData.LoadDataByCmd(conn,"select id from repo_language_27w")))
    conn.close()
    
    taskque=Tools.OtherSupport.TaskqueGeneration(tasks,tasks_finished=tasks_finished,key=0)
    del tasks
    del tasks_finished
    
    return taskque


def main():
    Spider.main(get_paras(),create_queue,run,mode=1)

main()