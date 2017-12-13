import csv
import re
import urllib.request
# from itertools import count
import itertools
from urllib import robotparser
from urllib.parse import urljoin, urlparse, urldefrag

import lxml.html
import os
import requests
import subprocess


# def download_page(url, user_agent='wswp',retries=2):
#     '''
#     简单的下载页面示例
#     python2的urllib2 在python3中改为了urllib.requests
#     :param url:
#     :param retries: 重试次数，作为递归的依据
#     :param user_agent: 自定义用户代理，某些网站不能用python默认代理
#     :return:
#     '''
#     print('downloading:%s'%(url))
#     html = None
#     headers = {'User-agent': user_agent}
#     request = urllib.request.Request(url=url, headers=headers)#可以建立一个request传入rulopen
#     try:
#         html = urllib.request.urlopen(request).read().decode('utf8')
#
#     except Exception as e:
#     # except urllib.request.URLError as e:
#         print("Down error %s"%(str(e)))
#
#         if retries > 0:
#             if hasattr(e, 'code') and 500 <= e.code <600:
#                 #__dict__中有code属性并且是5XX的只在服务器错误的情况下重试
#                 return download_page(url=url, retries=retries-1)#递归方法重试
#
#
#
#
#     return html
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError

from itools import commtools




class ScrapeCallback:
    '''
    此类用来作为链接爬虫的回调函数
    发生时间取决于调用时间
    本次例子中发生在网页下载完成
    '''
    def __init__(self):
        self.writer = csv.writer(open('/home/alex/testcsv.csv', 'w'))#初始化时 实例化一个csv.writer
        self.fields = (
            'area',
            'population',
            'iso',
            'country',
            'capital',
            'continent',
            'tld',
            'currency_code',
            'currency_name',
            'phone',
            'postal_code_format',
            'postal_code_regex',
            'languages',
            'neighbours',
        )
        self.writer.writerow(self.fields)

    def __call__(self, url, html):#函数内对象被作为函数调用的情况下__call__函数就会被调用scrap_callback(url, html)与scrap_callback.__call__(url, html)相同
        if re.search('/view/', html):#判断
            tree = lxml.html.fromstring(html)
            row = []
            for field in self.fields:
                result = tree.cssselect('tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content()
                print('{}: {}'.format(field, result))
                row.append(result)
            print('-' * 88)
            self.writer.writerow(row)



def download_page(url, user_agent='wswp', proxies=None, retries=2):
    '''
    简单的下载页面示例
    新版用requests模块来获取页面
    python2的urllib2 在python3中改为了urllib.requests
    :param url:
    :param retries: 重试次数，作为递归的依据
    :param user_agent: 自定义用户代理，某些网站不能用python默认代理
    :param proxy: 代理地址
    :return:
    '''
    print('downloading:%s'%(url))
    print('retries left: %s' % retries)
    html = None
    headers = {'User-agent': user_agent}
    # request = urllib.request.Request(url=url, headers=headers)#可以建立一个request传入rulopen

    from requests.exceptions import ProxyError
    try:
        # html = urllib.request.urlopen(request).read().decode('utf8')#urllib方法获得，ip代理麻烦
        html = requests.get(url=url, proxies=proxies, headers=headers).text#新版用requests模块来获取页面

    except requests.ConnectionError as e:

        print("Down error %s"%(str(e)))
        # print(e.__dir__())
        # print(e.__class__)
        # print(e.errno)

        if retries > 0:
            # if hasattr(e, 'code') and 500 <= e.code <600:
                #__dict__中有code属性并且是5XX的只在服务器错误的情况下重试
                # return download_page(url=url, proxys=proxys, retries=retries-1)#递归方法重试
            #*****在这里加一个测试代理ip是否可用的函数来确定是否更换proxys变量*****
            return download_page(url=url, proxies=proxies, retries=retries-1)#递归方法重试





    return html

def crawl_sitemap(rul):
    '''
    下载网站sitemap文件通过re解析链接并下载所有链接
    示例网站已修改 并无<loc>
    :param rul:
    :return:
    '''
    #下载sitemap文件
    sitemap = download_page(url)

    links = re.findall('http', sitemap)
    print(links)
    for link in links:
        print('link:%s'%(link))
        # html = download_page(link)

def get_available_page(path=''):
    '''
    根据网址后面缀的id来批量判断可用已继续操作
    加入错误次数判断，到达避免一次请求错误就退出程序的情况发生
    :param path:
    :return:
    '''
    import itertools
    max_errors = 5#请求页面允许的错误数

    num_errors = 0#错误判断的依据


    path = 'http://example.webscraping.com/places/default/index/'
    for page in itertools.count(1):#迭代器 从1开始
        url = path + str(page)
        html = download_page(url)#下载该url
        if html is None:#如果html不为空就就做相应操作
            num_errors += 1
            if num_errors == max_errors:#如果错误数达到上限，break
                break
        else:
            num_errors = 0
            print('this page can scrape:%s' % url)


def get_links(html):
    '''
    返回html中的a标签的所有链接
    :param html:
    :return:
    '''
    #r'<a[^>]+href=["\'](.*?)["\']' 可以找到a链接的正则
    webpage_regex = re.compile(r'<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)
    pass


# def link_crawler(seed_url, link_regex):
#     '''
#     下载种子页面中的所有链接
#     :param seed_url:
#     :param link_regex:
#     :return:
#     '''
#     crawl_queue = [seed_url]#队列中先投入种子地址，类似于www.b来aidu.com
#
#     seen = set(crawl_queue)#已下载的链接加入此集合，来判断链接是否重复。
#     while crawl_queue:#while true 死循环
#         # print(crawl_queue)
#         url = crawl_queue.pop()# 从crawl_queue 出栈一个元素来判断是否列表中已空
#         #----暂不启用----
#         # if not is_user_agent_available():#如果网站robots.txt文件中不允许useragent爬取数据就退出程序并提示
#         #     print('根据该网站robots.txt文件，此user_agent不允许搜索数据。')
#         #     break
#
#         html = download_page(url)#下载该url链接
#         for link in get_links(html):#循环get_links中返回的所有a标签的链接
#             # print('link is : %s' %link)
#             if re.match(link_regex, link):#按照link_crawler 参数link_regex 的正则来判断那个link合法
#                 link = urljoin(seed_url, link)#用urljoin函数来将link改为绝对路径，如果不加的话会造成用相对链接的错误
#                 if link not in seen:#不在重复列集合里的话就添加
#                     seen.add(link)
#                     crawl_queue.append(link)

#该函数待测试
def link_crawler(seed_url, link_regex, delay=2, headers=None, user_agent='wswp', max_depth=-1, max_urls=-1, scrape_callback=None):
    '''
    下载种子页面中的所有链接(跟踪链接的方式)
    :param seed_url:
    :param link_regex:
    :param delay:
    :param headers:
    :param user_agent:
    :param max_depth: 爬取深度负数表示无限制
    :param max_urls: 用来限制总下载数，负数表示无限制
    :return:
    '''
    crawl_queue = [seed_url]#队列中先投入种子地址，类似于www.b来aidu.com
    seen = {seed_url: 0}#把种子地址和深度填入
    num_urls = 0 #记录下载了多少url

    throttle = commtools.Throttle(delay)

    headers = headers or {}
    if user_agent:
        headers['User-agent'] = user_agent
    errlogs = []

    while crawl_queue:#while true 死循环
        # print(crawl_queue)
        url = crawl_queue.pop()# 从crawl_queue 出栈一个元素来判断是否列表中已空
        #----暂不启用----
        # if not is_user_agent_available():#如果网站robots.txt文件中不允许useragent爬取数据就退出程序并提示
        #     print('根据该网站robots.txt文件，此user_agent不允许搜索数据。')
        #     break
        # if is_user_agent_available(url=url, user_agent=user_agent):#暂不启用该功能
        throttle.wait(url)#按照延迟等待下一次下载
        html = download_page(url)#下载该url链接

        links = []
        if scrape_callback:#网页下载完成查看是否传入回调类，如果有就扩展到links中。（不明白没有返回值的类为什么能扩展到links中）
            #只需要对scrape_callback类定制就可以下载别的网页了。
            try:
                links.extend(scrape_callback(url, html) or [])
            except Exception as e:
                errlog = 'url={}   errmsg={}'.format(url, str(e))
                errlogs.append(errlog)
                print(errlog)
        depth = seen[url]#取该url的深度
        if depth != max_depth:

            if link_regex:
                # 过滤符合正则的链接扩展到links中
                links.extend(link for link in get_links(html) if re.match(link_regex, link))

            for link in links:
                link = normalize(seed_url, link)#将链接于seed_url拼接在一起
                # check whether already crawled this link
                if link not in seen:#可以通过 关键词 in dict 来查找是否包含此关键此的元素
                    seen[link] = depth + 1
                    # check link is within same domain
                    if same_domain(seed_url, link):
                        # success! add this new link to queue
                        crawl_queue.append(link)
                        # check whether have reached downloaded maximum
                        num_urls += 1

        if num_urls == max_urls:
            break

            #
            # for link in get_links(html):#循环get_links中返回的所有a标签的链接
            #     # print('link is : %s' %link)
            #     if re.match(link_regex, link):#按照link_crawler 参数link_regex 的正则来判断那个link合法
            #         link = urljoin(seed_url, link)#用urljoin函数来将link改为绝对路径，如果不加的话会造成用相对链接的错误
            #         if link not in seen:#不在重复列集合里的话就添加
            #             seen.add(link)
            #             crawl_queue.append(link)





def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urldefrag(link)  # remove hash to avoid duplicates
    return urljoin(seed_url, link)


def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    """
    return urlparse(url1).netloc == urlparse(url2).netloc


def get_robots(url):
    """Initialize robots parser for this domain
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(urljoin(url, '/robots.txt'))
    rp.read()
    return rp






def is_user_agent_available(url=r'http://example.webscraping.com', user_agent='wswp'):
    '''
    判断该网站用此userangent是否可行
    :param robots_url:
    :param user_agent:
    :param url:
    :return:
    '''
    rp = robotparser.RobotFileParser()
    rp.set_url(urljoin(url, '/robots.txt'))
    rp.read()
    return rp.can_fetch(user_agent, url)


def bstest1():
    '''
    BeautifulSoup简单的解析过程
    :return:
    '''
    url = 'http://example.webscraping.com/places/default/view/United-Kingdom-239'
    html = download_page(url)
    #解析下载的html BeautifulSoup(html)不指定parser的情况下
    #会提示自动用最合适的parser来解析
    soup = BeautifulSoup(html)
    #依次根据attrs来过滤需要的数据
    tr = soup.find(attrs={'id': 'places_area__row'})
    td = tr.find(attrs={'class': 'w2p_fw'})
    area = td.text
    print(area)

def lxmltest1():
    #用以下3行代码来修复可能不完整的html
    url = 'http://example.webscraping.com/places/default/view/United-Kingdom-239'
    bronk_html = download_page(url)
    tree = lxml.html.fromstring(bronk_html)
    fixed_html = lxml.html.tostring(tree, pretty_print=True)
    # print(fixed_html)
    #用lxml的css选择器来抽取需要的数据
    td = tree.cssselect('tr#places_area__row > td.w2p_fw')[0]
    area = td.text_content()
    print(area)

def get_proxies(url='', cssselect=''):
    '''
    返回网站上抓到的代理地址
    :param url:
    :param cssselect:
    :return:
    '''
    # 用以下3行代码来修复可能不完整的html
    url = 'http://www.kuaidaili.com/free/intr/'
    bronk_html = download_page(url)
    tree = lxml.html.fromstring(bronk_html)
    # fixed_html = lxml.html.tostring(tree, pretty_print=True)
    # 用lxml的css选择器来抽取需要的数据
    tds = tree.cssselect('tbody > tr')
    total = len(tds)
    count = 1

    result = []
    def is_ip_available(proxies):
        headers = {'User-agent': 'alex'}
        # flag = os.system('ping -c 1 %s' % proxy_ip.split(':')[0])  # int型可用返回0,不可用256
        #subprocess.getstatusoutput 第一个参数获得状态，第二个获得输出
        print('ping testing...')
        flag = subprocess.getstatusoutput('ping -c 1 %s' % proxy_ip.split(':')[0])# 可用返回0,不可用256
        if flag[0] == 0:
            try:
                print('checking status code...')
                html = requests.get(url='http://ip.chinaz.com', proxies=proxies, headers=headers)
                if html.status_code == 200:
                    print('proxy %s---status code is %s' % (proxies, html.status_code))
                    return True
            except ProxyError as e:
                print(e)
                return None

    for td in tds:
        print('now %s/%s' %(count, total))
        ip = td[0].text
        port = td[1].text

        proxy_ip = '%s:%s' % (ip, port)
        proxies = {"http": "http://%s" % proxy_ip, "https": "http://%s" % proxy_ip, }
        if is_ip_available(proxies):
            result.append(proxy_ip)
        else:
            print('%s is invalid' % proxy_ip)
        print("-" * 88)
        count += 1

    return result



if __name__ == '__main__':
    # print(get_proxies())
    url = 'http://example.webscraping.com/places/default/view/United-Kingdom-239'
    #
    # writer = csv.writer(open('/home/alex/test.csv', 'w'))
    # writer.writerow(('123', '456'))

    link_crawler(seed_url='http://example.webscraping.com/', max_depth=3, link_regex='/places/default/(view|index)', scrape_callback=ScrapeCallback())
    # html = download_page(url)
    # tree = lxml.html.fromstring(html)
    # # print(tree.text_content())
    # a = tree.cssselect('tr#places_area__row > td.w2p_fw')
    # # print(a)
    # # print(a[0].text_content())
    # for i in a:
    #     print(i.text_content())







    # proxies = None
    # ips = [
    #     '119.130.115.226:808',
    #     '163.125.16.200:8888',
    #     '202.109.207.126:8888',
    #     '113.76.96.79:9797',
    #     '113.65.21.37:9797',
    #     '222.85.127.130:9797',
    #     '222.85.127.130:9999',
    #     '124.207.82.166:8008',
    #     '222.85.2.12:8089',
    #     '1.202.193.18:9000',
    #     '124.205.155.154:9090',
    #     '116.236.151.166:8080',
    #     '221.214.110.130:8080',
    #     '111.40.84.73:9797',
    #     '163.125.16.215:8888',
    # ]
    # result = []
    # for ip in ips:
    #     proxy_ip = ip
    #     headers = {'User-agent': 'alex'}
    #     proxies = {"http": "http://%s" % proxy_ip, "https": "http://%s" % proxy_ip, }
    #     print(proxies)
    #     flag = os.system('ping -c 1 %s' % proxy_ip.split(':')[0])  # int型可用返回0,不可用256
    #     if flag == 0:
    #         print('%s passed ping.' % proxy_ip.split(':')[0])
    #
    #         # html = download_page(url='http://www.baidu.com', proxies=proxies)
    #         try:
    #             html = requests.get(url='http://ip.chinaz.com', proxies=proxies, headers=headers)
    #             print(html.status_code)
    #             result.append(ip)
    #         except ProxyError as e:
    #             print('%s can not be proxy.' % proxy_ip)
    #
    #
    # print(result)







    # proxies = {"http": "http://218.4.199.94:3128", "https": "http://218.4.199.94:3128", }
    # url = 'http://ip.chinaz.com'
    # url = 'http://www.asdfas.com/asdfjke.html'
    # print(download_page(url=url, proxies=proxies))
    # html = requests.get(url=url, proxies=proxies).text
    # print(html)


    # print(soup.text)



    # urllib.request.urlparse(url).netloc获得请求的域名
    #根据访问domain的时间判断延时用的类
    # throttle = commtools.Throttle(2)
    # url = 'http://www.baidu.com'
    #
    # for i in range(1, 4):
    #     throttle.wait(url=url)
    #     download_page(url=url)

    # url = 'http://httpstat.us/500'
    # url = 'http://www.meetup.com/'
    # url = 'http://example.webscraping.com/sitemap.xml'
    # crawl_sitemap(url)
    # html = download_page(url)
    # print(html)
    # get_available_page()
    # print(html)
    # link_crawler('http://example.webscraping.com', '/(index|view)')
    # link_crawler('http://example.webscraping.com', '/places/default/(index|view)')
    # with open('/home/alex/test.html', 'w+') as file:
    # a = download_page('http://example.webscraping.com')
    # print(get_links(a))
    #     file.write(html)
    #------------------------------------------------------------
    # a = re.compile(r'<a[^>]+href=["\'](.*?)["\']')
    # str1 = "var ajax_error_500 = 'An error occured, please <a href=\"places/default/index\">reload</a> the page'"
    # print(a.findall("asdd <a href='test/test.html'></a>  sdfasdf"))
    # print(a.findall(str1))
