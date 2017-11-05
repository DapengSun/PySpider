#coding:utf-8
import re
import json
import urllib2
import sys
import MySQLdb
import time
from datetime import datetime
reload(sys)
sys.setdefaultencoding( "utf-8" )

db = MySQLdb.connect("localhost", "root", "sdmp", "spiderdb",charset='utf8')

class btc_Price_Statistics:
    def __init__(self):
        self.BaseUrl = 'https://www.bitstamp.net'
        self.BaseAjaxUrl = '/api/v2/ticker/btcusd/'
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = { 'User-Agent':self.user_agent }
        cursor = db.cursor()
        self.cuesor = cursor

    # 统计当日最新BTC价格
    def StatisticsBTCPrice(self):
        try:
            Sql = 'SELECT * FROM btc_price WHERE DATE(CDate) = DATE(NOW()) ORDER BY CDate DESC LIMIT 1'
            self.cuesor.execute(Sql)
            rows = self.cuesor.fetchall()

            if len(rows) > 0:
                LastPriceUSD = float(rows[0][2])
                DaysLow = float(rows[0][5])
                DaysHigh = float(rows[0][6])
                DaysOpen = float(rows[0][7])
                DaysVolume = float(rows[0][8])
                DailyChange = LastPriceUSD - DaysOpen
                DailyChangePercent = round(( LastPriceUSD - DaysOpen ) / DaysOpen , 6)

                # 当前时间
                CDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                Sql = 'Select * from btc_price_statistics where Date(CDate) = Date(Now())'
                self.cuesor.execute(Sql)
                rows = self.cuesor.fetchall()
                if len(rows)  > 0:
                    Sql = 'Update btc_price_statistics Set LastPriceUSD = "%s",DailyChange = "%s",DailyChangePercent = "%s",DaysLow = "%s",DaysHigh = "%s",DaysVolume = "%s",CDate = "%s" where Date(CDate) = Date(Now())' % (
                        LastPriceUSD, DailyChange, DailyChangePercent, DaysLow, DaysHigh, DaysVolume, CDate)
                else:
                    Sql = 'Insert into btc_price_statistics(Id,LastPriceUSD,DailyChange,DailyChangePercent,DaysLow,DaysHigh,DaysOpen,DaysVolume,CDate) values(replace(UUID(), "-", ""),"%s","%s","%s","%s","%s","%s","%s","%s")' % (
                          LastPriceUSD, DailyChange, DailyChangePercent, DaysLow, DaysHigh,DaysOpen,DaysVolume,CDate)
                self.cuesor.execute(Sql)
                db.commit()

        except Exception, ex:
            print ex

_btc_Price_Statistics = btc_Price_Statistics()
_btc_Price_Statistics.StatisticsBTCPrice()