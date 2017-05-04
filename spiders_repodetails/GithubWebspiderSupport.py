# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:35:03 2017

@author: duxin
"""


from sys import path
path.append("../")
from core import Tools
import sys


def GrabWeb1(driver,url):
    #需跳转至Web1,挖取proj的 watch,star,fork,mainbranch_commits数 branches数 releases数 license名 编程语言信息
    try:
        driver.get("https://www.github.com/"+url)
    except Exception,e:
        print(e)
        sys.exit("can not load the page: %s."%(url))
        
    try:
        #0 watchers,stars,forks数
        c_watchers=Tools.Filter.FilterNumber(Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-repo-pjax-container"]/div[1]/div[1]/ul/li[1]/form/div[2]/a[2]"""),returncount=1)
        c_stars=Tools.Filter.FilterNumber(Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-repo-pjax-container"]/div[1]/div[1]/ul/li[2]/div/form[2]/a"""),returncount=1)
        c_forks=Tools.Filter.FilterNumber(Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-repo-pjax-container"]/div[1]/div[1]/ul/li[3]/a"""),returncount=1)
        #print(c_watchers,c_stars,c_forks)
    except:
        sys.exit("Error: No watchers/stars/forks") 

    try:    
        #1 mainbranch_commits数 branches数 releases数 license
        c_mbcommits=Tools.Filter.FilterNumber(Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[2]/div/div/ul/li[1]/a/span"""),returncount=1)
        c_branches=Tools.Filter.FilterNumber(Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[2]/div/div/ul/li[2]/a/span"""),returncount=1)
        c_releases=Tools.Filter.FilterNumber(Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[2]/div/div/ul/li[3]/a/span"""),returncount=1)
    except:
	print("No c_mbcommits/c_branches/c_releases")
        c_mbcommits=None
	c_branches=None
	c_releases=None

    '''
    for i in range(5):
        c_contributors=Tools.Filter.FilterNumber(Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[2]/div/div/ul/li[4]/a/span"""),returncount=1)
        if c_contributors!='':
            break
    print "c_contributors: %s"%(c_contributors)
    if c_contributors=='':
        print('can not load contributor count: %s'%(url))
        c_contributors=None
    '''
    try:
        driver.find_element_by_xpath("""//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[2]/div/div/ul/li[5]/a""")
        v_license=Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[2]/div/div/ul/li[5]/a""")
    except:
        print "element exists not: license"
        v_license=None
    
    try:
        driver.find_element_by_xpath("""//*[@id="readme"]/article""")
        v_readme=Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="readme"]/article""")
        v_readme=v_readme.replace("'","\\'").replace('"','\\"')
        v_readme=Tools.Filter.FilterEmoji(v_readme)
    except:
        print "element exists not: readme"
        v_readme=None
    
    
    valuelist0=[c_watchers,c_stars,c_forks,c_mbcommits,c_branches,c_releases,v_license,v_readme]
    return valuelist0
    '''
    #2 编程语言信息 langcount,mainlang,mlangper,seclang,slangper,thilang,tlangper
    result=self.soup.find_all('ol',{'class':"repository-lang-stats-numbers"})
    if result==[]:
        valuelist2=['null']*7
    else:
        valuelist2=[]
        result=result[0].find_all('a')
        langcount=len(result)
        valuelist2.append(langcount)
        inputlangcount=min([langcount,3])
        for i in range(inputlangcount):
            r=result[i].find_all('span')
            valuelist2.append(r[1].text)
            valuelist2.append(r[2].text)
        for i in range(3-inputlangcount):
            valuelist2.append('null')
            valuelist2.append('null')
        for i in range(7):
            if type(valuelist2[i])==unicode:
                valuelist2[i]=valuelist2[i].replace(u"'",u"\\'")
    '''
        
        
def GrabWeb2(driver,url):
    #需跳转至Web2,挖取 open_issues close_issues
    try:
        driver.get("https://www.github.com/"+url+"/issues")
    except:
        sys.exit("can not load the page: %s/issues."%(url))

    if driver.current_url.split('/')[-1]!='issues':
        print('issues page exists not')
        return [0,0]
    
    try:
        driver.find_element_by_xpath("""//*[@id="js-issues-toolbar"]/div/div[1]/a[1]""")
        c_openissues=Tools.Filter.FilterNumber(Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-issues-toolbar"]/div/div[1]/a[1]"""),returncount=1)
        c_closeissues=Tools.Filter.FilterNumber(Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-issues-toolbar"]/div/div[1]/a[2]"""),returncount=1)
    except:
        print("element exists not: issues")
        c_openissues=0
        c_closeissues=0
    
    valuelist=[c_openissues,c_closeissues]
    return valuelist


def GrabWeb3(driver,url):
    #需跳转至Web3,挖取 open_pull close_pull
    try:
        driver.get("https://www.github.com/"+url+"/pulls")
    except:
        sys.exit("can not load the page: %s/pulls."%(url))
    
    if driver.current_url.split('/')[-1]!='pulls':
        print('pulls page exists not')
        return [0,0]
    
    try:
        driver.find_element_by_xpath("""//*[@id="js-issues-toolbar"]/div/div[1]/a[1]""")
        c_openpulls=Tools.Filter.FilterNumber(Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-issues-toolbar"]/div/div[1]/a[1]"""),returncount=1)
        c_closepulls=Tools.Filter.FilterNumber(Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="js-issues-toolbar"]/div/div[1]/a[2]"""),returncount=1)
    except:
        print("element exists not: pulls")
        c_openpulls=0
        c_closepulls=0
    
    valuelist=[c_openpulls,c_closepulls]
    return valuelist

'''
def GrabWeb4(self,proj_url,proj_index):
    #需跳转至Web4,挖取proj查询结果的 repositories,code,commits,issues,wikis,users
    proj_name=proj_url.split('/')[2]
    url="""/search?p=1&q="""+unicode(proj_name)+"""&type=Repositories&utf8=%E2%9C%93"""
    state,proj_index=self.JumpToPage(url,proj_index,4)
    if state==False:
        return False,proj_index
    
    waitcount=0
    while True:
        time.sleep(3)
        result=self.soup.find_all('nav',{'class':"menu"})
        if result==[]:
            print '\t',"warning: can't search project by name, current project index="+str(proj_index),"error part:2"
            valuelist=['null','null','null','null','null','null']
        else:
            result=result[0].find_all('a')
            valuelist=[] #插入值
            nullcount=0
            for i in result:
                value=i.find_all('span')
                if value==[]:
                    nullcount+=1
                    valuelist.append('null')
                else:
                    valuelist.append(Tools.Filter.ValueExtract(value[0].text))
            if nullcount<=2:
                break
            else:
                waitcount+=1
                if waitcount>5:
                    break
                else:
                    print '\t','too much nulls','waitcount:',waitcount,'nullcount:',nullcount
    return valuelist
'''