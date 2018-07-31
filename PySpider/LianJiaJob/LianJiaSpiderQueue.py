# coding:utf-8
from Redis.RedisQueueHelper import RedisQueueHelper

class LianJiaSpiderQueue(object):
    def __init__(self,spiderurl):
        self.queuename = 'lianjia'
        # 待爬的网页链接
        self.spiderurl = spiderurl

    def pushjobqueue(self):
        _redisQueue = RedisQueueHelper(self.queuename)
        _redisQueue.put(self.spiderurl)

_spiderJob = LianJiaSpiderQueue('https://bj.lianjia.com/ershoufang/rs香河/')
_spiderJob.pushjobqueue()