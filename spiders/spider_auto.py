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
import dbmanagement
import time
import Queue
from random import random


#从队列中获取任务，编写与该任务相关的信息提取代码
def crawl_userdetails(threadname,taskque,crawlerbody,errortasks):
    global columns

    conn=crawlerbody.conn
    g=crawlerbody.g
    
    while 1:
        try:
            ratelimit=g.rate_limiting[1]
        except:
            print "rate_limiting failed"
            continue
        break
    
    while ratelimit<100:
        print threadname,"current account get flagged:",crawlerbody.gaccount[0]
        account=Tools.GithubAccountManagement.OccupyAnAccount(conn)
        if account!=None:
            crawlerbody.g=Tools.GithubAccountManagement.CreateG(account[1],account[2])
            g=crawlerbody.g
            print threadname,"has changed account:",crawlerbody.gaccount[0]
        else:
            print "no available account in accountque.",time.ctime()
            print threadname,"get locked"
            time.sleep(180)
    
    '''
    #数据库中设置的varchar长度上限
    length_constraint=[int,50,50]
    '''
    
    taskid,username=taskque.get()
    try:
        user=g.get_user(username)
        followers=user.get_followers()
    except Exception,e:
        print e
        if 404 in e:#无法找到用户名（用户已注销），添加空记录，继续下一个任务
            print "can not found user %s"%(username)
        if 403 in e:
            errortasks.append((taskid,username))
            print "abuse error."
            time.sleep(random()*5+5)
            print "abuse stop finished"
        else:
            #未知错误，将该任务添加到错误任务列表，继续下一个任务
            errortasks.append((taskid,username))
            print "unexpected error. task %s has been put back to taskque"%(taskid)
        return
    relas=[]
    for follower in followers:
        relas.append((username,unicode(follower)[17:-2]))
        #print unicode(follower)[17:-2]
    
    '''
    for i in range(14):
        item=entry[i]
        if type(item)==unicode or type(item)==str:
            entry[i]=item[:length_constraint[i]]
    details.append(entry)
    '''
    
    #储存
    columns=["name","followername"]
    Tools.SaveData.SaveData(conn,relas,"user_relas_followed",columns)
    print threadname,g.rate_limiting,"successfully saved usernames of task",taskid,time.ctime()

#设置参数
def get_paras():
    paras={}
    #数据库访问设置
    paras["conn_settings"]={"dbname":"grabgithub",
                             'host':"10.2.1.26",
                             'user':'root',
                             'passwd':'123456'}
    #线程数
    paras["threadnumber"]=30
    #不开启webdriver
    paras["webdriver"]=None
    #使用的github账号
    
    paras["github_account"]=True
         
    paras["db_construction"]=None
    
    
    return paras

#创建队列
def create_queue():
    global t_urllist_name,t_xpath_name,t_data_name,columns
    
    conn=Tools.DatabaseSupport.GenerateConn("grabgithub",host="10.2.1.26")
    
    #动态创建数据表单
    tablenames=Tools.DatabaseSupport.GetTableNames(conn)
    if t_data_name not in tablenames:
        xpaths=Tools.LoadData.LoadDataByCmd(conn,"select * from %s"%(t_xpath_name))
        xpaths_count=len(xpaths)            
        cmd="""create table %s(
                id int primary key"""%(t_data_name)
        for i in range(xpaths_count):
            cmd+=""",%s text"""%(xpaths[i][1])
        cmd+=""")"""
        Tools.DatabaseSupport.CreateTable(conn,cmd)
    columns=map(lambda x:x[0],Tools.LoadData.LoadDataByCmd(conn,"desc %s"%(t_data_name)))
        
    #读取已完成的任务列表
    hasfinished_tasks=set(map(lambda x:x[0],Tools.LoadData.LoadDataByCmd(conn,"select id from %s"%(t_data_name))))
    #读取任务信息
    tasks=Tools.LoadData.LoadDataByCondition(conn,"active_users_10",["name"],rangeid)
    #构建任务队列
    que=Queue.Queue()
    omited_items_count=0
    task_count=0
    for username in usernames:
        if username[0] not in hasfinished_tasks:
            task_count+=1
            que.put([task_count,username[0]])
        else:
            omited_items_count+=1
    print omited_items_count,"items has been omited"
    print task_count,"tasks has been loaded"
    del hasfinished_tasks
    del usernames
            
    
    return que

# 程序执行入口
def main(t_urllist_name1,t_xpath_name1,t_data_name1):
    global t_urllist_name,t_xpath_name,t_data_name
    t_urllist_name=t_urllist_name1
    t_xpath_name=t_xpath_name1
    t_data_name=t_data_name1
    Spider.main(get_paras(),create_queue,crawl_userdetails,mode=1)