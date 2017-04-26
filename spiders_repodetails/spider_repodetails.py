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

import GithubWebspiderSupport as gws
import GithubApispiderSupport as gas
import GLOBAL


def run(taskque,crawlerbody,errortasks):
    #从队列中获取任务，编写与该任务相关的信息提取代码
    date=GLOBAL.date
    
    driver=crawlerbody.driver
    conn=crawlerbody.conn
    
    #从队列中读取1个任务
    task=taskque.get()
    repofullname=task[1]+'/'+task[2]
    taskstatus=list(task[3:5])   
    
    
    
    try:
        if task[3]==False:
            apidetails=gas.GrabApidetails(crawlerbody,repofullname)
            details=[task[0],task[1],task[2]]+apidetails+[1]
            Tools.SaveData.UpdateData(conn,details,"repodetails_%s"%(date),
                                    ["id","user","repo","repoid","size","has_downloads","has_issues","has_wiki",
                                    "private","createtime","pushtime","updatetime","recordtime",
                                    "ownerid","ownertype","contributors","codesize","langcount",
                                    "language","mlangsize","mlangper","seclang","slangsize","slangper",
                                    "thilang","tlangsize","tlangper","_api_finished"],"id=%s"%(task[0]))
            taskstatus[0]=1
        print("successfully updated api details of repo %s"%(task[0]))
        
        if task[4]==False:
            webdetails_1=gws.GrabWeb1(driver,repofullname)
            webdetails_2=gws.GrabWeb2(driver,repofullname)
            webdetails_3=gws.GrabWeb3(driver,repofullname)
            details=webdetails_1+webdetails_2+webdetails_3+[1]
            while 1: #检查是否成功过滤掉readme中的emoji，若失败则将其设为'*contains emoji*'
                try:
                    Tools.SaveData.UpdateData(conn,details,"repodetails_%s"%(date),
                                                  ["watchers","stars","forks","mainbranch_commits","branches","releases","license","readme",
                                                   "open_issues","close_issues","open_pull","close_pull","_web_finished"],
                                                   "id=%s"%task[0])
                except Exception,e:
                    print(crawlerbody.threadname,e)
                    details[7]=u'*contains emoji*'
		    continue
                break
            taskstatus[1]=1
        print("thread %s successfully updated web details of repo %s"%(crawlerbody.threadname,task[0]))
    except SystemExit,e:
        print("task %s: "%(task[0]),e)
    except Exception,e:
	print(e)
        traceback.print_exc()
        if 404 in e and hasattr(e,'data') and 'Not Found' in e.data['message']:
            taskstatus=[None,None]
        if 403 in e and hasattr(e,'data') and 'abuse' in e.data['message']:
            errortasks.append(task)
            #print "abuse error."
            time.sleep(random()*5+5)
            print("abuse stop finished")
        else:
            errortasks.append(task)
            print("unexpected error(run). error task %s has been put back to taskque"%(task[0]))
    Tools.SaveData.UpdateData(conn,taskstatus,"repodetails_%s"%(date),["_api_finished","_web_finished"],"id=%s"%(task[0]))
    

    
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
    paras["webdriver"]="PhantomJS"
    paras["loadimage"]=False
    
    #使用github账号
    paras["github_account"]=True
    
    #是否自动创建表单，paras["conn_settings"]为None时必须设为None
    paras["db_construction"]=True
         
    #Crawler对象的其他初始化操作(登陆之类的)
    paras["crawler_initialize"]=CrawlerInitialize
    
    return paras

def create_queue():
    date=GLOBAL.date
    #读取任务信息
    conn=Tools.DatabaseSupport.GenerateConn(dbname='grabgithub',host='10.2.1.26')
    tasks=Tools.LoadData.LoadDataByCmd(conn,"select id,user,repo,_api_finished,_web_finished from repodetails_%s where _api_finished=0 or _web_finished=0"%(date))
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
    crawlerbody.driver.get("https://www.github.com/login")
    username=Tools.SeleniumSupport.GetElementByXpath(crawlerbody.driver,"""//*[@id="login_field"]""")
    username.clear()
    username.send_keys(crawlerbody.gaccount[1])
    password=Tools.SeleniumSupport.GetElementByXpath(crawlerbody.driver,"""//*[@id="password"]""")
    password.clear()
    password.send_keys(crawlerbody.gaccount[2])
    Tools.SeleniumSupport.GetElementByXpath(crawlerbody.driver,"""//*[@id="login"]/form/div[4]/input[3]""").click()
    


def main():
    GLOBAL.date='20170503'
    Spider.main(get_paras(),create_queue,run,mode=1)

main()