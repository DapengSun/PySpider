# coding:utf-8
import sys
from Redis.RedisQueueHelper import RedisQueueHelper
from LianJiaSpider.ErShouFangSearchSpider import ErShoufangSearchInfo

class LianJiaSpiderJob(object):
    def __init__(self):
        self.queuename = 'lianjia'

    def getspiderjob(self):
         _redisHelper = RedisQueueHelper(self.queuename)
         _spiderJobUrl = _redisHelper.get_nowait()
         _searchInfo = ErShoufangSearchInfo(_spiderJobUrl)
         _searchInfo.getHouseInfo()

_spiderJob = LianJiaSpiderJob()
_spiderJob.getspiderjob()