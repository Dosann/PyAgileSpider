# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 14:01:25 2017

@author: duxin
"""


from sys import path
path.append("../")
from core import Tools
'''
GithubAccountManagement.ImportRawEmailAccounts(u'163邮箱3.txt')
GithubAccountManagement.ImportRawEmailAccounts(u'github_accounts.txt',split_char='\t')
GithubAccountManagement.ImportRawEmailAccounts(u'github_accounts2.txt')
GithubAccountManagement.ImportRawEmailAccounts(u'github_accounts3.txt')
'''
conn=Tools.DatabaseSupport.GenerateConn(dbname="grabgithub",host='10.2.1.26')
Tools.GithubAccountManagement.ImportRawEmailAccounts(conn,u'github_accounts4.txt')
conn.close()