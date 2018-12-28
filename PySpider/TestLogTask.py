# -*- coding: utf-8 -*-

import celery
from CelerySpiderConf.logtask import writelog

print('start')

result = writelog.delay("123")

print('end')

print(result.get())
