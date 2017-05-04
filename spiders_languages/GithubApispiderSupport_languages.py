# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:54:30 2017

@author: duxin
"""

import sys
sys.path.append("../")
from core import Tools
import time
import json

def GrabLanguages(crawlerbody,reponame):
    g=crawlerbody.g
    threadname=crawlerbody.threadname
    conn=crawlerbody.conn
    
    #检测当前g的状态，若rate_limiting[1]低于100，更换账号
    while 1:
        while 1:
            try:
                ratelimit=g.rate_limiting[1]
            except:
                print "rate_limiting failed"
                continue
            break
        if ratelimit<=100:
            print(threadname,"current account get flagged:",crawlerbody.gaccount[0])
            Tools.GithubAccountManagement.ReleaseAnAccount(conn,crawlerbody.gaccount)
            account=Tools.GithubAccountManagement.OccupyAnAccount(conn)
            if account!=None:
                crawlerbody.g=Tools.GithubAccountManagement.CreateG(account[1],account[2])
                crawlerbody.gaccount=account
                g=crawlerbody.g
                print threadname,"has changed account:",crawlerbody.gaccount[0]
            else:
                print "no available account in accountque.",time.ctime()
                print threadname,"exits"
                exit(999)
        else:
            break
    
    repo=g.get_repo(reponame)
    js=json.dumps(repo.get_languages())
    js=js.replace("'","\\'").replace('"','\\"')
    return js
    
    
    