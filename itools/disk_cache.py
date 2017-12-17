# from urllib.parse import urlsplit
#
# import re
#
# import os
#
#
# class DiskCache:
#     def __init__(self, cache_dir='cache'):
#         self.cache_dir = cache_dir
#         # self.max_length = max_length
#
#
#
#     def url_to_path(self, url):
#
#         components = urlsplit(url)
#
#         path = components.path
#
#         if not path:
#             path = '/index.html'
#         else:
#             path += 'index.html'
#
#         filename = components.netloc + path + components.query
#         print(components)
#
#         filename = re.sub(r'[^/0-9a-zA-Z\-.,;_]', '_', filename)
#         print(filename)
#         filename = '/'.join(segment[:255] for segment in filename.split('/'))
#         print(filename)
#         return os.path.join(self.cache_dir, filename)
#
# if __name__ == '__main__':
#
#     dc = DiskCache('/home/alex/cachedir/')
#     # a = dc.url_to_path(url='http://www.baidu.com/testfun/?name=alex')
#     # a = dc.url_to_path(url='http://www.acfun.cn/v/list1/index.htm')
#     a = dc.url_to_path(url='http://example.webscraping.com/places/default/view/Afghanistan-1')
#
#     print(a)