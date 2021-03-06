#!/usr/bin/python3
# coding=utf8

import httplib2
from bs4 import BeautifulSoup
import time,datetime
import os
from multiprocessing.pool import ThreadPool
import pymysql

MAXRETRYTIMES = 5
THREADNUM = 20
class Lianjia():


    def __init__(self,region = 'tongzhou'):
        self.url = 'http://bj.lianjia.com/ershoufang/{}/pg{}/'
        self.regions = ['dongcheng','xicheng','chaoyang','haidian','fengtai','shijingshan','tongzhou',\
                       'changping','daxing','yizhuangkaifaqu','shunyi','fangshan','mentougou','pinggu',\
                       'huairou','miyun','yanqing','yanjiao']

        assert region in self.regions, '北京无此地区!'

        self.chosenRegion = region

        # header = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) Apple    WebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36'}
        self.h = httplib2.Http()


    def getHouseUrlInPage(self,url):
        header = {\
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) Apple    WebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36'}
        resp,cont = self.h.request(url,headers=header)

        houseUrlList = []
        if resp.status == 200:
            html = cont.decode('utf8')

            soup = BeautifulSoup(html, 'html.parser')
            try:
                res = soup.find('ul',class_='listContent').find_all('a',class_='img')
            except:
                print('url {} 无房源信息'.format(url))
                return []

            for line  in res:
                houseUrlList.append(line['href'])

        return houseUrlList

    def getAllHouseUrls(self):

        houseUrls = []
        i = 1
        while True:
            print('trying parse page {}!'.format(i))
            res = self.getHouseUrlInPage(self.url.format(self.chosenRegion,i))
            if len(res ) == 0:
                break
            houseUrls.extend(res)
            i+=1

        return houseUrls

    def getAllHouseInfo(self):

        houseUrls = self.getAllHouseUrls()
        houseUrls = list(set(houseUrls))

        pool = ThreadPool(THREADNUM)
        res = pool.map(self.parseHouseInfo, houseUrls)

        #有可能页面返回错误，无法解析，得到None的结果，需把None删掉
        while(None in res):
            res.remove(None)

        return  res

    def parseHouseInfo(self,houseUrl):
        header = { \
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) Apple    WebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36'}
        h = httplib2.Http()

        for i in range(MAXRETRYTIMES-1):
            resp, cont = h.request(houseUrl, headers=header)

            if  resp.status == 200:
                break
            else:
                time.sleep(5)

        if not resp.status == 200:
            print('无法获取{}的房源信息'.format(houseUrl))

        html = cont.decode('utf8')
        soup = BeautifulSoup(html, 'html.parser')

        try:

            totalPrice = float(soup.find('div',class_='price').find('span',class_='total').text)
            unitPriceText =(soup.find('div',class_='unitPrice')).span.get_text(' ')
            unitPrice = float((unitPriceText.split())[0])

            title = ','.join((soup.find('div',class_='title').text).split())
            room = soup.find('div',class_='room').find('div',class_='mainInfo').text

            layer = soup.find('div',class_='room').find('div',class_='subInfo').text

            area = soup.find('div',class_='area').find('div',class_='mainInfo').text
            build = soup.find('div',class_='area').find('div',class_='subInfo').text
            communityName = soup.find('div',class_='communityName').find('a').text
            regiontxt = soup.find('div',class_='areaName').find('span',class_='info').get_text(',').replace(',',' ').split()
            region = regiontxt[0]
            subRegion = regiontxt[1]
            street = ','.join(regiontxt[2:])
            houseId = int(soup.find('div',class_='houseRecord').find('span',class_='info').get_text(',').split()[0])

            # return [totalPrice,unitPrice,title,room,layer,area,build,communityName,\
            #         region,houseId,houseUrl]
            return {'total':totalPrice,'unit':unitPrice,'title':title,'room':room,'layer':layer,\
                    'area':area,'build':build,'community':communityName,'region':region,\
                    'subRegion':subRegion,'street':street,'id':houseId,'url':houseUrl}
        except:


            filename = os.path.join('error',houseUrl[-17:-5]+'.html')
            fh = open(filename,'w')
            fh.writelines(soup.prettify())
            fh.close
            print('网页{} 解析错误'.format(houseUrl))

    def writeHouseInfo(self,export='json'):
        pass;



class LianjiaSql(Lianjia):
    DATABASE = 'house'
    BASICTABLENAME = 'info'
    PRICETABLENAME = 'price'
    def __init__(self,region = 'tongzhou',ip= '127.0.0.1',usr='root', psw='worship',char='utf8'):
        super(LianjiaSql,self).__init__(region)
        try:
            self.conn = pymysql.connect(host=ip,user=usr,password=psw,charset=char)
        except:
            print('无法连接数据库！')

        self.cur = self.conn.cursor()

        if not self.isDatabaseExist():
            s = 'create database {}'.format(self.DATABASE)
            self.cur.execute(s)

        s = 'use {}'.format(self.DATABASE)
        self.cur.execute(s)
        self.initTables()



    def isDatabaseExist(self):
        s = 'show databases'
        self.cur.execute(s)
        res = self.cur.fetchall()
        if (self.DATABASE,) not in res:
            return False
        else:
            return True
    def initTables(self):
        s = 'show tables'
        self.cur.execute(s)
        res = self.cur.fetchall()
        if (self.BASICTABLENAME,) not in res:
            # create basic table
            s = '''create table {} (
                                id BIGINT PRIMARY KEY NOT NULL,
                                community char(50),
                                room char(50),
                                area char(50),
                                build char(50),
                                layer char(50),
                                region char(50),
                                subRegion char(50),
                                street char(100),
                                title char(255),
                                url char(100))'''.format(self.BASICTABLENAME)
            self.cur.execute(s)

        if (self.PRICETABLENAME,) not in res:
            # create price table
            s = '''create table {}(
                                id BIGINT not null,
                                date Date not null,
                                total float,
                                unitprice float,
                                PRIMARY KEY(id,date))'''.format(self.PRICETABLENAME)
            self.cur.execute(s)

    def update(self):
        s = 'select id from {}'.format(self.BASICTABLENAME)
        self.cur.execute(s)
        houseIds = self.cur.fetchall()

        s = 'select id,date from {}'.format(self.PRICETABLENAME)
        self.cur.execute(s)
        priceItems = self.cur.fetchall()

        today = datetime.date.today()

        houseInfo = self.getAllHouseInfo()
        # houseInfo = self.parseHouseInfo('http://bj.lianjia.com/ershoufang/101092222554.html')
        # houseInfo = [houseInfo]
        for house in houseInfo:
            if (house['id'],) not in houseIds:
                self.insertHouseInfo(house)

            if (house['id'],today,) not in priceItems:
                self.insertHousePrice(house)

        self.conn.commit()
        print('database updated!')

    def insertHouseInfo(self,house):
        s = '''insert {} values({},'{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')'''.format(\
                                                                                    self.BASICTABLENAME,\
                                                                                    house['id'],\
                                                                                    house['community'],\
                                                                                    house['room'],\
                                                                                    house['area'],\
                                                                                    house['build'],\
                                                                                    house['layer'],\
                                                                                    house['region'], \
                                                                                    house['subRegion'],\
                                                                                    house['street'],\
                                                                                    house['title'], \
                                                                                    house['url'])
        self.cur.execute(s)


    def insertHousePrice(self,house):
        today = datetime.date.today().strftime('%Y-%m-%d')
        s = '''insert {} values({},'{}',{},{})'''.format(self.PRICETABLENAME,\
                                                         house['id'], \
                                                         today,\
                                                         house['total'], \
                                                         house['unit'])

        self.cur.execute(s)















if __name__ == '__main__':

    # url = 'http://bj.lianjia.com/ershoufang/rs%E9%80%9A%E5%B7%9E'
    # url = 'http://bj.lianjia.com/ershoufang/pg92rs%E9%80%9A%E5%B7%9E/'
    # lianjia = Lianjia('tongzhou')
    # a = lianjia.parseHouseInfo('http://bj.lianjia.com/ershoufang/101092222554.html')
    # # lianjia.getAllHouseInfo()


    l = LianjiaSql('tongzhou')
    l.update()