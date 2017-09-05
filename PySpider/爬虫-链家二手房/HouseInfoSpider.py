# -*- coding: utf-8 -*-
import re
import urllib2
import sys
import MySQLdb
import time
import LocationTrans
reload(sys)
sys.setdefaultencoding( "utf-8" )

db = MySQLdb.connect("localhost", "root", "sdmp", "spiderdb",charset='utf8')
class House:
    def __init__(self):
        self.pageIndex = 1
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        # 初始化headers
        self.Headers = {'User-Agent': self.user_agent}
        cursor = db.cursor()
        self.cuesor = cursor

    def loadPage(self,pageIndex):
        try:
            url = 'https://bj.lianjia.com/ershoufang/pg' + str(pageIndex) + '/'
            request = urllib2.Request(url,headers=self.Headers)
            response = urllib2.urlopen(request)
            pageCode = response.read().decode('utf-8')

            if not pageCode:
                print "页面加载失败...."
                return None

            # print pageCode

            content = re.compile(r'<li class="clear">([\S\s]*?)</li>')
            items = re.findall(content,pageCode)

            for item in items:
                # 标题
                parTitle = re.compile(r'(?<=<div class="title">)[\S\s]*?(?=</div>)')
                parTitle = re.search(parTitle, item)
                patTitle = parTitle.group()
                HouseTitle = re.compile(r'(<a.*>)([\s\S]*)(</a>)')
                HouseTitle = re.search(HouseTitle,patTitle).group(2).strip()
                # print HouseTitle

                # 房屋信息
                parHouseInfo = re.compile(r'(?<=<div class="houseInfo">)[\S\s]*?(?=</div>)')
                parHouseInfo = re.search(parHouseInfo, item)
                parHouseInfo = parHouseInfo.group()

                HouseInfo = re.split(r'\|',parHouseInfo)
                # 小区名称
                HouseName = HouseInfo[0]
                HouseNameRegex = re.compile(r'(<a.*>)([\s\S]*)(</a>)')
                HouseName = re.search(HouseNameRegex, HouseName).group(2)
                # print HouseName

                # 房屋格局 三室一厅
                HousePattern = HouseInfo[1].strip()
                # print HousePattern

                # 房屋大小 91.4平米
                HouseRange= HouseInfo[2].strip()
                # print HouseRange
                # 房屋大小 91.4平米（数字格式）
                HouseRangeNumRegex = re.compile(r'[\S\s]*(?=平米)')
                HouseRangeNum = re.search(HouseRangeNumRegex, str(HouseRange))
                HouseRangeNum = float(HouseRangeNum.group())

                # 房屋朝向 东南
                HouseFace = HouseInfo[3].strip()
                # print HouseFace

                # 房屋形式 精装
                HouseStyle= HouseInfo[4].strip()
                # print HouseStyle

                IsElevator = ''
                if len(HouseInfo) > 5:
                    # 房屋是否有电梯 有电梯
                    IsElevator = HouseInfo[5].strip()
                    # print IsElevator

                # 房屋位置
                parLocation = re.compile(r'(?<=<div class="positionInfo">)[\S\s]*?(?=</div>)')
                parLocation = re.search(parLocation, item)
                parLocation = parLocation.group().strip()
                # 房屋地址
                positionRegex = re.compile(r'(?<=</span>)[\S\s]*(?=\-)')
                HousePosition = re.search(positionRegex, parLocation).group().strip()
                # print HousePosition
                # 房屋区域
                areaRegex = re.compile(r'(<a.*>)([\s\S]*)(</a>)')
                HouseArea = re.search(areaRegex, parLocation).group(2).strip()
                # print HouseArea

                # 房屋关注次数 / 带看次数 / 发布天数
                parLike = re.compile(r'(?<=<div class="followInfo">)[\S\s]*?(?=</div>)')
                parLike = re.search(parLike, item)
                parLike = parLike.group()
                parLike1 = re.compile(r'(?<=</span>)[\S\s]*')
                parLike1 = re.search(parLike1, parLike)
                parLike1 = parLike1.group()
                LikeInfo = re.split(r'\/', parLike1)
                # 房屋关注次数
                HouseLike = LikeInfo[0].strip()
                # 房屋关注次数（数字格式）
                HouseLikeNumRegex = re.compile(r'[\S\s]*(?=人关注)')
                HouseLikeNum = re.search(HouseLikeNumRegex,str(HouseLike))
                HouseLikeNum = int(HouseLikeNum.group())
                # print HouseLike
                # 房屋带看次数
                HouseLook = LikeInfo[1].strip()
                # 房屋带看次数（数字格式）
                HouseLookNumRegex = re.compile(r'(?<=共)[\S\s]*(?=次带看)')
                HouseLookNum = re.search(HouseLookNumRegex, str(HouseLook))
                HouseLookNum = int(HouseLookNum.group())
                # print HouseLook
                # 房屋发布天数
                HouseReleaseDate = LikeInfo[2].strip()

                # 房屋交通 / 免税情况（满五唯一） / 看房情况（随时看房）
                parTag = re.compile(r'(?<=<div class="tag">)[\S\s]*?(?=</div>)')
                parTag = re.search(parTag, item)
                parTag = parTag.group()
                # 房屋交通
                trafficRegex = re.compile(r'(?<=<span class="subway">)[\S\s]*?(?=</span>)')
                traffic = re.search(trafficRegex,parTag)
                if traffic:
                    traffic = traffic.group().strip()
                    # print traffic.group()
                else:
                    traffic = ''
                    # print traffic
                # 免税情况（满五唯一）
                taxfreeRegex = re.compile(r'(?<=<span class="taxfree">)[\S\s]*?(?=</span>)')
                taxfree = re.search(taxfreeRegex, parTag)
                if taxfree:
                    taxfree = taxfree.group().strip()
                    # print taxfree.group()
                else:
                    taxfree = ''
                    # print taxfree
                # 房屋看房情况（随时看房）
                haskeyRegex = re.compile(r'(?<=<span class="haskey">)[\S\s]*?(?=</span>)')
                haskey = re.search(haskeyRegex, parTag)
                if haskey:
                    haskey = haskey.group().strip()
                    # print haskey.group()
                else:
                    haskey = ''
                    # print haskey

                # 房屋总价
                parTotalPriceRegex = re.compile(r'(?<=<div class="totalPrice">)[\S\s]*?(?=</div>)')
                parHouseTotalPrice = re.search(parTotalPriceRegex, item)
                parHouseTotalPrice = parHouseTotalPrice.group()
                totalPriceRegex = re.compile(r'(?<=<span>)[\S\s]*?(?=</span>)')
                HouseTotalPrice = re.search(totalPriceRegex, parHouseTotalPrice)
                HouseTotalPrice = HouseTotalPrice.group().strip()
                # print HouseTotalPrice
                # 房屋单价
                parPriceRegex = re.compile(r'(?<=<div class="unitPrice")[\S\s]*?(?=</div>)')
                parHousePrice = re.search(parPriceRegex, item)
                parHousePrice = parHousePrice.group()
                priceRegex = re.compile(r'(?<=data-price=")[\S\s]*?(?=\")')
                HousePrice = re.search(priceRegex, parHousePrice)
                HousePrice = HousePrice.group().strip()
                # print HousePrice

                CDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                TotalPriceUnit = '万元'
                PriceUnit = '万/平米'

                Sql = 'Insert into houseinfo(HouseTitle,HouseName,HousePattern,HouseRange,HouseFace,HouseStyle,IsElevator,' \
                      'HousePosition,HouseArea,HouseLike,HouseLook,HouseReleaseDate,traffic,taxfree,haskey,HouseTotalPrice,' \
                      'HousePrice,CDate,UpdateDate,Delflag,TotalPriceUnit,PriceUnit,HouseRangeNum,HouseLikeNum,HouseLookNum)' \
                      ' values("%s", "%s","%s","%s", "%s","%s","%s", "%s","%s","%s","%s", "%s","%s","%s", "%s","%s",' \
                      '"%s", "%s","%s","%s", "%s","%s","%s","%s","%s")' % (HouseTitle, HouseName, HousePattern,
                      HouseRange,HouseFace,HouseStyle,IsElevator,HousePosition,HouseArea,HouseLike,HouseLook,HouseReleaseDate,traffic,taxfree,
                      haskey,HouseTotalPrice,HousePrice,CDate,CDate,0,TotalPriceUnit,PriceUnit,HouseRangeNum,HouseLikeNum,HouseLookNum)

                # print Sql
                self.cuesor.execute(Sql)
                db.commit()
            return True
        except Exception,ex:
            print ex
            return False

    def Start(self):
        flag = self.loadPage(self.pageIndex)
        if flag == True:
            print '第%s页数据获取成功！' % self.pageIndex
        else:
            print '第%s页数据获取失败！' % self.pageIndex

for i in range(1,5):
    _house = House()
    _house.pageIndex = i
    _house.Start()
db.close()

# _locationTrans = LocationTrans.LocationTrans()
# Date = time.strftime('%Y-%m-%d',time.gmtime())
# _locationTrans.GetLocations(Date)