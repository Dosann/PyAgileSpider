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
    if "user_relas_followed" not in tables:
        CreateUserRelasFollowed(cur)
    if "user_relas_following" not in tables:
        CreateUserRelasFollowing(cur)
    if "user_subscribes_repo" not in tables:
        CreateUserSubscribesRepo(cur)
    if "user_stars_repo" not in tables:
        CreateUserStarsRepo(cur)
    if "user_has_repo" not in tables:
        CreateUserHasRepo(cur)
    #task_user_repo_relas记录 spider_activeusers_watch_subscription_repo.py 的完成情况
    if "tasks_user_repo_relas" not in tables:
        CreateTasksUserRepoRelas(cur)

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

def CreateUserRelasFollowed(cur):
    cmd="""create table user_relas_followed(
            rela_id int auto_increment primary key,
            name varchar(50),
            followername varchar(50))"""
    cur.execute(cmd)
    
def CreateUserRelasFollowing(cur):
    cmd="""create table user_relas_following(
            rela_id int auto_increment primary key,
            name varchar(50),
            followingname varchar(50))"""
    cur.execute(cmd)

def CreateUserSubscribesRepo(cur):
    cmd="""create table user_subscribes_repo(
            id int auto_increment primary key,
            name varchar(50),
            subbed_repo varchar(200))"""
    cur.execute(cmd)

def CreateUserStarsRepo(cur):
    cmd="""create table user_stars_repo(
            id int auto_increment primary key,
            name varchar(50),
            starred_repo varchar(200))"""
    cur.execute(cmd)

def CreateUserHasRepo(cur):
    cmd="""create table user_has_repo(
            id int auto_increment primary key,
            name varchar(50),
            owned_repo varchar(200))"""
    cur.execute(cmd)

def CreateTasksUserRepoRelas(cur):
    cmd="""create table tasks_user_repo_relas(
            id int primary key,
            name varchar(50),
            status varchar(20))"""
    cur.execute(cmd)