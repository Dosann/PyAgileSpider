# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 16:34:22 2017
@author: duxin
Email: duxin_be@outlook.com

"""

def db_construction(cur,tables):
    
    #若表单不存在，则添加
    
    if "_" not in tables:
        CreateUserdetails(cur)

#添加表单

def CreateUserdetails(cur):
    cmd="""select 1"""
    cur.execute(cmd)

