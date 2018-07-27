#coding:utf-8
import pymysql
import requests
import time
from bs4 import BeautifulSoup

class UpdateErShouFangSpider():
    def __init__(self):
        self.db = pymysql.connect(host="localhost",user="root",password="sdmp",db="spider",port=3306)
        self.cursor = self.db.cursor()

    def getHouseInfo(self):
        _header = {'Host': 'bj.lianjia.com',
                   'Connection': 'keep-alive',
                   'Cache-Control': 'max-age=0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9'
                   }

        _querySql = 'SELECT * FROM `ershoufanginfo` WHERE HouseArea IS NULL AND SysStatus = 0'
        self.cursor.execute(_querySql)
        _erShouFangData = self.cursor.fetchall()
        description = [i[0] for i in self.cursor.description]
        _data = [dict(zip(description,i)) for i in _erShouFangData]
        # 获取房屋编码、页面URL列表
        _houseCodeList = [(i['HouseInfoUrl'],i['HouseInfoCode']) for i in _data]
        for i in _houseCodeList:
            self.getPageHtml(i[0],i[1],_header)
            time.sleep(1)

    def getPageHtml(self,HouseInfoUrl,HouseCode,Header):
        _htmlDoc = requests.get(HouseInfoUrl,Header)
        _soup = BeautifulSoup(_htmlDoc.text,'html.parser',from_encoding='utf-8')

        # 获取房屋地区
        if _soup.find('div',class_='aroundInfo')!=None:
            _houseArea = _soup.find('div',class_='aroundInfo').find('div',class_='areaName').find('span',class_='info').find('a').text
            self.updateHouseArea(HouseCode,_houseArea)

    def updateHouseArea(self,HouseCode,HouseArea):
        _updateSql = "update `ershoufanginfo` set HouseArea = '%s' Where HouseInfoCode = '%s'" % (HouseArea,HouseCode)
        self.cursor.execute(_updateSql)
        self.db.commit()

t=UpdateErShouFangSpider()
t.getHouseInfo()