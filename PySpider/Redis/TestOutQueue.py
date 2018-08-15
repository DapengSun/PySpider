#coding:utf-8

from Redis.RedisOperHelper import RedisOperHelper

t = ['a','c']
_redisOper = RedisOperHelper()
print(_redisOper.hashHsetnx('JobStatus'))
