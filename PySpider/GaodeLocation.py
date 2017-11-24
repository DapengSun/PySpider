# -*- coding: utf-8 -*-
import re
import urllib2
import sys
import MySQLdb
import time
import json
import socket

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
        self.TransNum = 226
        # self.GaodeAK = "bfe5ebf03b4befba2a060cd90ca4c4a6"
        # self.GaodeAK = "511bf67f91aeb45bd8ba1f1062861b4d"
        # self.GaodeAK = "84beb2508d80d838c08b8d852f8d295d"
        # self.GaodeAK = "86f72978c56d2db706e13b837291bfdd"
        # self.GaodeAK = "fb8c675b3b467f16e72e0675d91f5c7e"
        # self.GaodeAK = "ead865a77b035d32ed1bf175fe2c8844"
        # self.GaodeAK = "4d2a29bc41057af9a25b5dc642ce989b"
        self.GaodeAK = "054898a4850a16393c5500c136891de2"
        # self.GaodeAK = "127c22d33d2d220b7cc78e1dea33fbbd"
        # self.GaodeAK = "0be589f98b56fe8e83d917fa3136cd1d"
        # self.GaodeAK = "da002d3e42a6a2557f9592364a724338"
        # self.GaodeAK = "5923e6c61458e511eede02cffa3627f2"
        # self.GaodeAK = "75552d8f037aa7212510b2cdf764f488"
        # self.GaodeAK = "720efd606e1fe5e2be5c7bdf2599cbd3"
        # self.GaodeAK = "e568c28c09a4594714f11814f0a97aa4"
        # self.GaodeAK = "cc12ee3cdc407588cf75cd0d4a31d745"
        # self.GaodeAK = "9ac478dc2ebf81aba03e388d3dda037b"
        # self.GaodeAK = "e53c2f3359745f80849f9f71e3812528"
        # self.GaodeAK = "a68bd488c37208e625887d26d06246b7"
        # self.GaodeAK = "9b102ae4ce94d24dfb3c7569fe8988cf"

        self.GetUrl = "http://restapi.amap.com/v3/geocode/geo?key=%s&address=%s&output=json"

    def GetLocations(self):
        try:
            StartRecordNum = self.GetFirstPosition()
            EndRecordNum = StartRecordNum - self.TransNum
            SuccessTransNum = 0

            if self.IsFinishTrans(EndRecordNum):
                GetDataSql = 'Select ID,Name,Address from companyinfoes_test where Lng = 0 and lat = 0 ORDER BY _id limit %d , %d' % (int(EndRecordNum),int(self.TransNum))
                self.cursor.execute(GetDataSql)
                Data = self.cursor.fetchall()

                for item in Data:
                    Name = str(item[1]).strip().replace(" ","%20")
                    Address = str(item[2]).strip().replace(" ", "%20")

                    # 企业名称中跳过带空格 则跳过 换行\r\n
                    if Name.strip().find("\r") > 0 or Name.strip().find("\n") > 0 or Name.strip() == "" or Name.strip() == "NULL" or Name.strip() == "null":
                        # 地址中跳过带空格 则无法定位 返回0,0 换行\r\n
                        if Address.strip().find("\r") > 0 or Address.strip().find("\n") > 0 or Address.strip() == "" or Address.strip() == "NULL" or Address.strip() == "null":
                            self.RecordResult(0, 0, item[0])
                            continue

                        # 地址正常 不包含空格 换行等符号
                        else:
                            LocationString = self.GetGeocoding(Address)

                    # 企业名称正常 不包含空格 换行等符号
                    else:
                        # 企业名称获取经纬度
                        LocationString = self.GetGeocoding(Name)

                        # 企业名称未获取到经纬度 切换成地址再次请求
                        if int(LocationString['status']) == 0 or len(LocationString['geocodes']) == 0:
                            # 地址中跳过带空格 则无法定位 返回0,0 换行\r\n
                            if Address.strip().find(" ") > 0 or Address.strip().find("\r") > 0 or Address.strip().find("\n") > 0 or Address.strip() == "" or Address.strip() == "NULL" or Address.strip() == "null":
                                self.RecordResult(0, 0, item[0])
                                continue

                            # 地址获取经纬度
                            LocationString = self.GetGeocoding(Address);

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
            else:
                print '超出范围，转换已全部完成！'
        except Exception, ex:
            print ex

    # 获取起始位置
    def GetFirstPosition(self):
        GetSql = 'select EndRecordNum from tranrecord ORDER BY CDate DESC limit 1'
        self.recordcursor.execute(GetSql)
        Data = self.recordcursor.fetchall()

        StartRecordNum = 0
        for item in Data:
            StartRecordNum = item[0]
            break

        # 记录表为空 则获取当前未转换长度作为起始节点
        if StartRecordNum == 0:
            GetSql = 'Select Count(*) from gyy_company.companyinfoes_test where Lng = 0 and lat = 0'
            self.cursor.execute(GetSql)
            Data = self.cursor.fetchall()

            for item in Data:
                StartRecordNum = item[0]
                break

        return StartRecordNum

    # 转换是否结束
    def IsFinishTrans(self,EndRecordNum):
        if EndRecordNum >= 0:
            return True
        else:
            return False

    # 记录经纬度转换记录
    def SaveTransRecord(self,StartRecordNum,EndRecordNum,SuccessTransNum):
        CDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        InsertSql = 'Insert tranrecord(StartRecordNum,EndRecordNum,CDate,TransNum,SuccessTransNum,GaodeKey) values(%d,%d,"%s",%d,%d,"%s")' % \
                    (int(StartRecordNum),int(EndRecordNum),CDate,int(self.TransNum),int(SuccessTransNum),self.GaodeAK)
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

        for i in range(1,5):
            try:
                request = urllib2.Request(GetLocationUrl)
                response = urllib2.urlopen(request,timeout = 5)
                break
            except Exception,ex:
                print ex
                time.sleep(1)
                print('HTTP Request Failed！Try %d Times！') % i
                continue

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