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
    date=GLOBAL.date
    
    conn=crawlerbody.conn
    
    #从队列中读取1个任务
    task=taskque.get()
    
    
    try:
        language=gasl.GrabLanguages(crawlerbody,task[1])
        Tools.SaveData.UpdateData(conn,[language],"repo_languages",["language"],"id=%s"%(task[0]))
        print("successfully updated api details of repo %s"%(task[0]))
        
    except SystemExit,e:
        pass
    except Exception,e:
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
    finally:
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
    paras["threadnumber"]=5
    
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
    conn=Tools.DatabaseSupport.GenerateConn(dbname='grabgithub',host='10.2.1.26')
    tasks=Tools.LoadData.LoadDataByCmd(conn,"select id,repo from repo_languages where language is not null")
    #构建任务队列
    que=Queue.Queue()
    loaded_items_count=0
    for task in tasks:
        que.put(task[0:2])
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
    GLOBAL.date='20170426'
    Spider.main(get_paras(),create_queue,run,mode=1)

main()