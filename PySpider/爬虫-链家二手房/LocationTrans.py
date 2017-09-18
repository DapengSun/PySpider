# -*- coding: utf-8 -*-
import re
import urllib2
import sys
import MySQLdb
import time
import json
reload(sys)
sys.setdefaultencoding( "utf-8" )

# 1.由地名（省份、城市、街道等）得到其对应的百度地图坐标：
# http://api.map.baidu.com/geocoder/v2/?output=json&ak=你从百度申请到的Key&address=北京市
# 2.由坐标反解得到对应的地址：
#  http://api.map.baidu.com/geocoder/v2/?output=json&ak=你从百度申请到的Key&location=纬度（Latitude）,经度（Longitude）

db = MySQLdb.connect("localhost", "root", "sdmp", "spiderdb",charset='utf8')
class LocationTrans:
    def __init__(self):
        self.cursor = db.cursor()
        self.Updatecursor = db.cursor()
        self.baiduAK = "XKdYj5FvGtXml1pkDmng5yhOssnteFWe"
        self.GetUrl = "http://api.map.baidu.com/geocoder/v2/?output=json&ak=%s&address=%s"

    def GetLocations(self,Date):
        try:
            GetHouseSql = 'Select ID,HouseName from Houseinfo where Date(CDate) = "%s"' % str(Date)

            self.cursor.execute(GetHouseSql)
            HouseInfo = self.cursor.fetchall()


            for item in HouseInfo:
                GetLocationUrl = self.GetUrl % (self.baiduAK,str(item[1]))
                request = urllib2.Request(GetLocationUrl)
                response = urllib2.urlopen(request)
                pageCode = response.read().decode('utf-8')

                LocationString = json.loads(pageCode)

                if LocationString['status'] == 1:
                    continue

                # 获取经度
                LocationLng = LocationString['result']['location']['lng']
                # 获取纬度
                LocationLat = LocationString['result']['location']['lat']
                # 修改时间
                UpdateDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                # 修改经度、纬度
                UpdateLocSql = 'Update Houseinfo set HouseLocationlng = %f ,HouseLocationlat = %f , UpdateDate = "%s" where ID = %d' % (float(LocationLng) , float(LocationLat) , UpdateDate,int(item[0]))
                self.Updatecursor.execute(UpdateLocSql)
                db.commit()

            self.Updatecursor.close()
            self.cursor.close()
            print '获取房屋经纬度完成！'
        except Exception,ex:
            print ex

_locationTrans = LocationTrans()
Date = time.strftime('%Y-%m-%d',time.gmtime())
_locationTrans.GetLocations(Date)
db.close()