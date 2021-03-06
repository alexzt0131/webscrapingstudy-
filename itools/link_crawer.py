import re
from urllib import robotparser
from urllib.parse import urljoin, urlparse, urldefrag

from for_learn_web_scraping import ScrapeCallback
from itools.commtools import Downloader


def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, user_agent='wswp', proxies=None,
                 num_retries=1, scrape_callback=None, cache=None):
    '''
    Crawl from the given seed URL following links matched by link_regex
    :param seed_url:种子地址
    :param link_regex:链接遍历的相关正则
    :param delay:延迟时间
    :param max_depth:最大遍历深度
    :param max_urls:
    :param user_agent:头文件
    :param proxies: 代理
    :param num_retries:重试次数
    :param scrape_callback: 传入scrape_callback类
    :param cache: 传入cache类
    :return:
    '''
    # the queue of URL's that still need to be crawled
    crawl_queue = [seed_url]
    # the URL's that have been seen and at what depth
    seen = {seed_url: 0}
    # track how many URL's have been downloaded
    num_urls = 0
    # rp = get_robots(seed_url)
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, cache=cache)
    errlogs = []
    while crawl_queue:
        url = crawl_queue.pop()
        depth = seen[url]
        # check url passes robots.txt restrictions
        # if rp.can_fetch(user_agent, url):
        html = D(url)
        links = []
        # 只需要对scrape_callback类定制就可以下载别的网页了。
        if scrape_callback:
            try:
                links.extend(scrape_callback(url, html) or [])
            except Exception as e:
                errlog = 'url={}   errmsg={}'.format(url, str(e))
                errlogs.append(errlog)
                print(errlog)
        # if scrape_callback:
        #     links.extend(scrape_callback(url, html) or [])

        if depth != max_depth:
            # can still crawl further
            if link_regex:
                # filter for links matching our regular expression
                links.extend(link for link in get_links(html) if re.match(link_regex, link))

            for link in links:
                link = normalize(seed_url, link)
                # check whether already crawled this link
                if link not in seen:
                    seen[link] = depth + 1
                    # check link is within same domain
                    if same_domain(seed_url, link):
                        # success! add this new link to queue
                        crawl_queue.append(link)

        # check whether have reached downloaded maximum
        num_urls += 1
        if num_urls == max_urls:
            break
        # else:
        #     print('Blocked by robots.txt:', url)
        #




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


# def normalize(seed_url, link):
#     """Normalize this URL by removing hash and adding domain
#     """
#     link, _ = urlparse.urldefrag(link)  # remove hash to avoid duplicates
#     return urlparse.urljoin(seed_url, link)
#
#
# def same_domain(url1, url2):
#     """Return True if both URL's belong to same domain
#     """
#     return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc
#
#
# def get_robots(url):
#     """Initialize robots parser for this domain
#     """
#     rp = robotparser.RobotFileParser()
#     rp.set_url(urlparse.urljoin(url, '/robots.txt'))
#     rp.read()
#     return rp


def get_links(html):
    '''
    返回html中的a标签的所有链接
    :param html:
    :return:
    '''
    #r'<a[^>]+href=["\'](.*?)["\']' 可以找到a链接的正则
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # list of all links from the webpage
    return webpage_regex.findall(html)


if __name__ == '__main__':


    link_crawler('http://example.webscraping.com', '/places/default/(view|index)', delay=0, num_retries=1, max_depth=2, user_agent='BadCrawler', scrape_callback=ScrapeCallback())
    # link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, max_depth=1,
    #              user_agent='GoodCrawler')

    pass
