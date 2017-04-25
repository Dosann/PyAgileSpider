# -*- coding: utf-8 -*-
"""
Created on Thu Mar 09 11:19:58 2017

@author: Gavin
"""

import MySQLdb
import Tools
import traceback

class Crawler:

    def __init__(self,threadname,paras):

        self.threadname=threadname

        if paras["conn_settings"]!=None:
            self.conn=MySQLdb.Connection(
                    host=paras["conn_settings"]["host"],
                    port=paras["conn_settings"]["port"],
                    user=paras["conn_settings"]["user"],
                    passwd=paras["conn_settings"]["passwd"],
                    db=paras["conn_settings"]["dbname"],
                    charset=paras["conn_settings"]["charset"])
        else:
            self.conn=None

        #是否使用Github账号
        if paras["github_account"]!=None:
            account=Tools.GithubAccountManagement.OccupyAnAccount(self.conn)
            print threadname,"tried to fetch an account"
            if account==None:
                print "no available account"
                print self.threadname,"exits"
                exit(999)
            self.g=Tools.GithubAccountManagement.CreateG(account[1],account[2])
            self.g.per_page=100
            self.gaccount=account
        else:
            self.g=None
            self.gaccount=None

        #是否开启selenium模拟浏览器webdriver
        if paras["webdriver"]!=None:
            self.driver=Tools.SeleniumSupport.CreateWebdriver(paras["webdriver"])
        else:
            self.driver=None

        #对该Crawler对象的其他初始化操作
        if paras["crawler_initialize"]!=None:
            paras["crawler_initialize"](self)
        
    """
    def Login(self):
        self.driver.get(self.baseurl)
        username=self.driver.find_element_by_name("TextBoxAccount")
        username.clear()
        username.send_keys("Kevin DU")
        password=self.driver.find_element_by_name("Password")
        password.clear()
        password.send_keys("a19960407")
        self.driver.find_element_by_id("ImageButtonLogin").click()
    """

    def Crawling(self,threadname,taskque,run):
        download_count=0
        status=1

        while not taskque.empty():
            #创建错误任务队列
            errortasks=[]
            try:
                #开始爬取
                run(taskque=taskque,crawlerbody=self,errortasks=errortasks)
            except Exception,e:
                print "(Crawler)",e
                #traceback.print_exc()
                print threadname,"Error when crawling"
                print "Failed mission has been put back into que"
                status=0
                break

            #将错误任务队列中的任务重新加入任务队列
            for errortask in errortasks:
                taskque.put(errortask)
            download_count+=1

        #队列已空，返回成功信息，程序结束
        if self.g!=None:
            Tools.GithubAccountManagement.ReleaseAnAccount(self.conn,self.gaccount)
            print threadname,"has released an account"
        if self.conn!=None:
            self.conn.close()
        if self.driver!=None:
            self.driver.quit()

        return status,download_count

