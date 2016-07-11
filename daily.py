#! /usr/bin/python3
# coding=utf8

from lianjia import *
import datetime,time

def dailyUpdate():

    try:
        l = LianjiaSql('tongzhou')
        l.update()
        return 0
    except:
        maxTry -= 1
        return max(0,maxTry)



if __name__=='__main__':
    #处理时间定为20:00：00
    SCHEDULEHOUR = 20
    SCHEDULEMINIT = 0
    while(1):
        maxTry = 3 #执行错误最大尝试次数
        now = datetime.datetime.now()

        scheduleTime = datetime.datetime(now.year,now.month,now.day,\
                                         SCHEDULEHOUR,SCHEDULEMINIT,0)

        nextSchedule = scheduleTime + datetime.timedelta(1)

        if now > scheduleTime:
            secondNeed = nextSchedule - now
        else:
            secondNeed = scheduleTime - now

        print ('等待下次执行时间：%s秒'%secondNeed.seconds)
        time.sleep(secondNeed.seconds)

        while(dailyUpdate()):
            print('更新失败，再次尝试更新, 剩余尝试次数：%s'%maxTry)

        #数据库更新成功，或者最大次数后仍失败，等待明天更新



