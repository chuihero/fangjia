#! /usr/bin/python3
# coding=utf8


import json
import pandas as pd
import sys
import matplotlib.pyplot as plt
import pymysql

class FangJiaShower():
    DATABASE = 'house'
    BASICTABLENAME = 'info'
    PRICETABLENAME = 'price'

    def __init__(self,sqlConfigFile='sqlConfig.json',char='utf8'):
        try:
            with open(sqlConfigFile) as f:
                sqlConfig = json.load(f)
        except:
            print('无法载入SQL连接配置信息，请检查')

        try:
            self.conn = pymysql.connect(host=sqlConfig['host'],\
                                      user=sqlConfig['user'],\
                                      password=sqlConfig['password'],\
                                      database=self.DATABASE,\
                                      charset=char)
        except Exception as e:
            print(e)
            print('无法打开数据库连接')
            sys.exit()

        self.cur=self.conn.cursor()

    def showTotalHouse(self):

        s = 'select date,count(id) as totalHouses from {} group by date order by date'.format(self.PRICETABLENAME)

        df = pd.read_sql(s,self.conn)

        df.plot.bar()


    def showPriceTrace(self):
        s = """select i.subRegion as 地区,p.date as 日期,round(avg(p.unitPrice),2) as 单价 from info i, price p
            where i.id=p.id group by i.subRegion,p.date order by i.subRegion, p.date"""
        df  = pd.read_sql(s,self.conn)

        df = df.set_index(['地区','日期'])

        region = set(df.index.get_level_values(0))

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)


        for r in region:
            regionPrice = df.loc[r]
            ax.plot(regionPrice['单价'],label=r)

        ax.legend(loc='upper left')
        plt.show()



if __name__ == '__main__':

    my = FangJiaShower()
    # my.showTotalHouse()
    my.showPriceTrace()