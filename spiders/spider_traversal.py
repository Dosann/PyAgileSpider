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
import re
import time


def run(threadname,taskque,crawlerbody,errortasks):
    #从队列中获取任务，编写与该任务相关的信息提取代码
    global initial_url,domain_name,urlset,visited_urlset

    driver=crawlerbody.driver
    conn=crawlerbody.conn
    
    #从队列中读取1个任务
    task=taskque.get()
    print task
    try:
        #print task[1]
        driver.get(task[1])
    except Exception,e:
        print e
        print traceback.print_exc()
        errortasks.append(task)
        print "error task %s has been put back to taskque"%(task[0])
    if task[0]<=100:
        urls=re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')",driver.page_source)
        urls=map(lambda x:domain_name+x,urls)
        print "found %s urls"%(len(urls))
        newurls=[]
        for url in urls:
            if url not in urlset:
                newurls.append([url])
                urlset.add(url)
                taskque.put((task[0]+1,url))
        Tools.SaveData.SaveData(conn,newurls,"t_urls",["url"])
    time.sleep(1)
    
def get_paras():
    #设置参数
    paras={}
    #数据库访问设置
    paras["conn_settings"]={"dbname":"test",
                             'host':"10.2.1.26",
                             'user':'root',
                             'passwd':'123456'}
    #线程数
    paras["threadnumber"]=20
    
    #不开启webdriver
    paras["webdriver"]="PhantomJS"
    
    #使用github账号
    paras["github_account"]=None
    
    #是否自动创建表单
    paras["db_construction"]=True
    
    
    return paras


def create_queue():
    global initial_url,domain_name,urlset
    
    conn=Tools.DatabaseSupport.GenerateConn(dbname='test',host='10.2.1.26')
    urlset=set(map(lambda x:x[0],Tools.LoadData.LoadDataByCmd(conn,"select url from t_urls")))
    #创建队列
    que=Queue.Queue()
    for url in urlset:
        que.put((0,url))
    
    return que

def main(initial_url1,domain_name1):
    global initial_url,domain_name
    initial_url=initial_url1
    domain_name=domain_name1
    Spider.main(get_paras(),create_queue,run,mode=1)

main("""http://zx.chnlc.net/Search/Index""",'http://zx.chnlc.net')