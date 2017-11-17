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

db = MySQLdb.connect("localhost", "root", "sdmp", "gyy_company", charset='utf8')
Recorddb = MySQLdb.connect("localhost", "root", "sdmp", "spiderdb", charset='utf8')

class LocationTrans:
    def __init__(self):
        self.cursor = db.cursor()
        self.recordcursor = Recorddb.cursor()
        self.TransNum = 100
        # self.GaodeAK = "557ad43c5b4de5e99629cf542ac91218"
        # self.GaodeAK = "511bf67f91aeb45bd8ba1f1062861b4d"
       	self.GaodeAK = "511bf67f91aeb45bd8ba1f1062861b4d"
        self.GetUrl = "http://restapi.amap.com/v3/geocode/geo?key=%s&address=%s&output=json"

    def GetLocations(self):
        try:
            StartRecordNum = self.GetTransRecord()
            EndRecordNum = StartRecordNum + self.TransNum
            SuccessTransNum = 0

            GetDataSql = 'Select ID,Name,Address from companyinfoes_test where Lng = 0 and lat = 0 ORDER BY _id limit %d , %d' % (int(StartRecordNum),int(self.TransNum))
            self.cursor.execute(GetDataSql)
            Data = self.cursor.fetchall()

            for item in Data:
                # 企业名称中跳过带空格 则跳过 换行\r\n
                if str(item[1]).strip().find(" ") > 0 or str(item[1]).strip().find("\r") > 0 or str(item[1]).strip().find("\n") > 0 or str(item[1]).strip() == "" or str(item[1]).strip() == "NULL" or str(item[1]).strip() == "null":
                    # 地址中跳过带空格 则无法定位 返回0,0 换行\r\n
                    if str(item[2]).strip().find(" ") > 0 or str(item[2]).strip().find("\r") > 0 or str(item[2]).strip().find("\n") > 0 or str(item[2]).strip() == "" or str(item[2]).strip() == "NULL" or str(item[2]).strip() == "null":
                        self.RecordResult(0, 0, item[0])
                        continue

                    # 地址正常 不包含空格 换行等符号
                    else:
                        LocationString = self.GetGeocoding(str(item[2]).strip())

                # 企业名称正常 不包含空格 换行等符号
                else:
                    # 企业名称获取经纬度
                    LocationString = self.GetGeocoding(str(item[1]).strip())

                    # 企业名称未获取到经纬度 切换成地址再次请求
                    if int(LocationString['status']) == 0 or len(LocationString['geocodes']) == 0:
                        # 地址中跳过带空格 则无法定位 返回0,0 换行\r\n
                        if str(item[2]).strip().find(" ") > 0 or str(item[2]).strip().find("\r") > 0 or str(item[2]).strip().find("\n") > 0 or str(item[2]).strip() == "" or str(item[2]).strip() == "NULL" or str(item[2]).strip() == "null":
                            self.RecordResult(0, 0, item[0])
                            continue

                        # 地址获取经纬度
                        LocationString = self.GetGeocoding(str(item[2]).strip());

                        # 地址未获取到经纬度 返回0,0
                        if int(LocationString['status']) == 0 or len(LocationString['geocodes']) == 0:
                            self.RecordResult(0, 0, item[0])
                            continue

                    Location = LocationString['geocodes'][0]['location']

                    # 获取经度
                    Location_Lng_Regex = re.compile(r'[\S\s]*?(?=,)')
                    LocationLng = re.search(Location_Lng_Regex, str(Location)).group()

                    # 获取纬度
                    Location_Lat_Regex = re.compile(r'(?<=,)[\S\s]*')
                    LocationLat = re.search(Location_Lat_Regex, str(Location)).group()

                    self.RecordResult(LocationLng, LocationLat,item[0])
                    SuccessTransNum = SuccessTransNum + 1

            self.SaveTransRecord(StartRecordNum,EndRecordNum,SuccessTransNum)
            self.cursor.close()
            self.cursor.close()
            print '经纬度转换完成！'
        except Exception, ex:
            print ex

    # 记录经纬度转换记录
    def SaveTransRecord(self,StartRecordNum,EndRecordNum,SuccessTransNum):
        CDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        InsertSql = 'Insert tranrecord(StartRecordNum,EndRecordNum,CDate,TransNum,SuccessTransNum) values(%d,%d,"%s",%d,%d)' % \
                    (int(StartRecordNum),int(EndRecordNum),CDate,int(self.TransNum),int(SuccessTransNum))
        self.recordcursor.execute(InsertSql)
        Recorddb.commit()

    # 获取经纬度转换记录 并返回已转换的行数
    def GetTransRecord(self):
         GetSql = 'select EndRecordNum from tranrecord ORDER BY CDate DESC limit 1'
         self.recordcursor.execute(GetSql)
         Data = self.recordcursor.fetchall()

         StartRecordNum = 0
         for item in Data:
             StartRecordNum = item[0]
             break
         return StartRecordNum

    #根据企业名称 或 地址 请求地理编码
    def GetGeocoding(self,Name):
        # str(item[1]).strip()
        GetLocationUrl = self.GetUrl % (self.GaodeAK, Name)
        request = urllib2.Request(GetLocationUrl)
        response = urllib2.urlopen(request)
        pageCode = response.read().decode('utf-8')
        LocationString = json.loads(pageCode)
        return LocationString

    def RecordResult(self,LocationLng,LocationLat,ID):
        print "Id : %s,Start : %s" % (ID, time.ctime())
        # 修改经度、纬度
        UpdateLocSql = 'Update companyinfoes_test set Lng = %f ,lat = %f where ID = "%s"' % (
            float(LocationLng), float(LocationLat), ID)
        self.cursor.execute(UpdateLocSql)
        db.commit()
        print "Id : %s,End : %s" % (ID, time.ctime())

_locationTrans = LocationTrans()
_locationTrans.GetLocations()
db.close()