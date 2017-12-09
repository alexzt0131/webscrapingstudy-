import urllib.request



def download_page(url, user_agent='wswp',retries=2):
    '''
    简单的下载页面示例
    python2的urllib2 在python3中改为了urllib.requests
    :param url:
    :param retries: 重试次数，作为递归的依据
    :param user_agent: 自定义用户代理，某些网站不能用python默认代理
    :return:
    '''
    urllib
    print('downloading:%s'%(url))
    html = None
    headers = {'User-agent': user_agent}
    request = urllib.request.Request(url=url, headers=headers)#可以建立一个request传入rulopen
    try:
        html = urllib.request.urlopen(request).read().decode('utf8')

    except Exception as e:
    # except urllib.request.URLError as e:
        print("Down error %s"%(str(e)))

        if retries > 0:
            if hasattr(e, 'code') and 500 <= e.code <600:
                #__dict__中有code属性并且是5XX的只在服务器错误的情况下重试
                return download_page(url=url, retries=retries-1)#递归方法重试




    return html


if __name__ == '__main__':
    # url = 'http://httpstat.us/500'
    url = 'http://www.meetup.com/'
    html = download_page(url)
    print(html)


    # print(html)

    # with open('/home/alex/test.html', 'w+') as file:
    #     file.write(html)
    #------------------------------------------------------------

