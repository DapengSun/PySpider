#coding:utf-8
import time
import BTCSpider
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

def sleeptime(hour,min,sec):
    return hour*3600 + min*60 + sec;

second = sleeptime(0, 5, 0);

while 1==1:
    CDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    _btc_Price = BTCSpider.btc_Price()
    _btc_Price.GetBTCPrice()

    content = u'BTC实时获取，获取时间为:%s' %  str(CDate).decode('utf-8')
    print content;
    time.sleep(second);
