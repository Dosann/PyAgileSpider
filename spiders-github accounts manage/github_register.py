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
from string import zfill


def crawl_userdetails(threadname,taskque,crawlerbody,errortasks):
    #从队列中获取任务，编写与该任务相关的信息提取代码

    webdriver=crawlerbody.driver
    conn=crawlerbody.conn
    if taskque.empty():
        print "taskqueue is empty. program ends"
        return
    accountid,accountname,nickname=taskque.get()
    time.sleep(5)
    
    try:
        #根据accountname,nickname注册github账号
        webdriver.get("https://github.com/")
        
        tb1=webdriver.find_element_by_xpath("""//*[@id="user[login]"]""")
        tb1.clear()
        tb1.send_keys(nickname)
        tb2=webdriver.find_element_by_xpath("""//*[@id="user[email]"]""")
        tb2.clear()
        tb2.send_keys(accountname)
        tb3=webdriver.find_element_by_xpath("""//*[@id="user[password]"]""")
        tb3.clear()
        tb3.send_keys("a123456")
        Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""/html/body/div[4]/div[1]/div/div/div[2]/div[1]/form/button""")
        
        Tools.SeleniumSupport.WaitUntilClickable(webdriver,"""//*[@id="js-pjax-container"]/div/div[2]/div/form/button""")
        Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="js-pjax-container"]/div/div[2]/div/form/button""")
        
        Tools.SeleniumSupport.WaitUntilPresence(webdriver,"""//*[@id="answers_98_choice_476"]""")
        webdriver.find_element_by_xpath("""//*[@id="answers_98_choice_476"]""").click()
        webdriver.find_element_by_xpath("""//*[@id="answers_99_choice_464"]""").click()
        webdriver.find_element_by_xpath("""//*[@id="answers_99_choice_467"]""").click()
        webdriver.find_element_by_xpath("""//*[@id="answers_100_choice_471"]""").click()
        webdriver.find_element_by_xpath("""//*[@id="js-pjax-container"]/div/div[2]/div/form/fieldset[4]/div/div/div[1]/input[1]""").send_keys('programming\n')
        Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="js-pjax-container"]/div/div[2]/div/form/input""")
        Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="user-links"]/li[3]/a/span""")
        Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="user-links"]/li[3]/div/div/form/button""")
        print "account %s has been successfully registered"%(accountid)
        Tools.SaveData.UpdateData(conn,("unverified",time.strftime("%Y%m%d-%H%M%S")),"github_accounts",["status","update_time"],"id=%s"%(accountid))
        time.sleep(5)
    except Exception,e:
        print e
        print "error while registering. current account:",accountid
        Tools.SaveData.UpdateData(conn,("flagged",time.strftime("%Y%m%d-%H%M%S")),"github_accounts",["status","update_time"],"id=%s"%(accountid))
    '''
    #检测该账号是否可用，若可用，则更新数据库
    g=github.Github(accountname,"a123456")
    if g.rate_limiting[1]>=5000:
        print "account %s is available"%(accountid)
        Tools.SaveData.UpdateData(conn,("available",time.strftime("%Y%m%d-%H%M%S")),"github_accounts",["status","update_time"],"id=%s"%(accountid))
    else:
        print "account %s is not available"%(accountid)
        Tools.SaveData.UpdateData(conn,("flagged",time.strftime("%Y%m%d-%H%M%S")),"github_accounts",["status","update_time"],"id=%s"%(accountid))
    '''

def get_paras():
    #设置参数
    paras={}
    #数据库访问设置
    
    paras["conn_settings"]={"dbname":"grabgithub",
                             'host':"10.2.1.26",
                             'user':'root',
                             'passwd':'123456'}
    #paras["conn_settings"]=None
    #线程数
    paras["threadnumber"]=8
    #不开启webdriver
    paras["webdriver"]="Chrome"
    #使用的github账号列表
    paras["accountlist"]=None
    
    
    return paras


def create_queue():
    #创建队列
    limit_number=40
    #读取任务信息
    conn=Tools.DatabaseSupport.GenerateConn(dbname="grabgithub",host='10.2.1.26')
    accounts=Tools.GithubAccountManagement.GetGithubAccounts(conn,select_condition="status='unregistered'",number_limit=limit_number)
    conn.close()
    #构建任务队列
    que=Queue.Queue()
    

    for i in range(len(accounts)):
        nickname=Tools.OtherSupport.GenerateRandomString(10)+zfill(accounts[i][0],5)
        que.put((accounts[i][0],accounts[i][1],nickname))
    return que

if __name__=='__main__':
    Spider.main(get_paras(),create_queue,crawl_userdetails,mode=1)