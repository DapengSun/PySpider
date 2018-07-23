#coding:utf-8
import requests
from bs4 import BeautifulSoup

class ErShouFangSpider():
    def getHouseInfo(self):
        _baseUrl = 'https://bj.lianjia.com/ershoufang'

        _header = { 'Host':'bj.lianjia.com',
                    'Connection':'keep-alive',
                    'Cache-Control':'max-age=0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9'
                }

        for i in range(1,2):
            _erShoufangUrl = '%s/pg%s/' % (_baseUrl,i)
            # print(_pgNum)
            self.getPageHtml(_erShoufangUrl,_header)


    def getPageHtml(self,url,header):
        _htmlDoc = requests.get(url,header)
        _soup = BeautifulSoup(_htmlDoc.text,'html.parser', from_encoding='utf-8')
        _soup.find('ul',class_="sellListContent").find_all('li',class_="clear LOGCLICKDATA")


t = ErShouFangSpider()
t.getHouseInfo()
