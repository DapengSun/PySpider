#coding:utf-8
import pymysql

from LianJiaJob.Common import Common
from LianJiaJob.EnumType import SpiderJobStatus
from LianJiaSpider.ErShouFangSearchSpider import SearchInfoModel
from RedisOper.RedisOperHelper import RedisOperHelper


class LianJiaSpiderSync:
    def __init__(self):
        try:
            self.db = pymysql.connect(host="localhost",user="root",password="sdmp",db="spider",port=3306)
            self.cursor = self.db.cursor()
        except Exception as e:
            print(e)

    # 保存任务结果
    def saveJobResult(self):
        try:
            _sql = "Select * from searchinfo where Status = '%s'" % (SpiderJobStatus.已完成.value)

            self.cursor.execute(_sql)
            _result = self.cursor.fetchall()
            _description = [i[0] for i in self.cursor.description]

            _common = Common()
            _resultDict = _common.getResultDict(_description,_result)
            _redisOper = RedisOperHelper()

            _currentSearchId = ''
            for item in _resultDict:
                _currentSearchId = item['SearchId']
                _searchId = "%s*" % (item['SearchId'])
                # 获取Id为前缀的爬虫结果
                _resultList = _redisOper.keys(_searchId)

                if len(_resultList) > 0:
                    for item in _resultList:
                        _itemList = _redisOper.hashHgetAll(item)
                        _searchInfoModel = SearchInfoModel(_itemList['SearchId'],_itemList['HouseInfoUrl'], _itemList['HouseInfoCode'], _itemList['SurfacePlotThumbnail'],
                                                           _itemList['HouseTitle'], _itemList['HouseTag'], _itemList['HouseAddressUrl'],
                                                           _itemList['HouseAddressName'], _itemList['HousePattern'],_itemList['HouseSize'],_itemList['HouseOrientation'],
                                                           _itemList['HouseCover'], _itemList['HouseElevator'],_itemList['HouseFloor'],
                                                           _itemList['HouseYear'], _itemList['HouseArea'],_itemList['HousePeoperNum'],_itemList['HouseLookNum'],
                                                           _itemList['HouseFollowSubway'], _itemList['HouseTaxFree'],_itemList['HouseHasKey'],
                                                           _itemList['HouseTotalPrice'], _itemList['HouseUnitPrice'])


                        self.saveHouseInfo(_searchInfoModel)

                    _updateSearchSql = "Update searchinfo Set Status = '%s' Where SearchId = '%s'" % (SpiderJobStatus.结果入库.value, _currentSearchId)
                    self.cursor.execute(_updateSearchSql)
                    self.db.commit()

                    # 删除redis中爬取结果
                    _redisOper.delKeys(*_resultList)

        except Exception as ex:
            print(ex)
            _updateSearchSql = "Update searchinfo Set Status = '%s' Where SearchId = '%s'" % (SpiderJobStatus.异常.value, _currentSearchId)
            self.cursor.execute(_updateSearchSql)
            self.db.commit()
        finally:
            self.cursor.close()
            self.db.close()


    def saveHouseInfo(self,SearchInfoModel):

        _insertSql = "insert into `searchdetailinfo`(SearchId,HouseInfoUrl,HouseInfoCode,SurfacePlotThumbnail,HouseTitle,HouseTag,HouseAddressUrl,HouseAddressName," \
                     "HousePattern,HouseSize,HouseOrientation,HouseCover,HouseElevator,HouseFloor,HouseYear,HouseArea,HousePeoperNum," \
                     "HouseLookNum,HouseFollowSubway,HouseTaxFree,HouseHasKey,HouseTotalPrice,HouseUnitPrice,SysStatus,CDate) " \
                     "VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                     (SearchInfoModel.SearchId,SearchInfoModel.HouseInfoUrl,SearchInfoModel.HouseInfoCode,SearchInfoModel.SurfacePlotThumbnail,SearchInfoModel.HouseTitle,
                      SearchInfoModel.HouseTag,SearchInfoModel.HouseAddressUrl,SearchInfoModel.HouseAddressName,SearchInfoModel.HousePattern,SearchInfoModel.HouseSize,
                      SearchInfoModel.HouseOrientation,SearchInfoModel.HouseCover,SearchInfoModel.HouseElevator,SearchInfoModel.HouseFloor,SearchInfoModel.HouseYear,
                      SearchInfoModel.HouseArea, SearchInfoModel.HousePeoperNum,SearchInfoModel.HouseLookNum, SearchInfoModel.HouseFollowSubway,
                      SearchInfoModel.HouseTaxFree, SearchInfoModel.HouseHasKey,SearchInfoModel.HouseTotalPrice, SearchInfoModel.HouseUnitPrice,
                      SearchInfoModel.SysStatus, SearchInfoModel.CDate)

        try:
            self.cursor.execute(_insertSql)
            self.db.commit()
        except Exception as ee:
            self.db.rollback()
            raise

# t = LianJiaSpiderSync()
# t.saveJobResult()