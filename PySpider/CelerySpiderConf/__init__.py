# coding:utf-8

from celery import Celery

app = Celery('SpiderCelery')

app.config_from_object('CelerySpiderConf.CeleryConf')
