# -*- coding: utf-8 -*-
import re
import urllib2
import MySQLdb
import sys
import time
from datetime import datetime
reload(sys)
sys.setdefaultencoding( "utf-8" )

db = MySQLdb.connect("localhost", "root", "sdmp", "spiderdb",charset='utf8')
class Spider:
    def __init__(self):
        # 属性列表
        self.pageIndex = 1
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.Headers = {'User-Agent':self.user_agent}
        cursor = db.cursor()
        self.cuesor = cursor

    # 获得页面代码
    def getContent(self,pageIndex):
        try:
            url = 'http://www.qiushibaike.com/text/page/' + str(pageIndex) + '/?s=4987361'
            request = urllib2.Request(url,headers=self.Headers)
            response = urllib2.urlopen(request)
            pageCode = response.read().decode('utf-8')

            if not pageCode:
                print "页面加载失败...."
                return None

            patternRegex = re.compile('<div class="article block untagged mb15"[\S\s]*?>([\S\s]*?)<div class="single-clear"></div>')
            items = re.findall(patternRegex, pageCode)
            # 遍历正则表达式匹配的信息
            for item in items:
                titleRegex = re.compile('(?<=<h2>).*(?=</h2>)')
                title = re.search(titleRegex, item)
                title = title.group()
                # print title.group()

                contentRegex = re.compile('(?<=<span>)[^<img][\s\S]*?(?=</span>)')
                content = re.search(contentRegex, item)
                content = content.group()
                # print content.group()

                tt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                Sql = 'Insert into spiderdata values("%s", "%s","%s")' % (title,content,tt)
                self.cuesor.execute(Sql)
                db.commit()
            return True
        except Exception,ex:
            print ex
            return False

    def start(self):
        flag = self.getContent(self.pageIndex)
        if flag == True:
            print '第%s页获取数据成功！' % self.pageIndex
        else:
            print '第%s页获取数据失败！' % self.pageIndex

for i in range(1,5):
    SpiderDemo = Spider()
    SpiderDemo.pageIndex = i
    SpiderDemo.start()
db.close()

