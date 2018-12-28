# -*- coding: utf-8 -*-
import sys
import time
import random
import urllib.request
from enum import Enum
sys.path.append('..')
from DoubanBookSpider.SpiderConf import doubanBookBaseUrl,categoryStatus
from RedisOper.RedisOperHelper import RedisOperHelper as redisOp
from concurrent import futures
from bs4 import BeautifulSoup
import lxml
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

class spiderStatus(Enum):
    爬取失败 = -1
    未爬取 = 0
    已爬取 = 1

class PreSpiderUrlHandler(object):
    '''
    预处理爬虫URL类
    '''
    def __init__(self):
        # 获取豆瓣阅读 爬虫基础URL路径
        self.baseUrl = doubanBookBaseUrl
        self.header = {
            'Host':'book.douban.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive'
        }

    def __enter__(self):
        '''
        使用with对资源进行访问，确保不管是否异常都会执行清理操作，释放资源
        :return:
        '''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        使用with对资源进行访问，确保不管是否异常都会执行清理操作，释放资源
        :return:
        '''
        pass

    def getKinds(self):
        '''
        获取可用的Kind类型
        :param kind:douban阅读类型 目前可用kind—id区间【1、18、19、100-235】
        :return:
        '''
        kinds = [1]
        # for i in range(100,235):
        #     kinds.append(i)
        return kinds

    def createKindUrl(self,kind):
        '''
        根据类型kind-id 生成URL
        :param kind:类型kind-id
        :return:
        '''
        yield f'{self.baseUrl}/?kind={kind}'

    def getIndexPage(self,indexUrl):
        '''
        获取首页URL数据 & 该类型数据总量
        :param indexUrl:首页地址URL
        :return:
        '''
        # 休眠随机数 避免反爬虫封ip
        # time.sleep(random.randint(1, 10))
        requestObj = urllib.request.Request(url=indexUrl,headers=self.header)
        responseObj = urllib.request.urlopen(requestObj)
        htmContent = responseObj.read().decode('utf-8')
        return htmContent

    def getIndexPageCallBack(self,result):
        '''
        获取首页URL数据 回调函数返回结果
        :param result:回调返回结果
        :return:
        '''
        responseObj = result.result()
        htmContent = responseObj.read().decode('utf-8')
        print(f'{htmContent}:end')

    def getCategoryInfo(self,htmContent):
        '''
        beautifulsoup解析内容
        :param htmContent: 页面内容
        :return:
        '''
        soup = BeautifulSoup(htmContent,'lxml')

        # 获取一级目录
        categorys = soup.find_all('a', class_='tag-title-wrapper')
        # 获取二级目录
        tags = soup.find_all('table', class_='tagCol')

        resList = []
        # 遍历一级目录与二级目录进行对应
        for index,category in enumerate(categorys):
            categoryName = category['name']
            tag = tags[index]
            tagSoup = BeautifulSoup(str(tag),'lxml')
            tagItems = tagSoup.find_all('td')

            # 截取域名https://book.douban.com
            domainUrl = f"{self.baseUrl.split('/')[0]}//{self.baseUrl.split('/')[2]}"

            res = map(lambda x:{
                'categoryName' : categoryName,
                'tagName' : x.contents[0].string,
                'tagHref' : x.contents[0]['href'],
                'tagNum': x.contents[1].string,
                'tagAllHref' : f"{domainUrl}{x.contents[0]['href']}",
                # 0-未爬取 1-已爬取
                'isFinishSpider' : spiderStatus.未爬取.value
            },tagItems)

            yield from list(res)

if __name__ == '__main__':
    # redis配置参数
    redisArgs = {
        'host':'localhost', 'port':6379 ,'decode_responses':True,'db':7
    }
    oper = redisOp(redisArgs)

    status = oper.getStr(f'{categoryStatus}')
    if status == None or status == spiderStatus.未爬取.value:
        with PreSpiderUrlHandler() as handler:
            # 目前可用类型kind-id区间【1、18、19、100-235】
            # spiderKindList = handler.getKinds()

            # spiderKindUrlList = []
            # for kindId in spiderKindList:
            #     # 根据类型kind-id 通过生成器生成URL
            #     for url in handler.createKindUrl(kindId):
            #         # 爬取页面 获取类型页面总量
            #         spiderKindUrlList.append(url)

            # print(spiderKindUrlList)
            # 开启多线程
            # threadPool = futures.ThreadPoolExecutor(max_workers=5)
            # 开启多线程 异步获取首页信息
            # tasks = [threadPool.submit(handler.getIndexPage,url).add_done_callback(handler.getIndexPageCallBack) for url in spiderKindUrlList]
            # for task in tasks:
            #     task.add_done_callback(handler.getIndexPageCallBack)

            # 爬取目录页面获取所有分类
            htm = handler.getIndexPage(doubanBookBaseUrl)
            # 解析页面内容 获取分类和目录信息 生成器返回
            for i in handler.getCategoryInfo(htm):
                oper.hashHmset(f"category_{i['categoryName']}_{i['tagName']}",i)
            oper.setStr(f'{categoryStatus}',spiderStatus.已爬取.value)
