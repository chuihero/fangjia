#!/usr/bin/python3
# coding=utf8

import httplib2
from bs4 import BeautifulSoup
import time
import os
from multiprocessing.pool import ThreadPool
import pymysql

MAXRETRYTIMES = 5
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

        pool = ThreadPool(10)
        res = pool.map(self.parseHouseInfo, houseUrls)

        print('end')
        print(res)

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

            title = soup.find('div',class_='title').text
            room = soup.find('div',class_='room').find('div',class_='mainInfo').text

            layer = soup.find('div',class_='room').find('div',class_='subInfo').text

            area = soup.find('div',class_='area').find('div',class_='mainInfo').text
            build = soup.find('div',class_='area').find('div',class_='subInfo').text
            communityName = soup.find('div',class_='communityName').find('a').text
            region = soup.find('div',class_='areaName').find('span',class_='info').get_text(',')

            houseId = soup.find('div',class_='houseRecord').find('span',class_='info').get_text(',').split()[0]

            return [totalPrice,unitPrice,title,room,layer,area,build,communityName,\
                    region,houseId,houseUrl]
        except:


            filename = os.path.join('error',houseUrl[-17:-5]+'.html')
            fh = open(filename,'w')
            fh.writelines(soup.prettify())
            fh.close
            print('网页{}解析错误'.format(houseUrl))



class LianjiaSql(Lianjia):
    def __init__(self,region = 'tongzhou',ip= '127.0.0.1',usr='root', psw='worship',char='utf8'):
        super(Lianjia,self).__init__(region)
        try:
            self.conn = pymysql.connect(host=ip,user=usr,password=psw,charset=char)
        except:
            print('无法连接数据库！')

        self.cur = self.conn.cursor()












if __name__ == '__main__':

    # url = 'http://bj.lianjia.com/ershoufang/rs%E9%80%9A%E5%B7%9E'
    # url = 'http://bj.lianjia.com/ershoufang/pg92rs%E9%80%9A%E5%B7%9E/'
    lianjia = Lianjia('tongzhou')
    a = lianjia.parseHouseInfo('http://bj.lianjia.com/ershoufang/101092222554.html')
    # lianjia.getAllHouseInfo()


