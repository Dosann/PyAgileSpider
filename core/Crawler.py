# -*- coding: utf-8 -*-
"""
Created on Thu Mar 09 11:19:58 2017

@author: Gavin
"""

import MySQLdb
import Tools
import traceback

class Crawler:
    
    def __init__(self,paras):
        
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
            if account==None:
                print "no available account"
                print "thread exits"
                exit(999)
            self.g=Tools.GithubAccountManagement.CreateG(account[1],account[2])
            self.g.per_page=100
            self.gaccount=account
        
        #是否开启selenium模拟浏览器webdriver
        if paras["webdriver"]!=None:
            self.driver=Tools.SeleniumSupport.CreateWebdriver(paras["webdriver"])
        else:
            self.driver=None
        
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
    
    def Crawling(self,threadname,taskque,crawl_function):
        download_count=0
        
        while not taskque.empty():
            try:
                #创建错误任务队列
                errortasks=[]
                #开始爬取
                crawl_function(threadname=threadname,taskque=taskque,crawlerbody=self,errortasks=errortasks)
            except Exception,e:
                print e
                #traceback.print_exc()
                print threadname,"Error when crawling"
                #将错误任务队列中的任务重新加入任务队列
                for errortask in errortasks:
                    taskque.put(errortask)
                print "Failed mission has been put back into que"
                if self.conn!=None:
                    self.conn.close()
                if self.driver!=None:
                    self.driver.quit()
                #返回失败信息、此次执行Crawling函数的成功下载数
                return 0,download_count
            
            download_count+=1
                
                
        #队列已空，返回成功信息，程序结束
        if self.conn!=None:
            self.conn.close()
        if self.driver!=None:
            self.driver.quit()
        return 1,download_count
        
