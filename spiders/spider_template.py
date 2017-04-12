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


def run(threadname,taskque,crawlerbody,errortasks):
    #从队列中获取任务，编写与该任务相关的信息提取代码

    driver=crawlerbody.driver
    
    
    #从队列中读取1个任务
    task=taskque.get()
    try:
        #print task[1]
        driver.get(task[1])
        content=Tools.SeleniumSupport.GetTextByXpath(driver,"""/html/body/div[1]/table[2]/tbody/tr/td[1]/table/tbody/tr/td/div[2]/div""")
        print task[0],content
    except Exception,e:
        print e
        print traceback.print_exc()
        errortasks.append(task)
        print "error task %s has been put back to taskque"%(task[0])
    
def get_paras():
    #设置参数
    paras={}
    #数据库访问设置
    paras["conn_settings"]={"dbname":"test",
                             'host':"10.2.1.26",
                             'user':'root',
                             'passwd':'123456'}
    #线程数
    paras["threadnumber"]=10
    
    #不开启webdriver
    paras["webdriver"]="PhantomJS"
    
    #使用github账号
    paras["github_account"]=None
    
    #是否自动创建表单
    paras["db_construction"]=True
    
    
    return paras


def create_queue():
    #创建队列
    conn=Tools.DatabaseSupport.GenerateConn(dbname="test",host="10.2.1.26")
    rangeid=(1,100)
    #读取任务信息
    tasks=Tools.LoadData.LoadDataByIdRange(conn,"courseabstracts",["id","name"],rangeid)
    #构建任务队列
    que=Queue.Queue()
    loaded_items_count=0
    for task in tasks:
        que.put(task)
        loaded_items_count+=1
    print loaded_items_count,"items has been loaded"
    del tasks
            
    
    return que

if __name__=='__main__':
    Spider.main(get_paras(),create_queue,run,mode=1)