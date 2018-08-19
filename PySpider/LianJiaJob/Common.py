#coding : utf-8

class Common(object):
    def getResultDict(self,description,result):
        _result = [dict(zip(description,i)) for i in result]
        return _result