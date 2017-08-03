#!/usr/bin/env python
# coding: utf-8

from pinyin import Pinyin
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

p = Pinyin()
print(p.get_pinyin(u"乌鲁木齐"))