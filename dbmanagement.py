# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 16:34:22 2017
@author: duxin
Email: duxin_be@outlook.com

"""

def db_construction(cur,tables):
    
    #若表单不存在，则添加
    
    if "t_urls" not in tables:
        CreateT_urls(cur)

#添加表单

def CreateT_urls(cur):
    cmd="""create table t_urls(id int auto_increment primary key,url text,status varchar(20))"""
    cur.execute(cmd)

