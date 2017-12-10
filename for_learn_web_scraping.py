import re
import urllib.request
# from itertools import count
import itertools
from urllib import robotparser
from urllib.parse import urljoin, urlparse
import requests


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
def download_page(url, user_agent='wswp', proxys=None, retries=2):
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
    html = None
    headers = {'User-agent': user_agent}
    request = urllib.request.Request(url=url, headers=headers)#可以建立一个request传入rulopen

    opener = urllib.request.build_opener()


    try:
        # html = urllib.request.urlopen(request).read().decode('utf8')
        html = requests.get(url=url, proxies=proxies).text#新版用requests模块来获取页面

    except Exception as e:
    # except urllib.request.URLError as e:
        print("Down error %s"%(str(e)))

        if retries > 0:
            if hasattr(e, 'code') and 500 <= e.code <600:
                #__dict__中有code属性并且是5XX的只在服务器错误的情况下重试
                return download_page(url=url, proxys=proxys, retries=retries-1)#递归方法重试




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


def link_crawler(seed_url, link_regex):
    '''
    下载种子页面中的所有链接
    :param seed_url:
    :param link_regex:
    :return:
    '''
    crawl_queue = [seed_url]#队列中先投入种子地址，类似于www.b来aidu.com

    seen = set(crawl_queue)#已下载的链接加入此集合，来判断链接是否重复。
    while crawl_queue:#while true 死循环
        # print(crawl_queue)
        url = crawl_queue.pop()# 从crawl_queue 出栈一个元素来判断是否列表中已空
        #----暂不启用----
        # if not is_user_agent_available():#如果网站robots.txt文件中不允许useragent爬取数据就退出程序并提示
        #     print('根据该网站robots.txt文件，此user_agent不允许搜索数据。')
        #     break

        html = download_page(url)#下载该url链接
        for link in get_links(html):#循环get_links中返回的所有a标签的链接
            # print('link is : %s' %link)
            if re.match(link_regex, link):#按照link_crawler 参数link_regex 的正则来判断那个link合法
                link = urljoin(seed_url, link)#用urljoin函数来将link改为绝对路径，如果不加的话会造成用相对链接的错误
                if link not in seen:#不在重复列集合里的话就添加
                    seen.add(link)
                    crawl_queue.append(link)


def is_user_agent_available(robots_url=r"http://example.webscraping.com/robots.txt", user_agent='wswp', url=r'http://example.webscraping.com'):
    '''
    判断该网站用此userangent是否可行
    :param robots_url:
    :param user_agent:
    :param url:
    :return:
    '''
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch(user_agent, url)


if __name__ == '__main__':
    proxies = {"http": "http://218.4.199.94:3128", "https": "http://218.4.199.94:3128", }
    url = 'http://ip.chinaz.com/'
    print(download_page(url=url, proxys=proxies))
    # html = requests.get(url=url, proxies=proxies).text
    # print(html)







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
