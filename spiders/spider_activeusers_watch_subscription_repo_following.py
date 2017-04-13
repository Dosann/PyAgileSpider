# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 14:24:55 2017
@author: duxin
Email: duxin_be@outlook.com

"""

from sys import path
path.append("../")
from sys import exit
from core import Tools
from core import Spider
import time
import Queue
from random import random


#从队列中获取任务，编写与该任务相关的信息提取代码
def crawl_userdetails(threadname,taskque,crawlerbody,errortasks):

    conn=crawlerbody.conn
    g=crawlerbody.g
    
    user_status="finished"
    

    
    while 1:
        while 1:
            try:
                ratelimit=g.rate_limiting[0]
            except:
                print "rate_limiting failed"
                continue
            break
        if ratelimit<2000
        print threadname,"current account get flagged:",crawlerbody.gaccount[0]
        account=Tools.GithubAccountManagement.OccupyAnAccount(conn)
        if account!=None:
            crawlerbody.g=Tools.GithubAccountManagement.CreateG(account[1],account[2])
            crawlerbody.gaccount=account
            g=crawlerbody.g
            print threadname,"has changed account:",crawlerbody.gaccount[0]
        else:
            print "no available account in accountque.",time.ctime()
            print threadname,"exits"
            exit(999)
    
    '''
    #数据库中设置的varchar长度上限
    length_constraint=[int,50,50]
    '''
    
    taskid,username=taskque.get()
    try:
        user=g.get_user(username)
        gsubs=user.get_subscriptions()
        gstars=user.get_starred()
        grepos=user.get_repos()
        gfollowing=user.get_following()
        rela_subs=[]
        rela_stars=[]
        rela_repos=[]
        rela_followings=[]
        for gsu in gsubs:
            rela_subs.append((username,unicode(gsu)[22:-2][:200]))
        for gst in gstars:
            rela_stars.append((username,unicode(gst)[22:-2][:200]))
        for gre in grepos:
            rela_repos.append((username,unicode(gre)[22:-2].split('/')[1][:200]))
        for gfing in gfollowing:
            rela_followings.append((username,unicode(gfing)[17:-2]))
    except Exception,e:
        print e
        if 404 in e:#无法找到用户名（用户已注销），添加空记录，继续下一个任务
            user_status="not found"
            print "can not found user %s"%(username)
        elif 403 in e:
            errortasks.append((taskid,username))
            print "abuse error."
            time.sleep(random()*5+5)
            print "abuse stop finished"
        else:
            #未知错误，将该任务添加到错误任务列表，继续下一个任务
            errortasks.append((taskid,username))
            print "unexpected error. task %s has been put back to taskque"%(taskid)
        return
    
    '''
    for i in range(14):
        item=entry[i]
        if type(item)==unicode or type(item)==str:
            entry[i]=item[:length_constraint[i]]
    details.append(entry)
    '''
    
    #储存
    
    Tools.SaveData.SaveData(conn,rela_subs,"user_subscribes_repo",["name","subbed_repo"])
    Tools.SaveData.SaveData(conn,rela_stars,"user_stars_repo",["name","starred_repo"])
    Tools.SaveData.SaveData(conn,rela_repos,"user_has_repo",["name","owned_repo"])
    Tools.SaveData.SaveData(conn,rela_repos,"user_relas_following",["name","following_user"])
    Tools.SaveData.UpdateData(conn,[user_status],"tasks_user",["status"],"id=%s"%(taskid))
    
    print threadname,g.rate_limiting,"successfully saved usernames of task",taskid,time.ctime()

#设置参数
def get_paras():
    paras={}
    #数据库访问设置
    paras["conn_settings"]={'dbname':"grabgithub",
                             'host':"10.2.1.26",
                             'user':'root',
                             'passwd':'123456'}
    #线程数
    paras["threadnumber"]=5
    #不开启webdriver
    paras["webdriver"]=None
    #使用的github账号
    
    paras["github_account"]=True
         
    paras["db_construction"]=True
    
    
    return paras

#创建队列
def create_queue():
    #复制任务队列
    conn=Tools.DatabaseSupport.GenerateConn("grabgithub",host="10.2.1.26")
    cur=conn.cursor()
    cmd="select id from tasks_user"
    item_count=cur.execute(cmd)
    if item_count==0:
        cmd="select id,name from active_users_10"
        cur.execute(cmd)
        data=cur.fetchall()
        data=map(lambda x:(x[0],x[1],"unfinished"),data)
        cmd="insert into tasks_user(id,name,status) values(%s,%s,%s)"""
        #数据分批导入
        data_volume=len(data)
        batch=data_volume/1000+1
        for i in range(batch):
            cur.executemany(cmd,data[1000*i:1000*(i+1)])
            conn.commit()
    
    #读取任务信息
    start_id=raw_input(unicode("输入id最小值:",'utf-8').encode('gbk'))
    end_id=raw_input(unicode("输入id最大值:",'utf-8').encode('gbk'))
    users=Tools.LoadData.LoadDataByCmd(conn,"select id,name from tasks_user where status='unfinished' and id>=%s and id<=%s"%(start_id,end_id))
    #构建任务队列
    que=Queue.Queue()
    task_count=0
    for user in users:
        task_count+=1
        que.put([user[0],user[1]])
    print task_count,"tasks has been loaded"
    del users
            
    
    return que

# 程序执行入口
if __name__=='__main__':
    Spider.main(get_paras(),create_queue,crawl_userdetails,mode=1)