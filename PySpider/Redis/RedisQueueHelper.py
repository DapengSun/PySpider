#coding:utf-8

import redis
import time

class RedisQueueHelper(object):
    def __init__(self,queuename,namespace="JobQueue"):
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self.db = redis.Redis(connection_pool=pool)
        # self.db = redis.Redis(**redis_param)
        self.key = '%s:%s' %(namespace, queuename)

    def qsize(self):
        return self.db.llen(self.key)# 返回队列里面list内元素的数量

    def put(self,item):
        self.db.rpush(self.key,item)

    def get_nowait(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        return self.db.lpop(self.key)

    def get_wait(self, timeout=None):
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.db.blpop(self.key, timeout=timeout)
        return item

