# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 16:34:22 2017
@author: duxin
Email: duxin_be@outlook.com

"""
from sys import path
path.append('/spiders_repodetails')
import GLOBAL


def db_construction(cur,tables):
    date=GLOBAL.date
    print("Database initializing...")
    
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
    #task_user记录 spider_activeusers_watch_subscription_repo_following.py 的完成情况
    if "tasks_user" not in tables:
        CreateTasksUser(cur)
    
    if "repodetails_%s"%(date) not in tables:
        CreateRepodetails_date(cur)
        InitializeRepodetails_date(cur)

    print("Database initialization finished")
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
            id int auto_increment primary key,
            name varchar(50),
            follower_user varchar(50))"""
    cur.execute(cmd)
    
def CreateUserRelasFollowing(cur):
    cmd="""create table user_relas_following(
            id int auto_increment primary key,
            name varchar(50),
            following_user varchar(50))"""
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

def CreateTasksUser(cur):
    cmd="""create table tasks_user(
            id int primary key,
            name varchar(50),
            status varchar(20))"""
    cur.execute(cmd)

def CreateRepodetails_date(cur):
    date=GLOBAL.date
    cmd="""create table repodetails_%s(
            id int primary key,
            user varchar(40),
            repo varchar(200),
            repoid int,
            watchers int,
            stars int,
            forks int,
            contributors int,
            size int,
            branches int,
            releases int,
            open_issues int,
            close_issues int,
            open_pull int,
            close_pull int,
            mainbranch_commits int,
            license varchar(20),
            has_downloads tinyint,
            has_issues tinyint,
            has_wiki tinyint,
            private tinyint,
            createtime varchar(20),
            pushtime varchar(20),
            updatetime varchar(20),
            recordtime varchar(20),
            ownerid int,
            ownertype varchar(13),
            codesize int,
            langcount int,
            language varchar(30),
            mlangsize int,
            mlangper varchar(10),
            seclang varchar(30),
            slangsize int,
            slangper varchar(10),
            thilang varchar(30),
            tlangsize int,
            tlangper varchar(10),
            _api_finished tinyint default 0,
            _web_finished tinyint default 0)"""%(date)
    cur.execute(cmd)

def InitializeRepodetails_date(cur):
    date=GLOBAL.date
    cmd="insert into repodetails_%s(id,user,repo) select id,user,repo from good_repos"%(date)
    cur.execute(cmd)
            