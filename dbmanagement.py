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
    
    if "t_iframes" not in tables:
        CreateT_iframes(cur)

#添加表单

def CreateT_urls(cur):
    cmd="""create table t_urls(id int auto_increment primary key,url text,status varchar(20))"""
    cur.execute(cmd)

def CreateT_iframes(cur):
    cmd="""create table t_iframes(iframe_name varchar(50))"""
    cur.execute(cmd)