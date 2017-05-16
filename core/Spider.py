# -*- coding: utf-8 -*-
"""
Created on Thu Mar 09 15:17:11 2017

@author: Gavin
"""

from sys import path
path.append("../")
import dbmanagement
import Crawler
import threading
from os import system
import time
import traceback
import Tools

#线程运行
def CrawlBegin(paras,threadname,taskque,crawl_function):
    download_count=0
    restart_count=0
    
    #若捕捉到错误status=0，则重新生成实例Crawler则打印错误，循环
    #直至收到任务完成信号status=1，循环停止
    while True:
        try:
            print threadname,"successfully started"
            c=Crawler.Crawler(threadname,paras)
            status,download_count_iter=c.Crawling(threadname,taskque,crawl_function)
            download_count+=download_count_iter
            if status==1:
                print threadname,"successfully finished",time.ctime()
                break
            restart_count+=1
        except Exception,e:
            print "(Spider)",e
            traceback.print_exc()
            continue
    print threadname,"finished. restart count:",restart_count
    print '\t',"download count:",download_count

#主函数，程序开始，创建线程。每个线程调用CrawlBegin函数
def main(paras,create_queue,crawl_function,mode=1):
    #对参数进行补全
    paras=ParasComplement(paras)
    #根据paras["db_construction"]确定是否调用dbmanagement创建表单
    if paras["db_construction"]!=None:
        conn=Tools.DatabaseSupport.GenerateConn(dbname=paras["conn_settings"]["dbname"],
                                                host=paras["conn_settings"]["host"],
                                                port=paras["conn_settings"]["port"],
                                                user=paras["conn_settings"]["user"],
                                                passwd=paras["conn_settings"]["passwd"],
                                                charset=paras["conn_settings"]["charset"])
        tablenames=Tools.DatabaseSupport.GetTableNames(conn)
        dbmanagement.db_construction(conn.cursor(),tablenames)
        conn.commit()
        conn.close()
    
    #创建任务队列
    taskque=create_queue()
    threads=[]
    threadnumber=paras["threadnumber"]
    
    
        
    
    if mode==1:#运行模式
        for i in range(threadnumber):
            '''
            y=floor(i/6)*300
            x=(i%6)*200
            windowpara=(180,300,x,y)
            '''
            
            t=threading.Thread(target=CrawlBegin,args=(paras,"Thread-%s"%(i+1),taskque,crawl_function))
            t.setDaemon(True)
            threads.append(t)
            t.start()
            time.sleep(1)
        i=0
        for t in threads:
            i+=1
            t.join()
            print "Thread-%s"%(i),"has been joined"
    elif mode==2:#调试模式，以主线程运行爬虫
        CrawlBegin(paras,"MainThread",taskque,crawl_function)

    print "successfully finished"
    system("pause")

#参数补全
def ParasComplement(paras):
    
    if "github_account" not in paras:
        paras["github_account"]=None
    
    if "webdriver" not in paras:
        paras["webdriver"]=None
    if "loadimage" not in paras:
        paras["loadimage"]=True
    
    
    conn_settings={'host':"localhost",
                   'dbname':"mysql",
                   'port':3306,
                   'user':'root',
                   'passwd':'123456',
                   'charset':'utf8'}
    if "conn_settings" not in paras:
        paras["conn_settings"]=None
    elif paras["conn_settings"]==None:
        pass
    else:
        for key,value in paras["conn_settings"].items():
            conn_settings[key]=value
        paras["conn_settings"]=conn_settings
    
    if "db_construction" not in paras:
        paras["db_construction"]=None
    elif paras["db_construction"]==True:
        paras["db_construction"]=dbmanagement.db_construction
    
    if "crawler_initialize" not in paras:
        paras["crawler_initialize"]=None

    if "taskque_format" not in paras:
        paras["taskque_format"]=None
    
    return paras