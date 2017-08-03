#coding:utf-8
import re
import urllib2
import sys
import MySQLdb
import time
reload(sys)
sys.setdefaultencoding( "utf-8" )

db = MySQLdb.connect("localhost", "root", "sdmp", "spiderdb",charset='utf8')

class Weather_Forecast:
    def __init__(self):
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = { 'User-Agent':self.user_agent }
        cursor = db.cursor()
        self.cuesor = cursor

    def getProviceContent(self):
        try:
            ProviceUrl = 'http://weather.sina.com.cn/'
            request = urllib2.Request(ProviceUrl,headers=self.headers)
            response = urllib2.urlopen(request)
            pageCode = response.read().decode('utf-8')

            if not pageCode:
                print "页面加载失败...."
                return None

            Weather_Provice_Regex = re.compile(r'(?<=<div class="wnbc_piC">)[\S\s]*?(?=</div>)')
            Weather_Provices = re.findall(Weather_Provice_Regex,pageCode)
            for Provices in Weather_Provices:

                Provices_Regex = re.compile(r'<a[\S\s]*?</a>')
                ProvicesList = re.findall(Provices_Regex,Provices)

                for Provice in ProvicesList:
                    # 省份名称
                    Provices_NameString_Regex = re.compile(r'<a[\S\s]*?</a>')
                    ProviceNameString = re.search(Provices_NameString_Regex, Provice).group()
                    Provices_Name_Regex = re.compile(r'(?<=>)[\S\s]*?(?=</a>)')
                    Provice_Name = re.search(Provices_Name_Regex, ProviceNameString).group()
                    # print Provice_Name

                    # 省份天气URL
                    Provice_Url_Regex = re.compile(r'(?<=href=")[\S\s]*?(?=")')
                    Provice_Url = re.search(Provice_Url_Regex, Provice).group()
                    # print Provice_Url
                    self.getWeatherContent(Provice_Name,Provice_Url)
        except Exception,ex:
            print ex

    def getWeatherContent(self,ProviceName,Provice_Url):
        try:
            WeatherUrl = Provice_Url
            request = urllib2.Request(WeatherUrl, headers=self.headers)
            response = urllib2.urlopen(request)
            pageCode = response.read().decode('utf-8')

            if not pageCode:
                print "页面加载失败...."
                return None

            # 当前时间
            CDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            # 按照市划分
            CityAndCountysRegex = re.compile(r'<div class="wd_cmain">[\S\s]*?</div>[\S\s]*?</div>')
            CityAndCountys = re.findall(CityAndCountysRegex,pageCode)

            # 遍历市
            for CityAndCounty in CityAndCountys:
                # 市名称
                CityRegex = re.compile(r'(?<=<div class="wd_cmh">)[\S\s]*?(?=</div>)')
                CityName = re.search(CityRegex, CityAndCounty).group().strip('\r\n').replace("\n", "").strip()
                # print CityName

                Weathers_Regex = re.compile(r'<table class="wd_cm_table">[\S\s]*?</table>')
                Weathers = re.findall(Weathers_Regex,CityAndCounty)
                # 按县/区遍历
                for Weather in Weathers:
                    City_Weather_Detail_Regex = re.compile(r'(?<=<tr>)[\S\s]*?</tr>')
                    CityWeatherDetails = re.findall(City_Weather_Detail_Regex,Weather)
                    for CityWeatherDetail in CityWeatherDetails:
                        # 按天气详情（td）遍历
                        Weather_Detail_Regex = re.compile(r'<td[\S\s]*?td>')
                        WeatherDetails = re.findall(Weather_Detail_Regex,CityWeatherDetail)

                        # 区县名称
                        CountyNameStringRegex = re.compile(r'<a href=[\S\s]*?</a>')
                        CountyNameString = re.search(CountyNameStringRegex, WeatherDetails[0]).group()
                        CountyNameRegex = re.compile(r'(?<=>)[\S\s]*?(?=</a>)')
                        CountyName = re.search(CountyNameRegex, CountyNameString).group()
                        # print CountyName

                        # 天气状况（早）
                        Morning_WeatherConditionRegex = re.compile(r'(?<=<p class="wd_cmt_txt">)[\S\s]*?(?=</p>)')
                        Morning_WeatherCondition = re.search(Morning_WeatherConditionRegex, WeatherDetails[1]).group()
                        # print Morning_WeatherCondition

                        # 风力方向（早）
                        Morning_WindConditionStringRegex = re.compile(r'(?<=<td style="width:125px;")[\S\s]*?(?=</td>)')
                        Morning_WindConditionString = re.search(Morning_WindConditionStringRegex, WeatherDetails[2]).group()
                        Morning_WindConditionRegex = re.compile(r'(?<=>)[\S\s]*')
                        Morning_WindCondition= re.search(Morning_WindConditionRegex, Morning_WindConditionString).group().replace(' &lt;','<')
                        # print Morning_WindCondition

                        # 最高温度（早）
                        Morning_TopTemperatureRegex = re.compile(r'(?<=<td style="width:125px;">)[\S\s]*?(?=</td>)')
                        Morning_TopTemperature = re.search(Morning_TopTemperatureRegex, WeatherDetails[3]).group()
                        # print Morning_TopTemperature

                        # 天气状况（晚）
                        Evening_WeatherConditionRegex = re.compile(r'(?<=<p class="wd_cmt_txt">)[\S\s]*?(?=</p>)')
                        Evening_WeatherCondition = re.search(Evening_WeatherConditionRegex, WeatherDetails[4]).group()
                        # print Evening_WeatherCondition

                        # 风力方向（晚）
                        Evening_WindConditionStringRegex = re.compile(r'(?<=<td style="width:125px;")[\S\s]*?(?=</td>)')
                        Evening_WindConditionString = re.search(Evening_WindConditionStringRegex, WeatherDetails[5]).group()
                        Evening_WindConditionRegex = re.compile(r'(?<=>)[\S\s]*')
                        Evening_WindCondition = re.search(Evening_WindConditionRegex, Evening_WindConditionString).group().replace(' &lt;','<')
                        # print Evening_WindCondition

                        # 最低温度（晚）
                        Evening_LowTemperatureRegex = re.compile(r'(?<=<td style="width:125px;">)[\S\s]*?(?=</td>)')
                        Evening_LowTemperature = re.search(Evening_LowTemperatureRegex, WeatherDetails[6]).group()
                        # print Evening_LowTemperature

                        Sql = 'Insert into weatherforecastdata(ProviceName,ProviceWeatherUrl,CityName,CountyName,MorningWeatherCondition,MorningWindCondition,' \
                              'MorningTopTemperature,EveningWeatherCondition,EveningWindCondition,EveningLowTemperature,CDate) values("%s","%s","%s","%s","%s","%s"' \
                              ',"%s","%s","%s","%s","%s")'% (ProviceName, Provice_Url, CityName,CountyName,Morning_WeatherCondition,Morning_WindCondition,Morning_TopTemperature,
                              Evening_WeatherCondition,Evening_WindCondition,Evening_LowTemperature,CDate)
                        self.cuesor.execute(Sql)
                        db.commit()
        except Exception,ex:
            print ex

_weather = Weather_Forecast()
_weather.getProviceContent()
db.close()