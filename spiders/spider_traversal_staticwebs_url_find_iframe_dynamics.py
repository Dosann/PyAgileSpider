﻿# -*- coding: utf-8 -*-
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
import urllib


def run(taskque,crawlerbody,errortasks):
    #从队列中获取任务，编写与该任务相关的信息提取代码
    global initial_url,domain_name,urlset,current_id,url_match_mode,ifrset

    conn=crawlerbody.conn
    driver=crawlerbody.driver
    
    #从队列中读取1个任务
    task=taskque.get()
    print task
    try:
        driver.get(task[2])
        html=driver.page_source
    except Exception,e:
        print e
        print traceback.print_exc()
        print "error task %s has been put back to taskque"%(task[0])
        return
    if task[1]<=1000000:
        soup=Tools.BsSupport.SoupGeneration(html)
        eles_href=Tools.BsSupport.FindElementsWithAttr(soup,'href')
        eles_src=Tools.BsSupport.FindElementsWithAttr(soup,'src')
        urls_href=Tools.BsSupport.UrlComplement(map(lambda x:x.attrs['href'],eles_href),task[2])
        urls_src=Tools.BsSupport.UrlComplement(map(lambda x:x.attrs['src'],eles_src),task[2])
        eles_iframe=soup.find_all('iframe')
        for iframe in eles_iframe:
            if 'id' in iframe.attrs:
                iframe_name=iframe.attrs['id']
                #iframe_url=iframe.attrs['src']
                if iframe_name not in ifrset:
                    Tools.SaveData.SaveData(conn,[[iframe_name]],"t_iframes",["iframe_name"])
                    ifrset.add(iframe_name)
                driver.switch_to_iframe(iframe.attrs['id'])
                html_attr
                
        urls=[]
        for url in urls_href+urls_src:
            if url.split('/')[-1].split('.')[-1] not in ['css','js']:
                urls.append(url)
            
        print "found %s urls"%(len(urls))
        newurls=[]
        for url in urls:
            if url not in urlset:
                urlsplit=url.split('/')
                if len(urlsplit)<3:
                    continue
                urlsplit2=urlsplit[2].split('.')
                if (url_match_mode==1 and '.'.join(urlsplit2)==domain_name or '.'.join(urlsplit2[1:])==domain_name):
                    current_id+=1
                    c_id=current_id
                    newurls.append([c_id,url,'unvisited'])
                    urlset.add(url)
                    taskque.put((c_id,task[0]+1,url))
        
        
        Tools.SaveData.SaveData(conn,newurls,"t_urls",["id","url","status"])
        Tools.SaveData.UpdateData(conn,['visited'],"t_urls",["status"],"id=%s"%(task[0]))
    
def get_paras():
    #设置参数
    paras={}
    #数据库访问设置
    paras["conn_settings"]={"dbname":"test",
                             'host':"590ab5bb84735.sh.cdb.myqcloud.com",
                             'user':'cdb_outerroot',
                             'port':14803,
                             'passwd':'Aa123456'}
    #线程数
    paras["threadnumber"]=10
    
    #不开启webdriver
    paras["webdriver"]="PhantomJS"
    
    #使用github账号
    paras["github_account"]=None
    
    #是否自动创建表单
    paras["db_construction"]=True
    
    
    return paras


def create_queue():
    global initial_url,domain_name,urlset,current_id,ifrset
    
    
    conn=Tools.DatabaseSupport.GenerateConn(dbname='test',host='590ab5bb84735.sh.cdb.myqcloud.com',user='cdb_outerroot',port=14803,passwd='Aa123456')
    temp=Tools.LoadData.LoadDataByCmd(conn,"select id,url from t_urls")
    if len(temp)==0:
        Tools.SaveData.SaveData(conn,[['%s'%(initial_url),'unvisited']],'t_urls',['url','status'])
    urls=Tools.LoadData.LoadDataByCmd(conn,"select id,url from t_urls where status='unvisited'")
    current_id=int(Tools.LoadData.LoadDataByCmd(conn,"select max(id) from t_urls")[0][0])
    
    ifrset=set(map(lambda x:x[0],Tools.LoadData.LoadDataByCmd(conn,"select iframe_name from t_iframes")))
    
    
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


def main(initial_url1,domain_name1,url_match_mode1):
    global initial_url,domain_name,url_match_mode
    initial_url=initial_url1
    domain_name=domain_name1
    url_match_mode=url_match_mode1
    Spider.main(get_paras(),create_queue,run,mode=2)


main("""http://www.douban.com/""",'douban.com',url_match_mode1=2)
# url_match_mode 1:全域名匹配(course.shlll.net) 2:匹配从第二格开始的部分(shlll.net)





def ExtractValuableInfos(driver,ypath,conn,task,taskque):
    global urlset,ifrset,domain_name,current_id
    
    eles_a=driver.find_elements_by_tag_name('a')
    
    [urls_src,urls_dynam_src]=Tools.BsSupport.UrlComplement(map(lambda x:x.attrs['src'],eles_src),task[2])
    newurls=[]
    for url in urls_href+urls_src:
        if url not in urlset:
            urlsplit=url.split('/')
            if len(urlsplit)<3:
                continue
            urlsplit2=urlsplit[2].split('.')
            if (url_match_mode==1 and '.'.join(urlsplit2)==domain_name or '.'.join(urlsplit2[1:])==domain_name):
                current_id+=1
                c_id=current_id
                newurls.append([c_id,url,'unvisited'])
                urlset.add(url)
                taskque.put((c_id,task[0]+1,url))
    Tools.SaveData.SaveData(conn,newurls,"t_urls",["id","url","status"])
    
    
    eles_iframe=soup.find_all('iframe')
    for iframe in eles_iframe:
        if 'id' in iframe.attrs:
            iframe_name=iframe.attrs['id']
            #iframe_url=iframe.attrs['src']
            if iframe_name not in ifrset:
                Tools.SaveData.SaveData(conn,[[iframe_name]],"t_iframes",["iframe_name"])
                ifrset.add(iframe_name)
            driver.switch_to_iframe(iframe.attrs['id'])
