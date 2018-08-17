#coding:utf-8

from Redis.RedisOperHelper import RedisOperHelper

_redisOper = RedisOperHelper()
print(_redisOper.queuePut('JobStatus','queue1'))
