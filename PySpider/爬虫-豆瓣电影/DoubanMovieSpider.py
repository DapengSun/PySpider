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

class douban_Film:
    def __init__(self):
        self.BaseUrl = 'https://movie.douban.com'
        self.BaseAjaxUrl = 'https://movie.douban.com/j/chart/top_list?'
        self.StartNum = 0
        self.LimitNum = 300
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = { 'User-Agent':self.user_agent }
        cursor = db.cursor()
        self.cuesor = cursor

    # 热门电影
    def GetHotFilm(self):
        try:
            MovieUrl = self.BaseUrl
            request = urllib2.Request(MovieUrl,headers=self.headers)
            response = urllib2.urlopen(request)
            pageCode = response.read().decode('utf-8')

            if not pageCode:
                print "页面加载失败...."
                return None

        except Exception,ex:
            print ex

    # 获取电影排行榜
    def GetTopRankFilm(self):
        try:
            MoviesType = self.GetTopRankTypeFilm()
            for TypeItem in MoviesType:
                # 获取电影分类名称
                MoviesTypeNameRegex = re.compile(r'(?<=">)[\s\S]*?(?=</a>)')
                MoviesTypeName = re.search(MoviesTypeNameRegex,TypeItem).group()

                # 获取电影分类URL
                MoviesTypeUrlRegex = re.compile(r'(?<=<a href=")[\s\S]*?(?=">)')
                MoviesTypeUrl = re.search(MoviesTypeUrlRegex,TypeItem).group()

                # 获取电影分类Ajax获取数据URL
                MoviesTypeAjaxUrlRegex = re.compile(r'(?<=&)[\S\s]*?(?=">)')
                MoviesTypeAjaxUrl = re.search(MoviesTypeAjaxUrlRegex, TypeItem).group()

                # 获取电影分类ID
                MoviesTypeNumRegex = re.compile(r'(?<=type=)[\s\S]*?(?=&)')
                MoviesTypeNum = re.search(MoviesTypeNumRegex,TypeItem).group()

                start = time.time()
                print '豆瓣%s类型电影排行开始抓取！' % (MoviesTypeName)
                self.GetTopRankFilmList(MoviesTypeName,MoviesTypeUrl,MoviesTypeNum,str(MoviesTypeAjaxUrl))
                end = time.time()
                print '豆瓣%s类型电影排行抓取完成！' % (MoviesTypeName)
                print '耗时%.2fs！' % (end-start)
        except Exception,ex:
            print ex

    # 获取电影排行榜类型
    def GetTopRankTypeFilm(self):
        try:
            TopRankMovieUrl = self.BaseUrl + '/chart'
            request = urllib2.Request(TopRankMovieUrl, headers=self.headers)
            response = urllib2.urlopen(request)
            pageCode = response.read().decode('utf-8')

            if not pageCode:
                print "页面加载失败...."
                return None

            # 获取电影分类Div
            MoviesTypesDivRegex = re.compile(r'(?<=<div class="types">)[\S\s]*?(?=</div>)')
            MoviesTypes = re.search(MoviesTypesDivRegex,pageCode).group()

            # 获取电影分类
            MoviesTypeRegex = re.compile(r'(?<=<span>)[\s\S]*?(?=</span>)')
            MoviesType = re.findall(MoviesTypeRegex,MoviesTypes)

            return MoviesType
        except Exception, ex:
            print ex

    # 获取电影排行榜电影清单
    def GetTopRankFilmList(self,MoviesTypeName,MoviesTypeUrl,MoviesTypeNum,MoviesTypeAjaxUrl):
        try:
            MovieFilmListUrl = self.BaseAjaxUrl + MoviesTypeAjaxUrl + "&start=" + str(self.StartNum) + "&limit=" + str(self.LimitNum)
            request = urllib2.Request(MovieFilmListUrl, headers=self.headers)
            response = urllib2.urlopen(request)
            pageCode = response.read().decode('utf-8')

            if not pageCode:
                print "页面加载失败...."
                return None

            AjaxFilmList = json.loads(pageCode)
            for Film in AjaxFilmList:
                FilmTitle = Film['title']
                FilmType = MoviesTypeName
                FilmRank = Film['rank']
                FilmUrl = Film['url']
                FilmActors = ';'.join(Film['actors'])
                FilmTags = ';'.join(Film['types'])
                FilmYears = Film['release_date']
                FilmRegions = ';'.join(Film['regions'])
                FilmScore = Film['score']
                FilmVoteCount = Film['vote_count']
                FilmCoverUrl = Film['cover_url']
                FilmPlayable = Film['is_playable']
                if FilmPlayable:
                    FilmPlayable = 0
                else:
                    FilmPlayable = 1
                DoubanFilmId = Film['id']

                # 当前时间
                CDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                Sql = 'Insert into douban_toprankfilm(FilmTitle,FilmType,FilmRankNum,FilmInfoUrl,FilmActor,FilmMisc,' \
                      'FilmYear,FilmRegion,FilmRateNum,FilmCommentNum,FilmPlayable,FilmCover,CDate,DoubanFilmId) values("%s","%s","%s","%s","%s","%s"' \
                      ',"%s","%s","%s","%s","%s","%s","%s","%s")' % (
                        FilmTitle, FilmType, FilmRank, FilmUrl, FilmActors, FilmTags,
                        FilmYears,FilmRegions, FilmScore, FilmVoteCount,FilmPlayable,FilmCoverUrl,CDate,DoubanFilmId)
                self.cuesor.execute(Sql)
                db.commit()

        except Exception, ex:
            print ex

_douban_Film = douban_Film()
_douban_Film.GetTopRankFilm()