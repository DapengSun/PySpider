# -*- coding: utf-8 -*-
import re
import urllib2
import sys
import MySQLdb
import time
import json

reload(sys)
sys.setdefaultencoding("utf-8")

# 1.由地名（省份、城市、街道等）得到其对应的高德地图坐标：
# http://api.map.baidu.com/geocoder/v2/?output=json&ak=你从高德申请到的Key&address=北京市
# 2.由坐标反解得到对应的地址：
#  http://api.map.baidu.com/geocoder/v2/?output=json&ak=你从高德申请到的Key&location=纬度（Latitude）,经度（Longitude）

db = MySQLdb.connect("192.168.0.106", "root", "caxa+2015", "gyy_company", charset='utf8')

class LocationTrans:
    def __init__(self):
        self.cursor = db.cursor()
        self.Updatecursor = db.cursor()
        self.GaodeAK = "bfe5ebf03b4befba2a060cd90ca4c4a6"
        self.GetUrl = "http://restapi.amap.com/v3/geocode/geo?key=%s&address=%s&output=json"

    def GetLocations(self):
        try:
            GetDataSql = 'Select ID,Address from companyinfoes where Lng is null or lat is null limit 1000'
            self.cursor.execute(GetDataSql)
            Data = self.cursor.fetchall()

            for item in Data:
                # 名字中跳过带空格
                if str(item[1]).strip().find(" ") > 0:
                    continue

                GetLocationUrl = self.GetUrl % (self.GaodeAK, str(item[1]).strip())
                request = urllib2.Request(GetLocationUrl)
                response = urllib2.urlopen(request)
                pageCode = response.read().decode('utf-8')
                LocationString = json.loads(pageCode)

                if str(item[1]).strip().find(" ") > 0:
                    self.RecordResult(0,0,item[0])
                    continue

                if int(LocationString['status']) != 1:
                    self.RecordResult(0, 0, item[0])
                    continue

                if len(LocationString['geocodes']) > 0 :
                    Location = LocationString['geocodes'][0]['location']

                    # 获取经度
                    Location_Lng_Regex = re.compile(r'[\S\s]*?(?=,)')
                    LocationLng = re.search(Location_Lng_Regex, str(Location)).group()

                    # 获取纬度
                    Location_Lat_Regex = re.compile(r'(?<=,)[\S\s]*')
                    LocationLat = re.search(Location_Lat_Regex, str(Location)).group()

                    self.RecordResult(LocationLng, LocationLat,item[0])

                    # 间隔2s
                    # time.sleep(2)

            self.Updatecursor.close()
            self.cursor.close()
            print '获取房屋经纬度完成！'
        except Exception, ex:
            print ex

    def RecordResult(self,LocationLng,LocationLat,ID):
        print "Id : %s,Start : %s" % (ID, time.ctime())
        # 修改经度、纬度
        UpdateLocSql = 'Update companyinfoes set Lng = %f ,lat = %f where ID = "%s"' % (
            float(LocationLng), float(LocationLat), ID)
        self.Updatecursor.execute(UpdateLocSql)
        db.commit()
        print "Id : %s,End : %s" % (ID, time.ctime())

_locationTrans = LocationTrans()
_locationTrans.GetLocations()
db.close()