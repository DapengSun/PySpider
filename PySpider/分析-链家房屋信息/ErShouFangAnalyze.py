#coding:utf-8
import pymysql

class ErShorFangAnalyze():
    def __init__(self):
        self.db = pymysql.connect(host="localhost",user="root",password="sdmp",db="spider",port=3306)
        self.cursor = self.db.cursor()

    def analyzeData(self):
        _selectSql = "SELECT * FROM `ershoufanginfo` WHERE SysStatus = 0"

        self.cursor.execute(_selectSql)
        _data = self.cursor.fetchall()
        _description = [i[0] for i in self.cursor.description]
        _erShorFangData = [dict(zip(_description,i)) for i in _data]
        _houseAreaList = [i['HouseArea'] for i in _erShorFangData]

        self.formatData(_houseAreaList)
        # print(_houseAreaList)

    def formatData(self,HouseAreaList):
        HouseAreaList = [i for i in HouseAreaList if i != None]

        # 房屋地区索引
        _houseAreaIndex = list(set(HouseAreaList))
        # 房屋地区计数
        _houseAreaCount = []
        for i in _houseAreaIndex:
            _houseAreaCount.append(HouseAreaList.count(i))

        _houseAreaAnalyze = list(zip(_houseAreaIndex,_houseAreaCount))
        _data2 = self.yieldAreaData(_houseAreaAnalyze)

        _data3 = []
        for i in _data2:
            _data3.append(i)
        print(_data3)

    def yieldAreaData(self,HouseAreaAnalyze):
        for i in HouseAreaAnalyze:
            data = {
                "name" : i[0],
                "y": i[1],
            }
            yield data

t = ErShorFangAnalyze()
t.analyzeData()