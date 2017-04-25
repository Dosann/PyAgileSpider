# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:54:30 2017

@author: duxin
"""

import sys
sys.path.append("../")
from core import Tools
import time

def GrabApidetails(crawlerbody,reponame):
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
    rd=repo.raw_data
    c_repoid=rd['id']
    c_size=rd['size']
    c_hasdownloads=rd['has_downloads']==True and 1 or 0
    c_hasissues=rd['has_issues']==True and 1 or 0
    c_haswiki=rd['has_wiki']==True and 1 or 0
    c_private=rd['private']==True and 1 or 0
    v_createtime=rd['created_at']
    v_pushtime=rd['pushed_at']
    v_updatetime=rd['updated_at']
    v_recordtime=unicode(time.strftime('%Y-%m-%d %H:%M:%S'))
    c_ownerid=rd['owner']['id']
    v_ownertype=rd['owner']['type']
    
    
    try:
        gcons=repo.get_contributors()
        ccount=0
        for gc in gcons:
            ccount+=1
        c_contributors=ccount
    except Exception,e:
        if 403 in e and hasattr(e,'data') and 'too large' in e.data['message']:
            c_contributors=99999999
        else:
            sys.exit("888: unexpected error when requesting contributors")
    print('c_contributors: %s'%(c_contributors))
    
    language_infos=sorted(repo.get_languages().items(),key=lambda x:x[1],reverse=1)
    codesize=0
    for lang in language_infos:
        codesize+=lang[1]
    c_codesize=codesize
    c_langcount=len(language_infos)
    
    v_langdetails=[]
    for i in range(min([3,c_langcount])):
        v_langdetails+=[language_infos[i][0],language_infos[i][1],unicode(language_infos[i][1]/c_codesize)[:10]]
    for i in range(c_langcount,3):
        v_langdetails+=[None,None,None]
    
    valuelist=[c_repoid,c_size,c_hasdownloads,c_hasissues,c_haswiki,c_private,
               v_createtime,v_pushtime,v_updatetime,v_recordtime,c_ownerid,v_ownertype,c_contributors,
               c_codesize,c_langcount]+v_langdetails
    return valuelist
    