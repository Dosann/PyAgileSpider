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
import time
import Queue


#从队列中获取任务，编写与该任务相关的信息提取代码
def crawl_userdetails(threadname,taskque,crawlerbody,errortasks):
    global t_data_name,columns,xpaths

    conn=crawlerbody.conn
    driver=crawlerbody.driver
    
    
    taskid,url=taskque.get()
    try:
        driver.get(url)
    except Exception,e:
        print e
        print threadname,"failed when turning page"
        return
    
    details=[taskid]
    for xpath in xpaths:
        details.append(Tools.SeleniumSupport.GetTextByXpath(driver,xpath))
    details=[details]
    
    
    #储存
    Tools.SaveData.SaveData(conn,details,t_data_name,columns)
    print threadname,"successfully saved usernames of task",taskid,time.ctime()

#设置参数
def get_paras():
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
    #使用的github账号
    
    paras["github_account"]=None
         
    paras["db_construction"]=True
    
    
    return paras

#创建队列
def create_queue():
    global t_urllist_name,t_xpath_name,t_data_name,xpaths,columns
    
    conn=Tools.DatabaseSupport.GenerateConn("test",host="10.2.1.26")
    
    xpath_entrys=Tools.LoadData.LoadDataByCmd(conn,"select element_name,xpath from %s"%(t_xpath_name))
    #动态创建数据表单
    tablenames=Tools.DatabaseSupport.GetTableNames(conn)
    if t_data_name not in tablenames:
        cmd="""create table %s(id int primary key"""%(t_data_name)
        for xpath_entry in xpath_entrys:
            cmd+=""",%s text"""%(xpath_entry[0])
        cmd+=""")"""
        Tools.DatabaseSupport.CreateTable(conn,cmd)
    
    xpaths=map(lambda x:x[1],xpath_entrys)
    columns=map(lambda x:x[0],Tools.LoadData.LoadDataByCmd(conn,"desc %s"%(t_data_name)))
        
    #读取已完成的任务列表
    hasfinished_tasks=set(map(lambda x:x[0],Tools.LoadData.LoadDataByCmd(conn,"select id from %s"%(t_data_name))))
    #读取任务信息
    tasks=Tools.LoadData.LoadDataByCmd(conn,"select id,url from %s"%(t_urllist_name))
    #构建任务队列
    que=Queue.Queue()
    omited_items_count=0
    task_count=0
    for task in tasks:
        if task[0] not in hasfinished_tasks:
            task_count+=1
            que.put(task)
        else:
            omited_items_count+=1
    print omited_items_count,"items has been omited"
    print task_count,"tasks has been loaded"
    del hasfinished_tasks
    del tasks
            
    
    return que

# 程序执行入口

def main(t_urllist_name1,t_xpath_name1,t_data_name1):
    global t_urllist_name,t_xpath_name,t_data_name
    t_urllist_name=t_urllist_name1
    t_xpath_name=t_xpath_name1
    t_data_name=t_data_name1
    Spider.main(get_paras(),create_queue,crawl_userdetails,mode=1)


main(t_urllist_name1="t_urllist",t_xpath_name1="t_xpath",t_data_name1="t_data")