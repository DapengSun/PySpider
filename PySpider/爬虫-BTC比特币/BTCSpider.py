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

class btc_Price:
    def __init__(self):
        self.BaseUrl = 'https://www.bitstamp.net'
        self.BaseAjaxUrl = '/api/v2/ticker/btcusd/'
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = { 'User-Agent':self.user_agent }
        cursor = db.cursor()
        self.cuesor = cursor

    # 获取BTC价格
    def GetBTCPrice(self):
        try:
            BTCPriceUrl = self.BaseUrl + self.BaseAjaxUrl;
            request = urllib2.Request(BTCPriceUrl, headers=self.headers)
            response = urllib2.urlopen(request)
            pageCode = response.read().decode('utf-8')

            if not pageCode:
                print "页面加载失败...."
                return None

            BTCPrice = json.loads(pageCode)

            LastPriceUSD = float(BTCPrice['last'])
            DaysLow = float(BTCPrice['low'])
            DaysHigh = float(BTCPrice['high'])
            DaysOpen = float(BTCPrice['open'])
            DaysVolume = float(BTCPrice['volume'])
            DailyChange = LastPriceUSD - DaysOpen
            DailyChangePercent = round(( LastPriceUSD - DaysOpen ) / DaysOpen , 6)

            # 当前时间
            CDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            Sql = 'Insert into btc_price(Id,LastPriceUSD,DailyChange,DailyChangePercent,DaysLow,DaysHigh,DaysOpen,DaysVolume,CDate) values(replace(UUID(), "-", ""),"%s","%s","%s","%s","%s","%s","%s","%s")' % (
                  LastPriceUSD, DailyChange, DailyChangePercent, DaysLow, DaysHigh,DaysOpen,DaysVolume,CDate)
            self.cuesor.execute(Sql)
            db.commit()

        except Exception, ex:
            print ex

# _btc_Price = btc_Price()
# _btc_Price.GetBTCPrice()