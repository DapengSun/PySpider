# -*- coding: utf-8 -*-
import urllib2
from multiprocessing.dummy import Pool as ThreadPool
import time
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

class House:
    def printParallel(self,Num):
        print '%s开始获取数据' % str(Num)
        start = time.time()
        time.sleep(Num)
        end = time.time()
        print '%s获取数据结束' % str(Num)

    def test(self):
        urls = []

        for i in range(0, 10):
            urls.append(i)

        # Make the Pool of workers
        pool = ThreadPool(4)
        # Open the urls in their own threads
        # and return the results
        try:
            results = pool.map(self.printParallel, urls)
            # close the pool and wait for the work to finish
            pool.close()
            pool.join()
        except Exception, ex:
            print ex

if __name__ == "__main__":
    house=House()
    house.test()