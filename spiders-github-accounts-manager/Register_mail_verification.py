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
accounts=Tools.GithubAccountManagement.GetGithubAccounts(conn,select_condition="status='flagged' and mail_passwd!='a123456'",time_recall=-60,number_limit=30)
conn.close()

content=map(lambda x:(x[1].split('@')[0],x[4]),accounts)
nicknames=["sp0321"]*len(content)
for i in range(len(content)):
    nicknames[i]+=str(i+1)
    print nicknames[i]
print content

webdriver=Tools.SeleniumSupport.CreateWebdriver("Chrome")

for i in range(4,len(content)):
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
    
    verification=raw_input('verification:')
    if verification!="":
        ele=webdriver.find_element_by_xpath("""//*[@id="login-form"]""")
        webdriver.find_element_by_xpath("""//div[4]/div[2]/div[1]/input""").send_keys(verification)
    
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="dologin"]""")
    time.sleep(1)
    
    Tools.SeleniumSupport.WaitUntilPresence(webdriver,"""//*[@id="cnt-box2"]""")
    ele=webdriver.find_element_by_xpath("""//*[@id="cnt-box2"]""")
    Tools.SeleniumSupport.WaitUntilClickable(webdriver,"""//div/div/div[3]/a[1]""")
    ele.find_element_by_xpath("""//div/div/div[3]/a[1]""").click()
    time.sleep(1)
    
    Tools.SeleniumSupport.WaitUntilPresence(webdriver,"""//*[@id="dvNavContainer"]""")
    ele=webdriver.find_element_by_xpath("""//*[@id="dvNavContainer"]""")
    Tools.SeleniumSupport.PushButtonByXpath(ele,"""//nav/div[2]/ul/li[1]""")
    print "succeeded"
    Tools.SeleniumSupport.WaitUntilPresence(webdriver,"""//*[@id="dvContentContainer"]""")
    ele=webdriver.find_element_by_xpath("""//*[@id="dvContentContainer"]""")
    print "succeeded2"
    time.sleep(1)
    Tools.SeleniumSupport.PushButtonByXpath(ele,"""//div[1]/div[2]/div/div[1]/div[4]/div[2]""")
    
    Tools.SeleniumSupport.WaitUntilPresence(ele,"""//div[1]/div[3]/div/div[1]/div[4]/div/iframe""")
    iframe=ele.find_element_by_xpath("""//div[1]/div[3]/div/div[1]/div[4]/div/iframe""")
    iframename=iframe.get_attribute('name')
    print iframename
    time.sleep(1)
    webdriver.switch_to_frame(iframename)
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""/html/body/div/a""")
    
    time.sleep(1)
    webdriver.switch_to_window(webdriver.window_handles[1])
    Tools.SeleniumSupport.WaitUntilPresence(webdriver,"""//*[@id="login_field"]""")
    webdriver.find_element_by_xpath("""//*[@id="login_field"]""").send_keys(content[i][0]+"@163.com")
    webdriver.find_element_by_xpath("""//*[@id="password"]""").send_keys('a123456')
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="login"]/form/div[4]/input[3]""")
    
    time.sleep(1)
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="js-pjax-container"]/div[1]/div/div/a[2]""")
    Tools.SeleniumSupport.WaitUntilPresence(webdriver,"""//*[@id="repository_name"]""")
    webdriver.find_element_by_xpath("""//*[@id="repository_name"]""").send_keys(content[i][0])
    webdriver.find_element_by_xpath("""//*[@id="repository_description"]""").send_keys(content[i][0])
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="new_repository"]/div[4]/button""")
    Tools.SeleniumSupport.PushButtonByXpath(webdriver,"""//*[@id="js-repo-pjax-container"]/div[1]/div[1]/ul/li[2]/div/form[2]/button""")
    
    webdriver.close()
    webdriver.switch_to_window(webdriver.window_handles[0])
    
    webdriver.switch_to_default_content()
    ele=webdriver.find_element_by_xpath("""/html/body/header/div[1]""")
    Tools.SeleniumSupport.PushButtonByXpath(ele,"""//ul[1]/li[18]""")
    
    
    
    time.sleep(2)

    