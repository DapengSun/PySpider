# -*- coding: utf-8 -*-

from concurrent import futures

class SpiderUrlHandler(object):
    '''
    多线程爬虫类
    '''
    def __init__(self,url):
        self.url = url
        self.spiderThreadPool = futures.ThreadPoolExecutor(max_workers=5)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def spiderUrl(self):
        pass

