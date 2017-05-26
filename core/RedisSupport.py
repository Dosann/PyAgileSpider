# -*- coding: utf-8 -*-
"""
Created on Wed May 17 09:15:17 2017

@author: duxin
"""

import redis

class RedisSupport:
    
    @staticmethod
    def GenerateRedisConnection(host,port=6379,dbname=0):
        red=redis.Redis(host=host,port=port,db=dbname)
        return red