#!/usr/bin/python3
# coding=utf8

import httplib2
from bs4 import BeautifulSoup


class Lianjia():

    def __init__(self,url):
        self.entrance = url

        # header = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) Apple    WebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36'}
        self.h = httplib2.Http('.cache')

    def getPage(self):
        header = {\
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) Apple    WebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36'}
        resp,cont = self.h.request(self.entrance,headers=header)

        if resp.status == 200:
            html = cont.decode('utf8')
            fh = open('main.html','w')
            fh.writelines(html)
            fh.close()

            soup = BeautifulSoup(html, 'html.parser')

            houses = soup.find_all('li',class_='listContent')

        pass;


if __name__ == '__main__':

    url = 'http://bj.lianjia.com/ershoufang/rs%E9%80%9A%E5%B7%9E'
    lianjia = Lianjia(url)
    lianjia.getPage()
