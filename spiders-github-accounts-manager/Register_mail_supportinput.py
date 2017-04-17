# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 13:18:39 2017
@author: duxin
Email: duxin_be@outlook.com

"""
from sys import path
path.append("../")
from core import Tools
import time

conn=Tools.DatabaseSupport.GenerateConn(dbname="grabgithub",host='10.2.1.26')
accounts=Tools.GithubAccountManagement.GetGithubAccounts(conn,select_condition="status='unverified'")
conn.close()

content=map(lambda x:(x[1].split('@')[0],x[4]),accounts)
conn=Tools.DatabaseSupport.GenerateConn("grabgithub")
nicknames=["sp0321"]*len(content)
for i in range(len(content)):
    nicknames[i]+=str(i+1)
    print nicknames[i]
print content

webdriver=Tools.SeleniumSupport.CreateWebdriver("Chrome")


for i in range(0,len(content)):
    print "now account",i
    webdriver.get("https://mail.163.com/")
    
    webdriver.switch_to_frame("x-URS-iframe")
    
    inputboxes=webdriver.find_elements_by_class_name("inputbox")
    ib1=inputboxes[0].find_element_by_xpath("""//div[2]/input""")
    ib1.clear()
    ib1.send_keys(content[i][0])
    ib2=inputboxes[1].find_element_by_xpath("""//div[2]/input[2]""")
    ib2.clear()
    ib2.send_keys(content[i][1])
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="dologin"]""")
    
    print u"邮箱验证码:"
    verification=raw_input()
    if verification!="":
        ele=webdriver.find_element_by_xpath("""//*[@id="login-form"]""")
        webdriver.find_element_by_xpath("""//div[4]/div[2]/div[1]/input""").send_keys(verification)
    
    print u"按回车键输入账号密码:"
    raw_input()
    webdriver.switch_to_window(webdriver.window_handles[1])
    Tools.SeleniumSupport.WaitUntilPresence(webdriver,"""//*[@id="login_field"]""")
    webdriver.find_element_by_xpath("""//*[@id="login_field"]""").send_keys(content[i][0]+"@163.com")
    webdriver.find_element_by_xpath("""//*[@id="password"]""").send_keys('a123456')
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="login"]/form/div[4]/input[3]""")
    
    if u"Your account has been flagged." in unicode(webdriver.page_source):
        print u"请完成退出操作，并回车。"
        raw_input()
        webdriver.switch_to_window(webdriver.window_handles[0])
        Tools.SaveData.UpdateData(conn,("flagged",time.strftime("%Y%m%d-%H%M%S")),"github_accounts",["status","update_time"],"id=%s"%(accounts[i][0]))
        continue
    else:
        Tools.SaveData.UpdateData(conn,("unchecked",time.strftime("%Y%m%d-%H%M%S")),"github_accounts",["status","update_time"],"id=%s"%(accounts[i][0]))
    
    time.sleep(1)
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="js-pjax-container"]/div[1]/div/div/a[2]""")
    Tools.SeleniumSupport.WaitUntilPresence(webdriver,"""//*[@id="repository_name"]""")
    webdriver.find_element_by_xpath("""//*[@id="repository_name"]""").send_keys(content[i][0])
    webdriver.find_element_by_xpath("""//*[@id="repository_description"]""").send_keys(content[i][0])
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="new_repository"]/div[4]/button""")
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="user-links"]/li[3]/a/span""")
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="user-links"]/li[3]/div/div/form/button""")
                                                        
    webdriver.close()
    webdriver.switch_to_window(webdriver.window_handles[0])
    
    webdriver.switch_to_default_content()
    ele=webdriver.find_element_by_xpath("""/html/body/header/div[1]""")
    Tools.SeleniumSupport.PushButtonByXpath(ele,"""//ul[1]/li[18]""")
    
    
    
    print i,"finished"

print "all finished"

    