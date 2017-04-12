# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 16:34:22 2017
@author: duxin
Email: duxin_be@outlook.com

"""

def db_construction(cur,tables):
    
    #若表单不存在，则添加
    
    if "userdetails" not in tables:
        CreateUserdetails(cur)

#添加表单

def CreateUserdetails(cur):
    cmd="""create table userdetails(
            id int primary key,
            userid int,
            name varchar(50),
            company varchar(30),
            created_at varchar(19),
            updated_at varchar(19),
            followercount int,
            followingcount int,
            hireable tinyint,
            location varchar(50),
            public_gists int,
            public_repos int,
            site_admin tinyint,
            type varchar(12))
            """
    cur.execute(cmd)

