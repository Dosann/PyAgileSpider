# -*- coding: utf-8 -*-
'''
create time: 2017/5/6 11:31
author: duxin
site: 
email: duxin_be@outlook.com
'''


from sys import path
path.append("../")
from core import Tools
from core import Spider
import Queue
import traceback
import time
import random

from spiders_reporeadme import GithubWebspiderSupport as gws
import GLOBAL


def run(taskque,crawlerbody,errortasks):
    #从队列中获取任务，编写与该任务相关的信息提取代码
    date=GLOBAL.date

    if crawlerbody.threadname=='Thread-1':
        data_1=Tools.LoadData.LoadDataByCmd(crawlerbody.conn,"select readme from repo_readme where id=1")
        print("current readme of task 1: ",data_1[:20])
        time.sleep(20)
        return

    conn=crawlerbody.conn
    driver=crawlerbody.driver

    #从队列中读取1个任务
    task=taskque.get()
    repofullname=task[1]+'/'+task[2]

    try:
        readme=[gws.GrabWeb1(driver,repofullname)]
    except SystemExit,e:
        print("task %s: "%(task[0]),e)
        if e.message=='ERROR: WHOA THERE':
            errortasks.append(task)
            return
        if e.message=='ERROR: README FOUND':
            errortasks.append(task)
            return
    except Exception,e:
        traceback.print_exc()
        print(e)
        traceback.print_exc()
        if 404 in e and hasattr(e,'data') and 'Not Found' in e.data['message']:
            readme=['*404:%s*'%(e)]
        if 451 in e:
            readme=['*451:%s*'%(e)]
        if 403 in e and hasattr(e,'data') and 'blocked' in e.data['message']:
            readme=['*403:%s*'%(e)]
        if 403 in e and hasattr(e,'data') and 'abuse' in e.data['message']:
            readme=[None]
            errortasks.append(task)
            print "abuse error."
            time.sleep(random()*5+5)
            print("abuse stop finished")
        else:
            readme=[None]
            errortasks.append(task)
            print("unexpected error(run). error task %s has been put back to taskque"%(task[0]))
    if readme==[None]:
        return
    try:
        Tools.SaveData.UpdateData(conn,readme,"repo_readme",["readme"],"id=%s"%(task[0]))
    except Exception,e:
        traceback.print_exc()
        print(crawlerbody.threadname,e)
        readme=u'*contains emoji or something*'
        Tools.SaveData.UpdateData(conn,readme,"repo_readme",["readme"],"id=%s"%(task[0]))
    print("thread %s successfully updated all details of repo %s"%(crawlerbody.threadname,task[0]))



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
    paras["webdriver"]="PhantomJS"
    paras["loadimage"]=False

    #使用github账号
    paras["github_account"]=True

    #是否自动创建表单，paras["conn_settings"]为None时必须设为None
    paras["db_construction"]=None

    #Crawler对象的其他初始化操作(登陆之类的)
    paras["crawler_initialize"]=CrawlerInitialize

    return paras

def create_queue():
    date=GLOBAL.date
    #读取任务信息
    conn=Tools.DatabaseSupport.GenerateConn(dbname=GLOBAL.dbname,host=GLOBAL.host,user=GLOBAL.user,passwd=GLOBAL.passwd,port=GLOBAL.port,charset=GLOBAL.charset)
    startid=int(raw_input('input start task id: '))
    endid=int(raw_input('input end task id: '))
    tasks=Tools.LoadData.LoadDataByCmd(conn,"select id,user,repo,readme from repo_readme where id>=%s and id<=%s and readme is null"%(startid,endid))
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
    Spider.main(get_paras(),create_queue,run,mode=2)

main()