#coding:utf-8

from enum import Enum

class SpiderJobStatus(Enum):
    异常  = -1
    待启动 = 0
    启动中 = 1
    已完成 = 2
    结果入库 = 3
