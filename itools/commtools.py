import random
import socket
import urllib
from time import sleep
from urllib.parse import urlparse

import datetime

import itertools

import requests



DEFAULT_AGENT = 'wswp'
DEFAULT_DELAY = 5
DEFAULT_RETRIES = 1
DEFAULT_TIMEOUT = 60


class Downloader:
    def __init__(self, delay=DEFAULT_DELAY,
                 user_agent=DEFAULT_AGENT,
                 proxies=None,
                 num_retries=DEFAULT_RETRIES,
                 timeout=DEFAULT_TIMEOUT,
                 # opener=None,
                 cache=None):
        socket.setdefaulttimeout(timeout)
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        # self.opener = opener
        self.cache = cache
        self.headers = {'User-agent': self.user_agent}

    def __call__(self, url):
        #当类被当作函数调用的时候，会执行这个函数（参数要参照__call__的填写）
        result = None
        if self.cache:
            try:
                result = self.cache[url]
                print('{}  --  has cache'.format(url))
            except KeyError:
                # url is not available in cache
                pass
            # else:
            #     if self.num_retries > 0 and 500 <= result['code'] < 600:
            #         # server error so ignore result from cache and re-download
            #         result = None
        if result is None:
            # result was not loaded from cache so still need to download
            self.throttle.wait(url)
            proxy = random.choice(self.proxies) if self.proxies else None
            headers = {'User-agent': self.user_agent}
            result = self.download(url, headers, proxy=proxy, num_retries=self.num_retries)
            if self.cache:
                # save result to cache
                self.cache[url] = result
        return result['html']



    def download(self, url, headers=None, proxy=None, num_retries=2, data=None):
        print('downloading:%s' % (url))
        print('retries left: %s' % num_retries)
        html = ''
        headers = self.headers
        if proxy:
            #设置代理参数
            # {"http": "http://%s" % proxy_ip, "https": "http://%s" % proxy_ip, }
            proxy = random.choice(self.proxies) if self.proxies else None
            # pass
        try:

            rets = requests.get(url=url, proxies=proxy, headers=headers)  # 新版用requests模块来获取页面
            html = rets.text
            code = rets.status_code
            if num_retries > 0 and 500 <= code < 600:
                print('5xx error.....')

                # if hasattr(e, 'code') and 500 <= e.code <600:
                # __dict__中有code属性并且是5XX的只在服务器错误的情况下重试
                # return download_page(url=url, proxys=proxys, retries=retries-1)#递归方法重试
                # *****在这里加一个测试代理ip是否可用的函数来确定是否更换proxys变量*****
                return self.download(url, headers, proxy, num_retries - 1, data)  # 递归方法重试
                # return self._get(url, headers, proxy, num_retries - 1, data)  # 递归方法重试
        except Exception as e:
            print('Download error:%s' % str(e))
            code = str(e)
            # return self._get(url, headers, proxy, num_retries - 1, data)
            # html = ''
            # if hasattr(e, 'code'):
            #     code = e.code
            #     if num_retries > 0 and 500 <= code < 600:
            #         # retry 5XX HTTP errors
            #         return self._get(url, headers, proxy, num_retries - 1, data)
        else:
                code = None
        return {'html': html, 'code': code}

























































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
    #
    #
    # for i in range(1, 4):
    #     throttle.wait(url=url)
    #     download_page(url=url)