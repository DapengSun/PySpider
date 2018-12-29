# -*- coding: utf-8 -*-
import sys
import time
import random
import string
import urllib.request
from concurrent import futures
from enum import Enum
sys.path.append('..')
from DoubanBookSpider.SpiderConf import doubanBookBaseUrl,categoryStatus
from DoubanBookSpider import MultithreadSpider
from RedisOper.RedisOperHelper import RedisOperHelper as redisOp
from bs4 import BeautifulSoup
import lxml
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from urllib.request import quote

# redis配置参数
redisArgs = {
    'host':'localhost', 'port':6379 ,'decode_responses':True,'db':7
}
oper = redisOp(redisArgs)

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
        :param indexUrl:首页地址Url
        :return:
        '''
        # 休眠随机数 避免反爬虫封ip
        # time.sleep(random.randint(1, 10))
        htmContent = self.spiderUrlHtm(indexUrl)
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
                'isFinishSpider' : spiderStatus.未爬取.value,
                # tag下图书爬取页数
                'bookPageNum':0
            },tagItems)

            yield from list(res)

    def getBooksPageNum(self,category,tagUrl):
        '''
        通过tag获取图书总页数
        :param category:分类
        :param tagUrl:Tag基Url
        :return:
        '''
        print(f'爬取{category} start...')
        htmContent = self.spiderUrlHtm(tagUrl)
        soupBook = BeautifulSoup(htmContent,'lxml')
        bookPageNum = soupBook.find_all('div',class_='paginator')[0].find_all('a')[-2].string

        # 更新redis分类hash中 图书爬取数量bookPageNum
        oper.hashHset(category,'bookPageNum',bookPageNum)
        oper.hashHset(category, 'isFinishSpider', spiderStatus.已爬取.value)
        print(f'爬取{category} end... res:{bookPageNum}')
        return {'num':bookPageNum,'category':category,'tagUrl':tagUrl}

    def getBooksPageNumCallBack(self,result):
        '''
        通过tag获取图书总页数回调方法
        :param result:页数结果
        :return:
        '''
        res = result.result()
        bookPageNum = int(res['num'])
        # 超过50页当做50页处理
        bookPageNum = 50 if bookPageNum > 50 else int(bookPageNum)
        category = res['category']
        tagUrl = res['tagUrl']

        for num in range(0,bookPageNum):
            # 根据编号生成页面地址
            bookUrl = f"{tagUrl}?start={num * 20}&type=T"
            oper.queuePut(f'crawler_{category}',bookUrl)
        return

    def getBooksUrlByTag(self,tagUrl):
        '''
        通过分类获取图书爬虫Url
        :param tagUrl:Tag基Url
        :return:
        '''
        pass

    def spiderUrlHtm(self,spiderUrl):
        '''
        根据指定Url 获取单页面Html
        :param spiderUrl:页面Url
        :return:
        '''
        # Url包含中文需要转码
        spiderUrl = quote(spiderUrl,safe = string.printable)
        requestObj = urllib.request.Request(spiderUrl, headers=self.header)
        responseObj = urllib.request.urlopen(requestObj)
        htmContent = responseObj.read().decode('utf-8')
        return htmContent

    def relaxSpider(self):
        time.sleep(random.randint(1,5))

if __name__ == '__main__':
    # 爬取豆瓣图书目录及分类
    status = oper.getStr(f'{categoryStatus}')
    status = int(0 if status == None else status)
    with PreSpiderUrlHandler() as handler:
        if status == None or status == spiderStatus.未爬取.value:
            # 爬取目录页面获取所有分类
            htm = handler.getIndexPage(doubanBookBaseUrl)
            # 解析页面内容 获取分类信息 生成器返回
            for i in handler.getCategoryInfo(htm):
                oper.hashHmset(f"category_{i['categoryName']}_{i['tagName']}",i)
            # 标识目录已经获取 不需重新爬取
            oper.setStr(f'{categoryStatus}',spiderStatus.已爬取.value)

        status = int(oper.getStr(f'{categoryStatus}'))
        if status == spiderStatus.已爬取.value:
            # 根据分类Hash地址 爬取相应内容
            categorys = oper.keys('category_*')

            # 多线程获取各个Tag页面总量
            with futures.ThreadPoolExecutor(max_workers=5) as threadPool:
                for category in categorys:
                    categoryItem = oper.hashHgetAll(f'{category}')
                    isFinishSpider = int(categoryItem['isFinishSpider'])
                    bookPageNum = int(categoryItem['bookPageNum'])
                    # 获取该分类是否已爬取
                    if isFinishSpider == spiderStatus.未爬取.value and bookPageNum == 0:
                        tagUrl = categoryItem['tagAllHref']
                        # 获取能够爬取的页面数量
                        threadPool.submit(handler.getBooksPageNum,category,tagUrl).add_done_callback(handler.getBooksPageNumCallBack)
                        # 阻塞主线程 休眠几秒 避免爬取过快
                        # handler.relaxSpider()








