# coding:utf-8
from RedisOper.RedisOperHelper import RedisOperHelper

class LianJiaSpiderQueue(object):
    def __init__(self,spiderurl):
        self.queuename = 'JobQueue:lianjia'
        # 待爬的网页链接
        self.spiderurl = spiderurl

    def pushjobqueue(self):
        _redisOper = RedisOperHelper()
        _redisOper.queuePut(self.queuename,self.spiderurl)

# _spiderJob = LianJiaSpiderQueue('https://bj.lianjia.com/ershoufang/rs方庄/')
# _spiderJob.pushjobqueue()