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

db = MySQLdb.connect("localhost", "root", "sdmp", "spiderdb",charset="utf8mb4")

class douban_FilmReviews:
    def __init__(self):
        self.BaseUrl = 'https://movie.douban.com'
        self.BaseAjaxUrl = 'https://movie.douban.com/j/review/'
        self.PageNum = 1
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = { 'User-Agent':self.user_agent }
        cursor = db.cursor()
        self.cursor = cursor

    # 获取电影评论
    def GetFilmReviews(self):
        try:
            Date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            self.cursor.callproc("GetFilmList",[str(Date)])

            FilmUrls = []
            DoubanFilmIds = []
            # 遍历获取电影BaseURL
            for row in self.cursor.fetchall():
                FilmUrls.append(row[0])
                DoubanFilmIds.append(row[1])

            self.cursor.close()

            # 通过URL获取影评
            for i in range(0,len(FilmUrls)):
                for j in range(0,5):
                    FilmUrl = FilmUrls[i] + 'reviews?start=' + str(j*20)

                    request = urllib2.Request(FilmUrl, headers=self.headers)
                    try:
                        response = urllib2.urlopen(request)
                    except Exception,ex:
                        continue
                    pageCode = response.read().decode('utf-8')

                    if not pageCode:
                        print "页面加载失败...."
                        return None

                    # 获取电影影评
                    MoviesReviewsRegex = re.compile(r'<div class="main review-item"[\s\S]*?<div class="main-bd">[\s\S]*?</div>[\s\S]*?<div id="review[\s\S]*?</div>')
                    MoviesReviews = re.findall(MoviesReviewsRegex, pageCode)

                    for Review in MoviesReviews:
                        # 获取电影影评ID
                        ReviewIdRegex = re.compile(r'(?<=<div class="main review-item" id=")[\S\s]*?(?=">)')
                        ReviewId = re.search(ReviewIdRegex, Review).group()

                        # 获取电影影评名称
                        ReviewTitleRegex = re.compile(r'(?<=class="title-link">)[\S\s]*?(?=</a>)')
                        ReviewTitle = re.search(ReviewTitleRegex, Review).group()

                        # 获取电影影评链接
                        ReviewLinkRegex = re.compile(r'(?<=<a href=")[\s\S]*?(?=" class="title-link")')
                        ReviewLink = re.search(ReviewLinkRegex, Review).group()

                        # 获取电影影评作者头像链接
                        ReviewAuthorAvatarRegex = re.compile(r'(?<=<img width="48" height="48" src=")[\S\s]*?(?="></a>)')
                        ReviewAuthorAvatar = re.search(ReviewAuthorAvatarRegex, Review).group()

                        # 获取电影影评作者名称
                        ReviewAuthorNameRegex = re.compile(r'(?<=<span property="v:reviewer">)[\S\s]*?(?=</span>)')
                        ReviewAuthorName = re.search(ReviewAuthorNameRegex, Review).group()

                        # 获取电影影评评分
                        ReviewScoresRegex = re.compile(r'<span property="v:rating" class="allstar[\S\s]*?</span>')
                        ReviewScores = re.search(ReviewScoresRegex, Review)

                        if not ReviewScores:
                            ReviewScore = ''
                            ReviewScoreName = ''

                        else:
                            ReviewScores = re.search(ReviewScoresRegex, Review).group()
                            ReviewScoreRegex = re.compile(r'(?<=class="allstar)[\s\S]*?(?= main-title-rating")')
                            ReviewScore = re.search(ReviewScoreRegex, ReviewScores).group()
                            ReviewScoreNameRegex = re.compile(r'(?<=main-title-rating" title=")[\s\S]*?(?="></span>)')
                            ReviewScoreName = re.search(ReviewScoreNameRegex, ReviewScores).group()

                        # 获取电影影评日期
                        ReviewDateRegex = re.compile(r'(?<=class="main-meta">)[\s\S]*?(?=</span>)')
                        ReviewDate = re.search(ReviewDateRegex, Review).group()

                        # 获取电影影评内容
                        ReviewContentsRegex = re.compile(r'(?<=<div class="short-content">)[\s\S]*?(?=</div>)')
                        ReviewContents = re.search(ReviewContentsRegex, Review).group()

                        # 判断该影评是否能够访问 不能显示 则通过Ajax获取
                        ReviewContentTipRegex = re.compile(r'(?<=<p class="main-title-tip">)[\s\S]*?(?=</p>)')
                        ReviewContentTip = re.search(ReviewContentTipRegex, ReviewContents)

                        if not ReviewContentTip:
                            # 判断该影评回应数目
                            ReviewContentReturnsRegex = re.compile(r'<a class="pl" [\s\S]*?</a>')
                            ReviewContentReturns = re.search(ReviewContentReturnsRegex, ReviewContents)

                            # 判断该影评是否有影评回复
                            if not ReviewContentReturns:
                                ReviewContentRegex = re.compile(r'[\s\S]*?(?=<div class="more-info pl clearfix">)')
                                ReviewContent = re.search(ReviewContentRegex, ReviewContents).group()

                                ReviewContentReturn = int('0')
                            else:
                                ReviewContentRegex = re.compile(r'[\s\S]*?(?=<a class="pl")')
                                ReviewContent = re.search(ReviewContentRegex, ReviewContents).group()

                                # 获取电影影评反应数量
                                ReviewContentReturnRegex = re.compile(r'(?<=#comments">\()[\s\S]*?(?=回应\)</a>)')
                                ReviewContentReturn= int(re.search(ReviewContentReturnRegex, str(ReviewContents)).group())

                        else:
                            AjaxUrl = self.BaseAjaxUrl + ReviewId + '/full'
                            request = urllib2.Request(AjaxUrl, headers=self.headers)
                            response = urllib2.urlopen(request)
                            pageCode = response.read().decode('utf-8')

                            if not pageCode:
                                print "页面加载失败...."
                                return None

                            AjaxFilmReviewList = json.loads(pageCode)
                            ReviewContent = AjaxFilmReviewList['html']
                            ReviewContentReturn = int('0')

                        # 当前时间
                        CDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        Sql = 'Insert into douban_filmreview(DoubanFilmId,ReviewTitle,ReviewLink,ReviewAuthorAvatar,ReviewAuthorName,' \
                              'ReviewScore,ReviewDate,ReviewContent,ReviewReturn,CDate,ReviewScoreName,DoubanFilmReviewId) values("%s","%s","%s","%s","%s"' \
                              ',"%s","%s","%s","%s","%s","%s","%s")' % (
                                DoubanFilmIds[i], ReviewTitle, ReviewLink, ReviewAuthorAvatar, self.DeleteEmoji(ReviewAuthorName), ReviewScore,
                                ReviewDate, self.DeleteEmoji(ReviewContent.strip().replace("\"","'")), ReviewContentReturn,CDate,ReviewScoreName,ReviewId)
                        try:
                            commitCursor = db.cursor()
                            commitCursor.execute(Sql)
                            db.commit()
                        except Exception,ex:
                            continue

        except Exception,ex:
            print ex

    def DeleteEmoji(self,text):
        try:
            emoji_pattern = re.compile(
                u"(\ud83d[\ude00-\ude4f])|"  # emoticons
                u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
                u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
                u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
                u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
                "+", flags=re.UNICODE)

            return emoji_pattern.sub(r'', text)
        except Exception,ex:
            return ''

_douban_FilmFilmReviews = douban_FilmReviews()
_douban_FilmFilmReviews.GetFilmReviews()