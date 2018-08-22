# coding:utf-8
import sys
# sys.path.append("..")
# sys.path.insert(0, '..')
from RedisOper.RedisOperHelper import RedisOperHelper
# from ..RedisOper import RedisOperHelper
from LianJiaSpider.ErShouFangSearchSpider import ErShoufangSearchInfo

class LianJiaSpiderJob(object):
    def __init__(self):
        self.queuename = 'JobQueue:lianjia'

    def getspiderjob(self):
         _redisHelper = RedisOperHelper()
         _spiderJobUrl = _redisHelper.queueGetNoWait(self.queuename)
         if _spiderJobUrl != None:
             _searchInfo = ErShoufangSearchInfo(_spiderJobUrl)
             _searchInfo.getHouseInfo()

# _spiderJob = LianJiaSpiderJob()
# _spiderJob.getspiderjob()