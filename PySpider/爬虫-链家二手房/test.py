# -*- coding: utf-8 -*-

def yield_func():
    Info_list = [{'area': '北京', 'count': 1}, {'area': '上海', 'count': 2}, {'area': '天津', 'count': 3},
                 {'area': '天津', 'count': 1000}]

    area_list = []
    for i in Info_list:
        area_list.append(i['area'])
    area_index = list(set(area_list))
    # print(area_index)

    area_count = []
    for i in area_index:
        area_count.append(area_list.count(i))

    # for area,count in zip(area_index,area_count):
        # print(area,count)
        # data = {
        #     'area':area,
        #     'count':[count]
        # }

    for i in range(1,10):
        yield i

data = yield_func()

for i in data:
    print(i)
