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
from random import random


def crawl_userdetails(threadname,taskque,crawlerbody,errortasks):
    #从队列中获取任务，编写与该任务相关的信息提取代码

    conn=crawlerbody.conn
    g=crawlerbody.g
    tasks=[]
    
    
    while g.rate_limiting[1]<100:
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
    
    
    #从队列中读取100一百个任务
    for i in range(100):
        if taskque.empty()==True:
            print "taskque is empty",threadname
            break
        tasks.append(taskque.get())
    if len(tasks)==0: #如果没有读取到任务，则直接返回
        return
    details=[]
    #数据库中设置的varchar长度上限
    length_constraint=[int,int,50,30,19,19,int,int,int,50,int,int,int,12]
    for i in range(len(tasks)):
        taskid,username=tasks[i]
        try:
            user=g.get_user(username)
            rd=user.raw_data
        except Exception,e:
            print e
            if 404 in e:#无法找到用户名（用户已注销），添加空记录，继续下一个任务
                entry=[taskid]+[None]*13
                details.append(entry)
                continue
            if 403 in e:
                errortasks.append((taskid,username))
                print "abuse error."
                time.sleep(random()*5+5)
                print "abuse stop finished"
                continue
            else:
                #未知错误，将该任务添加到错误任务列表，继续下一个任务
                errortasks.append((taskid,username))
                print "unexpected error. task %s has been put back to taskque"%(taskid)
                continue
        
        entry=[taskid,rd["id"],rd["login"],rd["company"],unicode(rd["created_at"]),unicode(rd["updated_at"]),rd["followers"],rd["following"],
                 rd["hireable"],rd["location"],rd["public_gists"],rd["public_repos"],rd["site_admin"],rd["type"]]
        for i in range(14):
            item=entry[i]
            if type(item)==unicode or type(item)==str:
                entry[i]=item[:length_constraint[i]]
        details.append(entry)
    
    #一次储存100条数据
    columns=["id","userid","name","company","created_at","updated_at","followercount","followingcount",
             "hireable","location","public_gists","public_repos","site_admin","type"]
    Tools.SaveData.SaveData(conn,details,"userdetails",columns)
    print threadname,g.rate_limiting,"successfully saved usernames of task. from",details[0][0],"to",details[-1][0],time.ctime()

def get_paras():
    #设置参数
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
    
    
    return paras


def create_queue():
    #创建队列
    conn=Tools.DatabaseSupport.GenerateConn("grabgithub",host="10.2.1.26")
    rangeid=(22000001,24000000)
    #读取已完成的任务列表
    hasfinished_tasks=set(map(lambda x:x[0],Tools.LoadData.LoadDataByIdRange(conn,"userdetails",["id"],rangeid)))
    #读取任务信息
    usernames=Tools.LoadData.LoadDataByIdRange(conn,"usernames",["id","username"],rangeid)
    #构建任务队列
    que=Queue.Queue(maxsize=int((rangeid[1]-rangeid[0]+1)*1.2))
    omited_items_count=0
    for username in usernames:
        if username[0] not in hasfinished_tasks:
            que.put(username)
        else:
            omited_items_count+=1
    print omited_items_count,"items has been omited"
    del hasfinished_tasks
    del usernames
            
    
    return que

if __name__=='__main__':
    Spider.main(get_paras(),create_queue,crawl_userdetails,mode=1)