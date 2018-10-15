# coding:utf-8
import sys

from CelerySpiderConf import app
# sys.path.append("..")
# sys.path.insert(0, '..')
from RedisOper.RedisOperHelper import RedisOperHelper
# from ..RedisOper import RedisOperHelper
from LianJiaSpider.ErShouFangSearchSpider import ErShoufangSearchInfo


# 异步调用获取爬虫链接 将爬虫信息存入缓存
@app.task
def getspiderjob():
    queuename = 'JobQueue:lianjia'
    _redisHelper = RedisOperHelper()
    _spiderJobUrl = _redisHelper.queueGetNoWait(queuename)
    if _spiderJobUrl != None:
        _searchInfo = ErShoufangSearchInfo(_spiderJobUrl)
        _searchInfo.getHouseInfo()

class LianJiaSpiderJob(object):
    def __init__(self):
        queuename = 'JobQueue:lianjia'

    # @app.task
    # def getspiderjob(self):
    #      _redisHelper = RedisOperHelper()
    #      _spiderJobUrl = _redisHelper.queueGetNoWait(self.queuename)
    #      if _spiderJobUrl != None:
    #          _searchInfo = ErShoufangSearchInfo(_spiderJobUrl)
    #          _searchInfo.getHouseInfo()

# _spiderJob = LianJiaSpiderJob()
# _spiderJob.getspiderjob()

if __name__ == '__main__':
    getspiderjob()