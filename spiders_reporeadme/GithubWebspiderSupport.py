# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:35:03 2017

@author: duxin
"""


from sys import path
path.append("../")
from core import Tools
import sys
import re


def GrabWeb1(driver,url):
    #需跳转至Web1,挖取proj的 watch,star,fork,mainbranch_commits数 branches数 releases数 license名 编程语言信息
    try:
        driver.get("https://www.github.com/"+url)
    except Exception,e:
        print(e)
        sys.exit("can not load the page: %s."%(url))

    try:
        Tools.SeleniumSupport.WaitUntilPresence(driver,"""//*[@id="readme"]""")
        v_readme=Tools.SeleniumSupport.GetTextByXpath(driver,"""//*[@id="readme"]""")
        #v_readme=v_readme.replace("'","\\'").replace('"','\\"')
        pattern=re.compile(r"""['";]""")
        v_readme=pattern.sub(' ',v_readme)
        v_readme=Tools.Filter.FilterEmoji(v_readme)
        if type(v_readme)==str or type(v_readme)==unicode:
            v_readme=v_readme[:65500]
    except Exception,e:
        #traceback.print_exc()
        print(e)
        user,repo=url.split('/')
        driver.save_screenshot('../files/screenshots/%s.png'%(user+'_'+repo))
        # "Whoa there" 错误
        if 'Whoa there' in driver.page_source:
            sys.exit('ERROR: WHOA THERE')

        # 是否能找到README
        try:
            table=driver.find_element_by_xpath("""//*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[6]/table/tbody""")
            if "README" in table.text:
                sys.exit('ERROR: README FOUND')
        except:
            #这个repo啥都没有
            pass

        print("README NOT FOUND")
        #不属于上述错误，则说明readme不存在
        v_readme='*Nothing*'

    return v_readme