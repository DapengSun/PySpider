# coding:utf -8

import time
from celery import Celery
from CelerySpiderConf import app

@app.task
def add(x,y):
    time.sleep(5)
    return x + y