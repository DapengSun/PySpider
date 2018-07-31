#coding:utf-8

import redis
import time

class TestOutQueue(object):
    def __init__(self,queuename,namespace="queue"):
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self.db = redis.Redis(connection_pool=pool)
        self.key = '%s:%s' % (namespace, queuename)

    def OutQueue(self):
        return self.db.lpop(self.key)

_redis = TestOutQueue("test3")

while True:
    time.sleep(2)
    _out = _redis.OutQueue()
    print('出队列%s' % _out)
    if _out == None:
        break;

