# -*- coding: utf-8 -*-
"""
Created on Wed May 31 10:36:29 2017

@author: duxin
"""

from sys import path
path.append("../")
from core import Tools
import time

def isUrl(s):
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
    global surls
    driver.get(url[0][1])
    current_url=driver.current_url
    new_urls=[]
    if len(url)>1:
        for action in url[1:]:
            if action[0]=='iframe':
                driver.switch_to_frame(action[1])
            elif action[0]=='button':
                Tools.SeleniumSupport.WaitUntilClickable(driver,link_text=action[1])
                driver.find_element_by_link_text(action[1]).click()
                time.sleep(1)
                if driver.current_url!=current_url:
                    new_urls.append([['url',driver.current_url]])
                    path=[['url',driver.current_url]]
                else:
                    path=url
                urls_in_new_page=findUrlOfA(driver)
                urls_in_new_page=urlPathComplement(urls_in_new_page,path)
                iframes_in_new_page=findIframes(driver)
                urls_in_new_page+=iframes_in_new_page
                for url_in_new_page in urls_in_new_page:
                    surl_in_new_page=str(url_in_new_page)
                    if surl_in_new_page not in surls:
                        new_urls.append(url_in_new_page)
                        surls.add(surl_in_new_page)
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
            t_iframes.append([['url',driver.current_url]])
    return t_iframes
            




driver=Tools.SeleniumSupport.CreateWebdriver('Chrome')
driver.get('http://course.shlll.net/course/discovery')

ifrs=driver.find_elements_by_tag_name('iframe')
t_iframes=[]
for ifr in ifrs:
    ifr_id=ifr.get_attribute('id')
    if ifr_id==None:
        t_iframes.append([None])
        continue
    
    ifr_src=ifr.get_attribute('src')
    if ifr_src==None:
        ifr_src_valid=False
    if isUrl(ifr_src):
        ifr_src_valid=True
    else:
        ifr_src_valid=False
    t_iframes.append([ifr_id,ifr_src_valid,driver.current_url,ifr_src])

print t_iframes

urls=findUrlOfA(driver)
urls=urlPathComplement(urls,driver.current_url)
for ifr in t_iframes:
    if ifr==None:
        continue
    driver.switch_to_frame(ifr[0])
    path=ifr[1]==True and [['url',ifr[3]]] or [['url',ifr[2]],['iframe',ifr[0]]]
    new_urls=findUrlOfA(driver)
    new_urls2=urlPathComplement(new_urls,path)
    urls+=new_urls2
    driver.switch_to.parent_frame()
print urls


for url in urls:
    if len(url)==1:
        print 'ignoring...'
        continue
    new_urls=turnToElement(driver,url)
    urls.append(new_urls)