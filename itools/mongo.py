from datetime import timedelta, datetime

import zlib

import pickle
from bson import Binary
from pymongo import MongoClient




#*************************使用测试*****************************************
# #实例化mongoclient类 链接数据库
# client = MongoClient('localhost', 27017)
# #待存入的数据
# url = 'http://example.webscraping.com/view/United-Kingdom-239'
# html = '...132'
# #创建数据表（文档）
# db = client.cache
# #插入数据
# db.webpage.insert({'url': url, 'html': html})
# #查找一个数据
# print(db.webpage.find_one({'url': url}))
#
# #下面语法的意思是在该记录由更新的时候才进行更新，没有更新创建。
# #_id设为url不知道什么意思
# # $set 定义html有更新的时候才会update 需要加上upsert=True参数
# db.webpage.update({'_id': url}, {'$set': {'html': html}}, upsert=True)
#
# print(db.webpage.find_one({'_id': url}))
#************************************************************************


class MongoCache:

    def __init__(self, client=None, expires=timedelta(days=30)):

        self.client = MongoClient('localhost', 27017) if client is None else client

        self.db = self.client.cache
        #将这个index加到mongodb cache库中的system.indexes中（用expires传进来的timedelta时间来做对比参数）mongo是UTC时间
        #先理解为 过了设定的时间mongodb就会自己删除过期条目
        #要注意在链接爬虫更换种子地址的时候这里会报错
        self.db.webpage.create_index('timestap', expireAfterSeconds=expires.total_seconds())


    #pickle.load 与 dump是相反作用的两个函数，在配合zlib成对使用的时候要注意先后顺序


    def __getitem__(self, url):
        record =self.db.webpage.find_one({'_id': url})

        if record:
            return pickle.loads(zlib.decompress(record['result']))
        else:
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        #mongo是UTC时间
        record = {'result': Binary(zlib.compress(pickle.dumps(result))),
                  'timestap': datetime.utcnow()}

        self.db.webpage.update({'_id': url}, {'$set': record}, upsert=True)





if __name__ == '__main__':
    print(timedelta())
    url = 'http://test.com/'
    #expries设置为0:00:00与MongoCache中__init__()中的过期时间对比
    #如果超过时间
    cache = MongoCache(expires=timedelta())
    result = {'html': '....'}
    import time
    # cache[url] = result
    # # time.sleep(60)
    # print(cache[url])

    a = Binary(zlib.compress(pickle.dumps(result)))
    b = pickle.loads(zlib.decompress(a))
    print(b)