# -*- coding: utf-8 -*-
import os
import re
import shutil
import zlib
from datetime import datetime, timedelta
from urllib.parse import urlsplit

from itools.link_crawer import link_crawler

try:
    import cPickle as pickle
except ImportError:
    import pickle



class DiskCache:
    """
    磁盘缓冲有很多缺陷，比如url映射为文件名会有重复的比如query- /？a+b and /?a-b都会得到同一个文件名
    磁盘的文件数也会有限制fat32是65535个
    ext4达到1500万个，可大网站动辄就上亿页面
    改善方法是使用类似B+树的算法进行索引，我们使用已经实现这类算法的数据库来实现


    实现__getitem__和__setitem__可以让类以 类名[‘数据’]的方式来存储读取数据
    具体由实现决定
    Dictionary interface that stores cached
    values in the file system rather than in memory.
    The file path is formed from an md5 hash of the key.

    cache = DiskCache()
    url = 'http://example.webscraping.com'
    result = {'html': '...'}
    cache[url] = result
    cache[url]['html'] == result['html']
    True
    cache = DiskCache(expires=timedelta())
    cache[url] = result
    cache[url]
    Traceback (most recent call last):
     ...
    KeyError: 'http://example.webscraping.com has expired'
    cache.clear()
    """

    def __init__(self, cache_dir='cache', expires=timedelta(days=30), compress=True):
        """
        cache_dir: the root level folder for the cache
        expires: timedelta of amount of time before a cache entry is considered expired
        compress: whether to compress data in the cache
        """
        self.cache_dir = cache_dir
        self.expires = expires
        self.compress = compress

    def __getitem__(self, url):
        """Load data from disk for this URL
        """
        #将url转化为安全文件名
        path = self.url_to_path(url)
        #检测文件是否存在，否则报错
        if os.path.exists(path):
            #以rb（读取byte）打开该文件
            with open(path, 'rb') as fp:
                data = fp.read()
                #以compress变量判断是否解压缩
                if self.compress:
                    #解压缩文件
                    data = zlib.decompress(data)
                #用pickle.load将html的内容与时间戳取出 dumps与load两个函数效果相反
                result, timestamp = pickle.loads(data)
                #用时间戳来判断该缓存文件是否已经过期
                # if self.has_expired(timestamp):
                #     raise KeyError(url + ' has expired')
                #返回这个结果
                return result
        else:
            # URL has not yet been cached
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        """Save data to disk for this url
        """
        #先转化为安全文件名
        path = self.url_to_path(url)
        #定位文件夹+文件名的位置
        folder = os.path.dirname(path)
        #如果没有该文件夹则创建
        if not os.path.exists(folder):
            os.makedirs(folder)
        #pickle 会将输入转化为字符串存入磁盘中类似b'\x80\x03X\n\x00\x00\5....'
        data = pickle.dumps((result, datetime.utcnow()))
        # print(len(data))
        #根据变量compress来确定事发要进行压缩
        if self.compress:
            data = zlib.compress(data)
        # print(len(data))
        #写入文件
        with open(path, 'wb') as fp:
            fp.write(data)

    # def __delitem__(self, url):
    #     """Remove the value at this key and any empty parent sub-directories
    #     """
    #     path = self._key_path(url)
    #     try:
    #         os.remove(path)
    #         os.removedirs(os.path.dirname(path))
    #     except OSError:
    #         pass

    def url_to_path(self, url):
        """Create file system path for this URL
        """
        components = urlsplit(url)
        # when empty path set to /index.html
        path = components.path
        # print(components)
        #给path加以下的字符是为了
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'
        filename = components.netloc + path + components.query
        # replace invalid characters
        # filename = re.sub('[^/0-9a-zA-Z\-.,;_ ]', '_', filename)
        filename = re.sub('[\-,;_ /]', '_', filename)
        # restrict maximum number of characters
        filename = '/'.join(segment[:255] for segment in filename.split('/'))
        return os.path.join(self.cache_dir, filename)

    # def has_expired(self, timestamp):
    #     """Return whether this timestamp has expired
    #     """
    #     return datetime.utcnow() > timestamp + self.expires
    #
    # def clear(self):
    #     """Remove all the cached values
    #     """
    #     if os.path.exists(self.cache_dir):
    #         shutil.rmtree(self.cache_dir)


if __name__ == '__main__':
    # link_crawler('http://example.webscraping.com/', '/(index|view)', cache=DiskCache())
    url = 'http://example.webscraping.com/'
    url1 = 'http://example.webscraping.com/qwe/'
    d = DiskCache(cache_dir='/home/alex/cachedir')

    d.__setitem__(url, {'test': 'testcontents'})
    # print(d.__getitem__(url))

    # data = pickle.dumps(('testresult', datetime.utcnow()))
    # print(('testresult', datetime.utcnow()))
    # print(data)