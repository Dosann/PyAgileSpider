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
import Levenshtein
import json


def isUrl(s):
    #print "current s:",s
    if s==None:
        return False
    if len(s)==0:
        return False
    if s[:4]=='http':
        return True
    elif s[0]=='/':
        return True
    else:
        return False

def findUrlOfA(driver):
    a_s=driver.find_elements_by_tag_name('a')
    t_as=[]
    for a in a_s:
        a_src=a.get_attribute('href')
        if isUrl(a_src):
            t_as.append([1,a_src])
        else:
            t_as.append([2,a.text])
    return t_as

def urlPathComplement(urls,path):
    urls_compl=[]
    for url in urls:
        if url[0]==1:
            urls_compl.append([['url',url[1]]])
        elif url[0]==2:
            urls_compl.append(path+[['button',url[1]]])
    return urls_compl

def turnToElement(driver,url):
    global urlset
    new_urls=[]
    for action in url:
        print action
        if action[0]=='url':
            print action[1]
            driver.get(action[1])
        elif action[0]=='iframe':
            driver.switch_to_frame(action[1])
        elif action[0]=='button':
            content=driver.find_element_by_tag_name('html').text
            page_url=driver.current_url
            Tools.SeleniumSupport.WaitUntilClickable(driver,link_text=action[1])
            driver.find_element_by_link_text(action[1]).click()
            time.sleep(1)
    if len(url)==1:
        path=[['url',url[0][1]]]
    else:
        # 如果页面url改变，添加url路径；如果url未变，检测页面内容→如果页面内容也未变，不添加该路径；如果页面内容改变，添加点击路径。
        if driver.current_url!=page_url:
            path=[['url',driver.current_url]]
        else:
            if Levenshtein.jaro(driver.find_element_by_tag_name('html').text,content)<0.95:
                path=url
            else:
                return []
    urls_in_new_page=findAllUrls(driver,path)
    for url_in_new_page in urls_in_new_page:
        surl_in_new_page=json.dumps(url_in_new_page)
        if surl_in_new_page not in urlset:
            new_urls.append(url_in_new_page)
            urlset.add(surl_in_new_page)
    return new_urls

def findIframes(driver):
    ifrs=driver.find_elements_by_tag_name('iframe')
    t_iframes=[]
    for ifr in ifrs:
        ifr_id=ifr.get_attribute('id')
        if ifr_id==None:
            continue

        ifr_src=ifr.get_attribute('src')
        if ifr_src==None or not isUrl(ifr_src):
            t_iframes.append([['url',driver.current_url],['iframe',ifr_id]])
            continue
        else:
            t_iframes.append([['url',ifr_src]])
    return t_iframes

def findAllUrls(driver,path):
    t_iframes=findIframes(driver)
    urls=findUrlOfA(driver)
    urls=urlPathComplement(urls,path)
    urls+=t_iframes
    return urls

def filterByDomain(url,domainName,urlMatchMode=1):
    if urlMatchMode==1:
        if url.split('/')[2]==domainName:
            return 'pass'
        else:
            return 'filtered'
    elif urlMatchMode==2:
        if '.'.join(url.split('/')[2].split('.')[1:])==domainName:
            return 'pass'
        else:
            return 'filtered'
        

def run(taskque,crawlerbody,errortasks):
    #从队列中获取任务，编写与该任务相关的信息提取代码
    global initial_url,domain_name,urlset,current_id,url_match_mode,ifrset,tname_urls

    conn=crawlerbody.conn
    driver=crawlerbody.driver
    
    #从队列中读取1个任务
    task=taskque.get()
    print task
    
    try:
        #print "url:%s"%(task[2]),len(task[2]),type(task[2])
        new_urls=turnToElement(driver,json.loads(task[2]))
        if task[1]<=1000000:
            
            data=[]
            for new_url in new_urls:
                if filterByDomain(new_url[0][1],domain_name,url_match_mode)!='pass':
                    continue
                current_id+=1
                new_url_json=json.dumps(new_url)
                taskque.put([current_id,task[1]+1,new_url_json])
                data.append([current_id,new_url_json,'unvisited'])
                
            Tools.SaveData.SaveData(conn,data,"%s"%(tname_urls),['id','url','status'])
            Tools.SaveData.UpdateData(conn,['visited'],"%s"%(tname_urls),['status'],'id=%s'%(task[0]))
    except Exception,e:
        traceback.print_exc()
        print e
        print "error task %s has been put back to taskque"%(task[0])
        return
        
        
        
def get_paras():
    #设置参数
    paras={}
    #数据库访问设置
    paras["conn_settings"]={"dbname":"sentiment",
                             'host':"rm-bp10rf4zreaw5he66o.mysql.rds.aliyuncs.com",
                             'user':'root',
                             'port':3306,
                             'passwd':'Csstsari107'}
    #线程数
    paras["threadnumber"]=10
    
    #不开启webdriver
    paras["webdriver"]="PhantomJS"
    paras["loadimage"]=False
    
    #使用github账号
    paras["github_account"]=None
    
    #是否自动创建表单
    paras["db_construction"]=True
         
    #Crawler对象的其他初始化操作(登陆之类的)
    #paras["crawler_initialize"]=CrawlerInitialize
    
    #是否在redis中读写队列
    paras["taskque_format"]=None
    #paras["taskque_format"]="redis"
    #paras["redis_settings"]={"dbname":0,
    #                         "host":'120.25.107.34',
    #                         "port":6379}
    
    
    return paras


def create_queue():
    global initial_url,domain_name,urlset,current_id,ifrset,tname_urls
    
    initial_url=json.dumps([['url',initial_url]])
    conn=Tools.DatabaseSupport.GenerateConn(dbname='sentiment',host='rm-bp10rf4zreaw5he66o.mysql.rds.aliyuncs.com',user='root',port=3306,passwd='Csstsari107')
    temp=Tools.LoadData.LoadDataByCmd(conn,"select id,url from %s limit 1"%(tname_urls))
    if len(temp)==0:
        Tools.SaveData.SaveData(conn,[['%s'%(initial_url),'unvisited']],'%s'%(tname_urls),['url','status'])
    urls=Tools.LoadData.LoadDataByCmd(conn,"select id,url from %s where status='unvisited'"%(tname_urls))
    current_id=int(Tools.LoadData.LoadDataByCmd(conn,"select max(id) from %s"%(tname_urls))[0][0])
    
    
    conn.close()
    
    #创建队列
    que=Queue.Queue()
    print len(urls)
    if len(urls)==0:
        urlset=set(initial_url)
        task=(0,0,initial_url)
        que.put(task)
    else:
        urlset=set(map(lambda x:x[1],urls))
        for urlid,url in urls:
            que.put((urlid,0,url))
    
    return que


def main(initial_url1,domain_name1,url_match_mode1,tname_urls1):
    global initial_url,domain_name,url_match_mode,tname_urls
    initial_url=initial_url1
    domain_name=domain_name1
    url_match_mode=url_match_mode1
    tname_urls=tname_urls1
    Spider.main(get_paras(),create_queue,run,mode=1)


main("""https://www.dianping.com/shanghai/food""",'dianping.com',url_match_mode1=2,tname_urls1='t_dianping')
# url_match_mode 1:全域名匹配(course.shlll.net) 2:匹配从第二格开始的部分(shlll.net) 3:匹配域名的全部部分(course.shlll.net/course)





