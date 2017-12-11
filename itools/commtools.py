import urllib
from time import sleep
from urllib.parse import urlparse

import datetime

import itertools

from for_learn_web_scraping import download_page


class Throttle:
    # urllib.request.urlparse(url).netloc获得请求的域名

    def __init__(self, delay):
        #延迟的时间
        self.delay = delay
        #域名的字典
        self.domains = {}


    def wait(self, url):
        #获得请求网站的域名
        domain = urlparse(url).netloc
        #获取最domain最后一次访问的时间
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            #用delay 减去 两次访问的时间 如果大于0说明没有到需要等待的时间则继续等待，直到到达等待时间在记录上次访问时间
            sleep_secs = self.delay - (datetime.datetime.now() - last_accessed).seconds

            if sleep_secs > 0:
                sleep(sleep_secs)
        self.domains[domain] = datetime.datetime.now()

    # pass


if __name__ == '__main__':
    throttle= Throttle(3)
    url = 'http://www.baidu.com'


    for i in range(1, 4):
        throttle.wait(url=url)
        download_page(url=url)