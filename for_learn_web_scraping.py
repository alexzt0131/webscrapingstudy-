import re
import urllib.request
# from itertools import count
import itertools
from urllib import robotparser
from urllib.parse import urljoin, urlparse, urldefrag
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
from itools import commtools


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
def link_crawler(seed_url, link_regex, delay=2, headers=None, user_agent='wswp', max_depth=1, max_urls=-1):
    '''
    下载种子页面中的所有链接
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

    while crawl_queue:#while true 死循环
        # print(crawl_queue)
        url = crawl_queue.pop()# 从crawl_queue 出栈一个元素来判断是否列表中已空
        #----暂不启用----
        # if not is_user_agent_available():#如果网站robots.txt文件中不允许useragent爬取数据就退出程序并提示
        #     print('根据该网站robots.txt文件，此user_agent不允许搜索数据。')
        #     break
        # if is_user_agent_available(url=url, user_agent=user_agent):#暂不启用该功能
        throttle.wait(url)
        html = download_page(url)#下载该url链接
        links = []

        depth = seen[url]#取该url的深度
        if depth != max_depth:

            if link_regex:
                # 过滤符合正则的链接扩展到links中
                links.extend(link for link in get_links(html) if re.match(link_regex, link))

            for link in links:
                link = normalize(seed_url, link)
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


if __name__ == '__main__':
    proxies = None
    # proxies = {"http": "http://218.4.199.94:3128", "https": "http://218.4.199.94:3128", }
    # url = 'http://ip.chinaz.com'
    # url = 'http://www.asdfas.com/asdfjke.html'
    # print(download_page(url=url, proxies=proxies))
    # html = requests.get(url=url, proxies=proxies).text
    # print(html)





    # urllib.request.urlparse(url).netloc获得请求的域名
    #根据访问domain的时间判断延时用的类
    # throttle = commtools.Throttle(2)
    # url = 'http://www.baidu.com'
    #
    # for i in range(1, 4):
    #     throttle.wait(url=url)
    #     download_page(url=url)

    # url = 'http://httpstat.us/500'
    url = 'http://www.meetup.com/'
    # url = 'http://example.webscraping.com/sitemap.xml'
    # crawl_sitemap(url)
    # html = download_page(url)
    # print(html)
    # get_available_page()
    # print(html)
    # link_crawler(seed_url='http://example.webscraping.com/index', link_regex='/(index|view)')
    # link_crawler('http://example.webscraping.com', '/(index|view)')
    link_crawler('http://example.webscraping.com', '/places/default/(index|view)')
    # with open('/home/alex/test.html', 'w+') as file:
    # a = download_page('http://example.webscraping.com')
    # print(get_links(a))
    #     file.write(html)
    #------------------------------------------------------------
    # a = re.compile(r'<a[^>]+href=["\'](.*?)["\']')
    # str1 = "var ajax_error_500 = 'An error occured, please <a href=\"places/default/index\">reload</a> the page'"
    # print(a.findall("asdd <a href='test/test.html'></a>  sdfasdf"))
    # print(a.findall(str1))
