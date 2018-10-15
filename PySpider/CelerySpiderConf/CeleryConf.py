# coding:utf-8
from datetime import timedelta
from celery.schedules import crontab

BROKER_URL = 'redis://localhost:6379/1'

CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'

CELERY_TIMEZONE = 'Asia/Shanghai'

CELERY_IMPORTS = (
    # 'CelerySpiderConf.StartLianJiaSpiderJob'
    'LianJiaJob.LianJiaSpiderJob',
    'LianJiaJob.LianJiaSpiderSync'
)

CELERYBEAT_SCHEDULE = {
    'add-every-1-minute': {
         'task': 'LianJiaJob.LianJiaSpiderJob.getspiderjob',
         'schedule': timedelta(minutes=1),       # 每 1 分钟执行一次
         # 'args': (5, 8)                           # 任务函数参数
    },
    'add-every-2-minute': {
         'task': 'LianJiaJob.LianJiaSpiderSync.saveJobResult',
         'schedule': timedelta(minutes=2),       # 每 2 分钟执行一次
         # 'args': (5, 8)                           # 任务函数参数
    },
}
