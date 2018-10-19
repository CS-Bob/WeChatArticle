# encoding: utf-8
'''
@author: bo

@file: OnTime.py
@time: 2018/10/13/013 10:34
@desc:
'''
import datetime
import time
from WeChatSpider import *

def do_sth():
    # 把爬虫程序放在这个类里
    print(u'It is time to Spider')
    Spider()

# 让这个函数不断执行，在特定的时间内进行爬取
def one_time_run():
    while True:
        while True:
            now = datetime.datetime.now()               #获得当前的时间
            # print(now.hour, now.minute)
            #每天的10点30分 16点30分 22点30分定时爬取
            if now.hour == 10 and now.minute == 30:
                break
            if now.hour == 16 and now.minute == 30:
                break
            if now.hour == 22 and now.minute == 30:
                break
            # 每隔60秒检测一次
            time.sleep(60)
        do_sth()
        #休息一分钟后再进行爬取
        time.sleep(60)

if __name__ == '__main__':
    one_time_run()
