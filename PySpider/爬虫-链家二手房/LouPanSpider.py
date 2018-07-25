#coding:utf-8
import re
import requests
import pymysql
import datetime
import time
from  decimal import Decimal
from bs4 import BeautifulSoup

class LouPanModel():
    def __init__(self,HouseInfoUrl,SurfacePlotThumbnail,
                 HouseTitle,HouseTag,HouseArea,HouseAreaDetail,HouseAddressUrl,HouseAddressName,
                 HouseSize,HouseInfoTag,HouseTotalPrice,HouseUnitPrice):
        self.HouseInfoUrl = HouseInfoUrl
        self.SurfacePlotThumbnail = SurfacePlotThumbnail
        self.HouseTitle = HouseTitle
        self.HouseTag = HouseTag
        self.HouseArea = HouseArea
        self.HouseAreaDetail = HouseAreaDetail
        self.HouseAddressUrl = HouseAddressUrl
        self.HouseAddressName = HouseAddressName
        self.HouseSize = HouseSize
        self.HouseInfoTag = str(HouseInfoTag)
        self.HouseTotalPrice = str(HouseTotalPrice)
        self.HouseUnitPrice = str(HouseUnitPrice)
        self.SysStatus = 0
        self.CDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

class LouPanSpider():
    def __init__(self):
        try:
            self.db = pymysql.connect(host="localhost",user="root",password="sdmp",db="spider",port=3306)
            self.cursor = self.db.cursor()
        except Exception as e:
            print(e)

    def getHouseInfo(self):
        _baseUrl = 'https://bj.lianjia.com/loupan'

        _header = { 'Host':'bj.lianjia.com',
                    'Connection':'keep-alive',
                    'Cache-Control':'max-age=0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9'
                }

        for i in range(1,53):
            _loupanUrl = '%s/pg%s/' % (_baseUrl,i)
            self.getPageHtml(_loupanUrl,_header)
            time.sleep(20)

        self.cursor.close()
        self.db.close()


    def getPageHtml(self,url,header):
        _htmlDoc = requests.get(url,header)
        _soup = BeautifulSoup(_htmlDoc.text,'html.parser', from_encoding='utf-8')
        _houseInfoList = _soup.find('ul',class_="resblock-list-wrapper").find_all('li',class_="resblock-list")

        # 获取新房简介信息
        for houseInfo in _houseInfoList:
            # 新房详情链接
            _houseInfoUrl = houseInfo.find('a')["href"]
            # 新房封面缩略图
            _surfacePlotThumbnail = houseInfo.find('a').find('img',class_="lj-lazy")["data-original"]
            # 新房名称
            _houseTitle = houseInfo.find('div',class_="resblock-name").find('a').text
            # 新房tag标识
            _houseTag = ''
            if houseInfo.find('div', class_="resblock-name").find_all('span', class_="resblock-type") != None:
                _houseTags = houseInfo.find('div',class_="resblock-name").find_all('span')
                for j in _houseTags:
                    _houseTag = _houseTag + " " + j.text

            # 新房位置信息
            _houseAreaInfo = houseInfo.find('div', class_="resblock-location").contents
            # 新房位置地区
            _houseArea = _houseAreaInfo[1].text
            # 新房位置详细地区
            _houseAreaDetail = _houseAreaInfo[5].text
            # 新房位置名称
            _houseAddressUrl = _houseAreaInfo[9]["href"]
            # 新房位置名称
            _houseAddressName = _houseAreaInfo[9].text

            # 新房房屋情况列表
            # 新房房屋大小
            _houseSize = houseInfo.find('div', class_="resblock-area").find('span').text

            # 新房tag标识
            _houseInfoTag = ''
            _houseInfoTags = houseInfo.find('div', class_="resblock-tag").find_all('span')
            for j in _houseInfoTags:
                _houseInfoTag = _houseInfoTag + " " + j.text

            # 新房价格情况
            _housePrice = houseInfo.find('div', class_="resblock-price")
            # 新房平均总价格
            _houseTotalPrice = ''
            if _housePrice.find('div', class_="second") != None:
                _houseTotalPrice = _housePrice.find('div', class_="second").text
            # 新房平均单价
            _houseUnitPrice = _housePrice.find('div', class_="main-price").find('span').text

            _louPanModel= LouPanModel(_houseInfoUrl,_surfacePlotThumbnail,_houseTitle,_houseTag,_houseArea,_houseAreaDetail,
                                      _houseAddressUrl,_houseAddressName,_houseSize,_houseInfoTag,_houseTotalPrice,_houseUnitPrice)
            self.saveHouseInfo(_louPanModel)

    def saveHouseInfo(self,LouPanModel):
        _insertSql = "insert into `loupaninfo`(HouseInfoUrl,SurfacePlotThumbnail,HouseTitle,HouseTag,HouseArea,HouseAreaDetail,HouseAddressUrl" \
                     ",HouseAddressName,HouseSize,HouseInfoTag,HouseTotalPrice,HouseUnitPrice,SysStatus,CDate) " \
                     "VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                     (LouPanModel.HouseInfoUrl,LouPanModel.SurfacePlotThumbnail,LouPanModel.HouseTitle,
                      LouPanModel.HouseTag,LouPanModel.HouseArea,LouPanModel.HouseAreaDetail,LouPanModel.HouseAddressUrl,LouPanModel.HouseAddressName,
                      LouPanModel.HouseSize,LouPanModel.HouseInfoTag,LouPanModel.HouseTotalPrice,LouPanModel.HouseUnitPrice,LouPanModel.SysStatus, LouPanModel.CDate)

        try:
            self.cursor.execute(_insertSql)
            self.db.commit()
        except Exception as ee:
            self.db.rollback()

t = LouPanSpider()
t.getHouseInfo()
# _now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
# # print(_now)