#coding:utf-8

from Redis.RedisOperHelper import RedisOperHelper

_redisOper = RedisOperHelper()
# print(_redisOper.queuePut('JobStatus','queue1'))

print([_redisOper.keys('s_result_20180817163711*')])

print(_redisOper.hashHgetAll('s_result_20180817163711_101102655980'))


class DictObj(object):
    def __init__(self,map):
        self.map = map

    def __setattr__(self, name, value):
        if name == 'map':
             object.__setattr__(self, name, value)
             return;
        print('set attr called ',name,value)
        self.map[name] = value

    def __getattr__(self,name):
        v = self.map[name]
        if isinstance(v,(dict)):
            return DictObj(v)
        if isinstance(v, (list)):
            r = []
            for i in v:
                r.append(DictObj(i))
            return r
        else:
            return self.map[name];

    def __getitem__(self,name):
        return self.map[name]

_dict = DictObj(_redisOper.hashHgetAll('s_result_20180817163711_101102655980'))
