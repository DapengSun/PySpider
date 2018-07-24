#coding:utf-8
import re
import requests
import pymysql
import datetime
import time
from  decimal import Decimal
from bs4 import BeautifulSoup

class ErShouFangInfoModel():
    def __init__(self,HouseInfoUrl,HouseInfoCode,SurfacePlotThumbnail,
                 HouseTitle,HouseTag,HouseAddressUrl,HouseAddressName,
                 HousePattern,HouseSize,HouseOrientation,HouseCover,
                 HouseElevator,HouseFloor,HouseYear,HouseArea,HousePeoperNum,
                 HouseLookNum,HouseFollowSubway,HouseTaxFree,HouseHasKey,
                 HouseTotalPrice,HouseUnitPrice):
        self.HouseInfoUrl = HouseInfoUrl
        self.HouseInfoCode = HouseInfoCode
        self.SurfacePlotThumbnail = SurfacePlotThumbnail
        self.HouseTitle = HouseTitle
        self.HouseTag = HouseTag
        self.HouseAddressUrl = HouseAddressUrl
        self.HouseAddressName = HouseAddressName
        self.HousePattern = HousePattern
        self.HouseSize = HouseSize
        self.HouseOrientation = HouseOrientation
        self.HouseCover = HouseCover
        self.HouseElevator = HouseElevator
        self.HouseFloor = HouseFloor
        self.HouseYear = HouseYear
        self.HouseArea = HouseArea
        self.HousePeoperNum = HousePeoperNum
        self.HouseLookNum = HouseLookNum
        self.HouseFollowSubway = HouseFollowSubway
        self.HouseTaxFree = HouseTaxFree
        self.HouseHasKey = HouseHasKey
        self.HouseTotalPrice = HouseTotalPrice
        self.HouseUnitPrice = HouseUnitPrice
        self.SysStatus = 0
        self.CDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

class ErShouFangSpider():
    def __init__(self):
        try:
            self.db = pymysql.connect(host="localhost",user="root",password="sdmp",db="spider",port=3306)
            self.cursor = self.db.cursor()
        except Exception as e:
            print(e)

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

        for i in range(2,3):
            _erShoufangUrl = '%s/pg%s/' % (_baseUrl,i)
            # print(_pgNum)
            self.getPageHtml(_erShoufangUrl,_header)
            self.cursor.close()
            self.db.close()


    def getPageHtml(self,url,header):
        _htmlDoc = requests.get(url,header)
        _soup = BeautifulSoup(_htmlDoc.text,'html.parser', from_encoding='utf-8')
        _houseInfoList = _soup.find('ul',class_="sellListContent").find_all('li',class_="clear LOGCLICKDATA")

        # 获取二手房简介信息
        for houseInfo in _houseInfoList:
            # 二手房详情链接
            _houseInfoUrl = houseInfo.find('a')["href"]
            # 二手房编码
            _houseInfoCode = houseInfo.find('a')["data-housecode"]
            # 二手房封面缩略图
            _surfacePlotThumbnail = houseInfo.find('a').find('img',class_="lj-lazy")["data-original"]
            # 二手房名称
            _houseTitle = houseInfo.find('div',class_="info clear").find('div',class_="title").find('a').text
            # 二手房tag标识
            _houseTag = ''
            if houseInfo.find('div', class_="info clear").find('div', class_="title").find('span') != None:
                _houseTag = houseInfo.find('div', class_="info clear").find('div', class_="title").find('span').text
            # 二手房位置URL
            _houseAddressUrl = houseInfo.find('div', class_="info clear").find('div', class_="address").find('a')["href"]
            # 二手房位置名称
            _houseAddressName = houseInfo.find('div', class_="info clear").find('div', class_="address").find('a').text

            # 二手房房屋情况列表
            _houseDetailInfoList = houseInfo.find('div', class_="info clear").find('div', class_="address").find_all('span', class_="divide")
            # 二手房房屋格局
            _housePattern = ''
            if len(_houseDetailInfoList) >= 1:
                _housePattern = _houseDetailInfoList[0].next_sibling
            # 二手房房屋大小
            _houseSize = ''
            if len(_houseDetailInfoList) >= 2:
                _houseSize = _houseDetailInfoList[1].next_sibling
            # 二手房房屋朝向
            _houseOrientation = ''
            if len(_houseDetailInfoList) >= 3:
                _houseOrientation = _houseDetailInfoList[2].next_sibling
            # 二手房房屋装修情况
            _houseCover = ''
            if len(_houseDetailInfoList) >= 4:
                _houseCover = _houseDetailInfoList[3].next_sibling
            # 二手房房屋有无电梯
                _houseElevator = ''
            if len(_houseDetailInfoList) >= 5:
                _houseElevator = _houseDetailInfoList[4].next_sibling

            # 二手房位置情况
            _housePositionInfo = houseInfo.find('div', class_="info clear").find('div', class_="flood").find_all('div', class_="positionInfo")[0].contents
            # 二手房楼层
            _houseFloor = _housePositionInfo[0]
            # 二手房年代
            _houseYear = _housePositionInfo[2]
            # 二手房地区
            _houseArea = _housePositionInfo[4].text

            # 二手房关注情况
            _houseFollow = houseInfo.find('div', class_="info clear").find('div', class_="followInfo")
            # 二手房关注人数
            _re = re.compile(r'[\S\s]*?(?=人关注)')
            _housePeoperNum = re.search(_re, _houseFollow.contents[0]).group()
            # 二手房带看人数
            _re = re.compile(r'[\S\s]*?(?=次带看)')
            _houseLookNum = re.search(_re, _houseFollow.contents[2]).group()
            # 二手房距离地铁位置
            _houseFollowSubway = ''
            if _houseFollow.find('span',class_="subway") != None:
                _houseFollowSubway = _houseFollow.find('span',class_="subway").text
            # 二手房免税
            _houseTaxFree = ''
            if _houseFollow.find('span',class_="taxfree") != None:
                _houseTaxFree = _houseFollow.find('span',class_="taxfree").text
            # 二手房是否能随时看房
            _houseHasKey = ''
            if _houseFollow.find('span',class_="haskey") != None:
                _houseHasKey = _houseFollow.find('span',class_="haskey").text

            # 二手房价格情况
            _housePrice = houseInfo.find('div', class_="info clear").find('div', class_="priceInfo")
            # 二手房价格
            _houseTotalPrice = Decimal(_housePrice.find('div', class_="totalPrice").find('span').text)
            # 二手房单价
            _houseUnitPriceText = _housePrice.find('div', class_="unitPrice").find('span').text
            _re = re.compile(r'(?<=单价).*?(?=元/平米)')
            _houseUnitPrice = Decimal(re.search(_re, _houseUnitPriceText).group())

            _erShouFangModel= ErShouFangInfoModel(_houseInfoUrl,_houseInfoCode,_surfacePlotThumbnail,_houseTitle,_houseTag,_houseAddressUrl,
                                                  _houseAddressName,_housePattern,_houseSize,_houseOrientation,_houseCover,_houseElevator,
                                                  _houseFloor,_houseYear,_houseArea,_housePeoperNum,_houseLookNum,_houseFollowSubway,_houseTaxFree,
                                                  _houseHasKey,_houseTotalPrice,_houseUnitPrice)
            self.saveHouseInfo(_erShouFangModel)

    def saveHouseInfo(self,ErShouFangInfoModel):
        _insertSql = "insert into `ershoufanginfo`(HouseInfoUrl,HouseInfoCode,SurfacePlotThumbnail,HouseTitle,HouseTag,HouseAddressUrl,HouseAddressName," \
                     "HousePattern,HouseSize,HouseOrientation,HouseCover,HouseElevator,HouseFloor,HouseYear,HouseArea,HousePeoperNum," \
                     "HouseLookNum,HouseFollowSubway,HouseTaxFree,HouseHasKey,HouseTotalPrice,HouseUnitPrice,SysStatus,CDate) " \
                     "VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                     (ErShouFangInfoModel.HouseInfoUrl,ErShouFangInfoModel.HouseInfoCode,ErShouFangInfoModel.SurfacePlotThumbnail,ErShouFangInfoModel.HouseTitle,
                      ErShouFangInfoModel.HouseTag,ErShouFangInfoModel.HouseAddressUrl,ErShouFangInfoModel.HouseAddressName,ErShouFangInfoModel.HousePattern,ErShouFangInfoModel.HouseSize,
                      ErShouFangInfoModel.HouseOrientation,ErShouFangInfoModel.HouseCover,ErShouFangInfoModel.HouseElevator,ErShouFangInfoModel.HouseFloor,ErShouFangInfoModel.HouseYear,
                      ErShouFangInfoModel.HouseArea, ErShouFangInfoModel.HousePeoperNum,ErShouFangInfoModel.HouseLookNum, ErShouFangInfoModel.HouseFollowSubway,
                      ErShouFangInfoModel.HouseTaxFree, ErShouFangInfoModel.HouseHasKey,ErShouFangInfoModel.HouseTotalPrice, ErShouFangInfoModel.HouseUnitPrice,
                      ErShouFangInfoModel.SysStatus, ErShouFangInfoModel.CDate)

        try:
            self.cursor.execute(_insertSql)
            self.db.commit()
        except Exception as ee:
            self.db.rollback()

t = ErShouFangSpider()
t.getHouseInfo()
# _now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
# # print(_now)