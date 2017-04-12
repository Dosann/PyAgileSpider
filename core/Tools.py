# -*- coding: utf-8 -*-
"""
Created on Thu Mar 09 11:19:57 2017

@author: Gavin
"""

import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.common.desired_capabilities as DC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import re
import string
from string import strip
from MySQLdb import Connection
import github
from os import getcwd
import random
import datetime

class SeleniumSupport:
    
    #按键事件
    @staticmethod
    def PushButtonByXpath(driver,xpath):
        SeleniumSupport.WaitUntilClickable(driver,xpath)
        driver.find_element_by_xpath(xpath).click()
    
    #抽取数字
    @staticmethod
    def Count(xpath,driver=None,url=None):
        if driver==None:
            driver=SeleniumSupport.CreateWebdriver("PhantomJS")
            driver.get(url)
        SeleniumSupport.WaitUntilPresence(driver,xpath)
        count=int(Filter.FilterNumber(driver.find_element_by_xpath(xpath).text))
        return count
    
    #计算某个container中某个item的数量
    @staticmethod
    def CountItems(driver,container_xpath,item_classname=None,item_tagname=None):
        SeleniumSupport.WaitUntilPresence(driver,container_xpath)
        container=driver.find_element_by_xpath(container_xpath)
        if item_classname!=None:
            items=container.find_elements_by_class_name(item_classname)
        elif item_tagname!=None:
            items=container.find_elements_by_tag_name(item_tagname)
        else:
            items=[]
        count=len(items)
        return count,items
    
    #等待直到某个对象的出现
    @staticmethod
    def WaitUntilPresence(driver,xpath):#通过xpath定位
        locator=(By.XPATH,xpath)
        WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located(locator))
    @staticmethod
    def WaitUntilPresenceByTagname(driver,tagname):#通过tagname定位
        locator=(By.TAG_NAME,tagname)
        WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located(locator))
    @staticmethod
    def WaitUntilPresenceByClassname(driver,classname):#通过tagname定位
        locator=(By.CLASS_NAME,classname)
        WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located(locator))
    
    #等待直到某个对象可点击
    @staticmethod
    def WaitUntilClickable(driver,xpath):#通过xpath定位
        locator=(By.XPATH,xpath)
        WebDriverWait(driver,20,1.5).until(EC.element_to_be_clickable(locator))
        time.sleep(2)
    
    #等待直到翻页完成
    @staticmethod
    def WaitUntilTurnpageFinished(driver,reference):
        while driver.find_element_by_xpath("""//*[@id="divlist"]/ul/li[1]/div[1]/a""").text==reference:
            time.sleep(0.5)
    
    #获取某个对象的text
    @staticmethod
    def GetTextByXpath(driver,xpath,option=None):#通过xpath定位
        if option=="Abandon":#若该对象在超时时间内仍为加载出来（可能不存在），则舍弃，返回None
            try:
                SeleniumSupport.WaitUntilPresence(driver,xpath)
                txt=driver.find_element_by_xpath(xpath).text
                return strip(txt)
            except:
                return None
        else:
            SeleniumSupport.WaitUntilPresence(driver,xpath)
            txt=driver.find_element_by_xpath(xpath).text
            return strip(txt)
    @staticmethod
    def GetTextByTagname(driver,tagname,option=None):#通过tagname定位
        if option=="Abandon":
            try:
                SeleniumSupport.WaitUntilPresenceByTagname(driver,tagname)
                txt=driver.find_element_by_tag_name(tagname).text
                return strip(txt)
            except:
                return None
        else:
            SeleniumSupport.WaitUntilPresenceByTagname(driver,tagname)
            txt=driver.find_element_by_tag_name(tagname).text
            return strip(txt)
            
    #获取某个对象的某个attribute
    @staticmethod
    def GetAttributeByXpath(driver,xpath,attr):#通过xpath定位
        SeleniumSupport.WaitUntilPresence(driver,xpath)
        txt=driver.find_element_by_xpath(xpath).get_attribute(attr)
        return txt
    @staticmethod
    def GetAttributeByTagname(driver,tagname,attr):#通过tagname定位
        SeleniumSupport.WaitUntilPresenceByTagname(driver,tagname)
        txt=driver.find_element_by_tag_name(tagname).get_attribute(attr)
        return txt
    
    #页面跳转，仅支持“输入页码→点击翻转”类型的翻转操作
    @staticmethod
    def JumpPage(driver,page,tb_xpath,btn_xpath=None):
        SeleniumSupport.WaitUntilPresence(driver,tb_xpath)
        pagetextbox=driver.find_element_by_xpath(tb_xpath)
        pagetextbox.clear()
        pagetextbox.send_keys(str(page))
        time.sleep(0.5)
        if btn_xpath==None:
            pagetextbox.send_keys(Keys.ENTER)
        else:
            SeleniumSupport.WaitUntilClickable(driver,btn_xpath)
            driver.find_element_by_xpath(btn_xpath).click()
        
    #创建一个selenium的模拟浏览器webdriver
    @staticmethod
    def CreateWebdriver(drivertype,path="..\\core\\webdrivers",loadimage=True,downloadpath=None):
        if drivertype=="PhantomJS":
            if loadimage==False:
                dcap=dict(DC.DesiredCapabilities.PHANTOMJS)
                dcap["phantomjs.page.settings.loadImages"]=False
                driver=webdriver.PhantomJS(desired_capabilities=dcap,executable_path=path+"\\phantomjs.exe")
            else:
                driver=webdriver.PhantomJS(executable_path=path+"\\phantomjs.exe")
        elif drivertype=="Chrome":
            if downloadpath!=None:
                chromeOptions=webdriver.ChromeOptions()
                prefs={"download.default_directory":downloadpath}
                chromeOptions.add_experimental_option("prefs",prefs)
                driver = webdriver.Chrome(chrome_options=chromeOptions,executable_path=path+"\\chromedriver.exe")
            else:
                driver=webdriver.Chrome(executable_path=path+"\\chromedriver.exe")
        elif drivertype=="Firefox":
            driver=webdriver.Firefox(executable_path=path+"\\geckodriver.exe")
        elif drivertype=="Ie":
            driver=webdriver.Ie(executable_path=path+"\\IEDriverServer.exe")
        return driver

class LoadData:
    
    #辅助函数： 生成特定格式字符串
    #['id','name','age','gender']→"(id,name,age,gender)"
    @staticmethod
    def GenerateColumns(columns,bracket=True):
        if columns=='*':
            return '*'
        columnsize=len(columns)
        columns=tuple(columns)
        s="%s,"*(columnsize-1)+"%s"
        if bracket==True:
            s="("+s+")"
        s=s%(columns)
        return s
    
    #从数据库获取通过id的范围获取特定字段
    @staticmethod
    def LoadDataByIdRange(conn,tablename,columns,rangeinfo):
    #conn: 数据库链接 Connection实例
    #columns格式: ["id","username","age","location"...]
    #rangeinfo格式: (333,10000)
        cur=conn.cursor()
        columns=LoadData.GenerateColumns(columns,bracket=False)
        cmd="""select %s from %s where id>=%s and id<=%s"""%(columns,tablename,rangeinfo[0],rangeinfo[1])
        columncount=len(columns.split(','))
        cur.execute(cmd)
        data=cur.fetchall()
        data=map(lambda x:x[0:columncount],data)
        cur.close()
        return data
    
    #从数据库中按条件获取一条或多条数据
    @staticmethod
    def LoadDataByCondition(conn,tablename,columns,condition,number_limit=None):
    #condition格式： "username=duxin and age<40 or gender=male..."
        cur=conn.cursor()
        columns=LoadData.GenerateColumns(columns,bracket=False)
        cmd="""select %s from %s%s"""%(columns,tablename,condition)
        if number_limit!=None:
            cmd+=" limit %s"%(number_limit)
        cur.execute(cmd)
        data=cur.fetchall()
        cur.close()
        return data
    
    #从数据库中按输入的控制命令读取数据
    @staticmethod
    def LoadDataByCmd(conn,cmd):
        cur=conn.cursor()
        cur.execute(cmd)
        data=cur.fetchall()
        cur.close()
        return data


class SaveData:
    
    #辅助函数： 生成特定格式字符串
    #['id','name','age','gender']→"(id,name,age,gender)"
    @staticmethod
    def GenerateColumns(columns,bracket=True):
        columnsize=len(columns)
        columns=tuple(columns)
        s="%s,"*(columnsize-1)+"%s"
        if bracket==True:
            s="("+s+")"
        s=s%(columns)
        return s
    
    #插入数据
    @staticmethod
    def SaveData(conn,data,tablename,columns):
    #data格式： [(1,'duxin',21,'male',...),(2,'xxx',30,'female',...),...]
    #columns格式： ['id','name','age','gender'...]
        cur=conn.cursor()
        #data=map(lambda x:map(lambda y:(y==None) and "null" or y,x),data)
        cmd="""insert into """+tablename+SaveData.GenerateColumns(columns)+""" values"""+SaveData.GenerateColumns(('%s',)*len(columns))
        cur.executemany(cmd,data)
        conn.commit()
        cur.close()
    
    #根据condition更新数据
    @staticmethod
    def UpdateData(conn,data,tablename,columns,condition):
    #data格式： (1,'duxin',21,'male',...)         与函数Savedata不同，此处data中只包含一行数据
    #columns格式： ['id','name','age','gender'...]
        cur=conn.cursor()
        equalstr=""
        columncount=len(columns)
        columntype=map(lambda x:type(x),columns)
        for i in range(columncount):
            if columntype[i]==str or columntype[i]==unicode:
                equalstr+="""%s="%s","""%(columns[i],data[i])
            elif columntype[i]==type(None):
                equalstr+="""%s=null,"""%(columns[i])
            else:
                equalstr+="""%s=%s,"""%(columns[i],data[i])
        equalstr=equalstr[:-1]
        cmd="""update %s set %s where %s"""%(tablename,equalstr,condition)
        cur.execute(cmd)
        conn.commit()
        cur.close()

class DatabaseSupport:
    
    #生成一个数据库链接
    @staticmethod
    def GenerateConn(dbname,host="localhost",port=3306,user="root",passwd="123456",charset='utf8'):
        conn=Connection(
            host=host,
            port=port,
            user=user,
            passwd=passwd,
            db=dbname,
            charset=charset)
        return conn
    
    #获取数据库中的表名
    @staticmethod
    def GetTableNames(conn):
        cur=conn.cursor()
        cur.execute("""show tables""")
        tablenames=map(lambda ta:ta[0],cur.fetchall())
        cur.close()
        return tablenames
    
    #创建表单
    @staticmethod
    def CreateTable(conn,cmd):
        cur=conn.cursor()
        cur.execute(cmd)
        conn.commit()
        cur.close()
        return True

        
class Filter:
    
    #过滤一条字符串中的数字
    @staticmethod
    def FilterNumber(s,returncount=1,removecomma=False):
    #returncount表示返回识别出的数字的前几项
    #removecomma表示在识别前是否移除逗号','和'，'
        if type(s)!=str and type(s)!=unicode:
            return None
        if removecomma==True:
            s=s.replace(u',','').replace(u'，','')
        result=re.findall('\d+',s)
        if len(result)==0:
            print "error: can't find numbers"
            return None
        else:
            if returncount==1:
                return result[0]
            else:
                return result[0:returncount]

class GithubAccountManagement:
    
    #读取github账号密码
    @staticmethod
    def GetGithubAccounts(conn,account_range=None,select_condition=None,number_limit=None,time_recall=None):
    #accountrange格式： (3,9)
        
        condition_text=""
        has_condition=False
        if account_range!=None or select_condition!=None:
            has_condition=True
            condition_text+=" where "
        if account_range!=None:
            condition_text+="id>=%s and id<=%s"%(account_range[0],account_range[1])
        if select_condition!=None:
            if account_range!=None:
                condition_text+=" and "
            condition_text+=select_condition
        if time_recall!=None:
            recall_time=datetime.datetime.now()+datetime.timedelta(minutes=time_recall)
            recall_time=recall_time.strftime("%Y%m%d-%H%M%S")
            if has_condition==True:
                condition_text+=" and update_time>='%s'"%(recall_time)
            else:
                condition_text+=" where update_time>='%s'"%(recall_time)
        if number_limit!=None:
            condition_text+=" limit %s"%(number_limit)
        
        accounts=LoadData.LoadDataByCondition(conn,"github_accounts",["id","github_account","github_passwd","mail_type","mail_passwd","status","update_time"],condition_text)
        
        return accounts
    
    #返回一组账号的(账号，密码，剩余请求次数，生成的请求句柄)
    @staticmethod
    def GetGithubAccountStatus(conn,accountlist):
    #accountlist格式 [('账号1','密码1'),('账号2','密码2'),...]
        existing_accounts=[]
        non_existing_accounts=[]
        account_status=[]
        current=0
        while current<len(accountlist):
            account=accountlist[current]
            try:
                g=github.Github(account[1],account[2])
                ratelimit=g.rate_limiting
                existing_accounts.append((account,ratelimit,g))
                print "has linked account %s"%(current+1)
            except Exception,e:
                if 401 in e:
                    non_existing_accounts.append(account)
                    print "account %s exists not"%(current+1)
                    current+=1
                    continue
                if 403 in e:
                    print e
                    print "403 error. waiting..."
                    time.sleep(random.randint(20,40))
                    continue
                    
            current+=1
        available_accounts=[]
        for account in existing_accounts:
            if account[1][1]==5000:
                available_accounts.append(account)
        all_accounts=GithubAccountManagement.GetGithubAccounts(conn)
        all_accounts_name=set(map(lambda x:x[1],all_accounts))
        available_accounts_name=set(map(lambda x:x[0][1],available_accounts))
        for account in existing_accounts:
            if account[0][1] not in all_accounts_name:
                SaveData.SaveData(conn,[account[0][1:3]],"github_accounts",["github_account","github_passwd"])
            if account[0][1] in available_accounts_name:
                print "account %s is available"%(account[0][0])
                SaveData.UpdateData(conn,("available",time.strftime("%Y%m%d-%H%M%S")),"github_accounts",["status","update_time"],"id=%s"%(account[0][0]))
                account_status.append((account[0][0],"working"))
            else:
                print "account %s is flagged"%(account[0][0])
                SaveData.UpdateData(conn,("flagged",time.strftime("%Y%m%d-%H%M%S")),"github_accounts",["status","update_time"],"id=%s"%(account[0][0]))
                account_status.append((account[0][0],"flagged"))
        for account in non_existing_accounts:
            if account[1] not in all_accounts_name:
                print "account %s is unregistered"%(account[0])
                SaveData.SaveData(conn,[account[1:3]+("unregistered",time.strftime("%Y%m%d-%H%M%S"))],"github_accounts",["github_account","github_passwd","status","update_time"])
                account_status.append((account[0],"unregistered"))
            else:
                print "account %s is unregistered"%(account[0])
                SaveData.UpdateData(conn,account[1:3]+("unregistered",time.strftime("%Y%m%d-%H%M%S")),"github_accounts",["github_account","github_passwd","status","update_time"],"id=%s"%(account[0]))
                account_status.append((account[0],"unregistered"))
        
        
        
        return account_status
    
    #将原始“邮箱-邮箱密码”格式账号导入数据库
    @staticmethod
    def ImportRawEmailAccounts(conn,filename,default_passwd="a123456",split_char='----'):
        path=getcwd()
        path=path[:-len(path.split('\\')[-1])]+"files\\"+filename
        f=open(path,'r')
        email_accounts=f.readlines()
        f.close()
        email_accounts=map(lambda x:x[:-1].split(split_char),email_accounts)
        email_accounts=map(lambda x:(x[0],default_passwd,x[1],x[0].split('@')[1],time.strftime("%Y%m%d-%H%M%S")),email_accounts)
        all_accounts=GithubAccountManagement.GetGithubAccounts()
        all_accounts_name=set(map(lambda x:x[1],all_accounts))
        for email_account in email_accounts:
            if email_account[0] not in all_accounts_name:
                SaveData.SaveData(conn,[email_account],"github_accounts",["github_account","github_passwd","mail_passwd","mail_type","update_time"])
            else:
                print "account %s already exists"%(email_account[0])
    
    @staticmethod
    def OccupyAnAccount(conn):
        account=LoadData.LoadDataByCondition(conn,"github_accounts","*"," where status='available'",number_limit=1)
        if len(account)==0:
            print "no available github accounts any more"
            return None
        account=account[0]
        SaveData.UpdateData(conn,("occupied",time.strftime("%Y%m%d-%H%M%S")),"github_accounts",["status","update_time"],"id=%s"%(account[0]))
        return account
    
    @staticmethod
    def CreateG(account,passwd):
        g=github.Github(account,passwd)
        return g
    

class OtherSupport:
    
    @staticmethod
    def GenerateRandomString(length=10):
        s=''.join(random.sample(string.ascii_letters + string.digits, length))
        return s