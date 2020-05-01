# coding: UTF-8
import logging

import os
# import urllib2
import requests
import opds.Config as Config
import json

from opds.utils import connect_path, getFile
bookdata = {}

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


__author__ = 'lei'
__author2__ = 'Lance'


# base="/home/cocky"
class FileSystem:
    def outErr(self):
        logging.error("No Realyzed")

    def exists(self, path):
        self.outErr()
        pass

    def isfile(self, path):
        self.outErr()
        pass

    def listdir(self, path):
        self.outErr()
        return []
        pass

    def getdownloadurl(self, path, name):
        self.outErr()
        return ""


class LocalFileSystem(FileSystem):
    """
    config the #Config.base
    """

    def __init__(self):
        self.path = ''

    def exists(self, path):
        if path is None:
            path = self.path
        return os.path.exists(connect_path(Config.base, path))

    def isfile(self, path):
        if path is None:
            path = self.path
        # print('isf', connect_path(Config.base, path))
        return os.path.isfile(connect_path(Config.base, path))

    def listdir(self, path):
        if path is None:
            path = self.path
        # print('listdir', os.listdir(connect_path(Config.base, path)))
        return os.listdir(connect_path(Config.base, path))

    def getdownloadurl(self, path, name):
        # print('down url:', connect_path(connect_path(Config.SITE_BOOK_DONWLOAD, path), name))
        # 这里有问题。已经修改
        return [connect_path(connect_path(Config.SITE_BOOK_DONWLOAD, path), name), ]


class LocalMetadataFileSystem(FileSystem):
    # q = Auth(Config.access_key, Config.secret_key)

    # bucket = BucketManager(q)
    def __init__(self):
        ff = open('metadata.json', 'r')

        self.book_trees = json.load(ff)

    def exists(self, path):
        files = getFile(self.book_trees, self.getTruePaths(path))
        return files != None

    def isfile(self, path):
        if path is None:
            return False
        # ???为啥放_-_
        if path.find('_-_') == -1:
            return False
        else:
            return True

    def listdir(self, path):
        paths = self.getTruePaths(path)

        if len(paths) != 0:
            return getFile(self.book_trees, paths)
        else:
            return self.book_trees

    def getTruePaths(self, tmp):
        """
        :param tmp:
        :return:
        """
        paths = tmp.split('/')
        paths = [p for p in paths if p != '']
        return paths

    def getdownloadurl(self, path, name):
        tmp = connect_path(path, name)

        files = getFile(self.book_trees, self.getTruePaths(tmp))

        return [connect_path(Config.SITE_BOOK_DONWLOAD, connect_path(path, ee)) for ee in files]


class QiniuFileSystem(FileSystem):
    # q = Auth(Config.access_key, Config.secret_key)

    # bucket = BucketManager(q)
    def __init__(self):
        # resp=urllib2.urlopen(connect_path(Config.SITE_BOOK_DONWLOAD,'metadata.json'))
        resp = requests.get(connect_path(Config.SITE_BOOK_DONWLOAD, 'metadata.json'))
        if resp.status_code == 200:
            self.book_trees = json.loads(resp.text)

    def outErr(self):
        logging.error("No Realyzed")

    def exists(self, path):
        files = getFile(self.book_trees, self.getTruePaths(path))
        # logging.info(len(files)!=0)
        return len(files) != 0

    def isfile(self, path):
        if path.find('_-_') == -1:
            return False
        else:
            return True

    def listdir(self, path):
        paths = self.getTruePaths(path)

        if len(paths) != 0:
            return getFile(self.book_trees, paths)
        else:
            return self.book_trees

    def getTruePaths(self, tmp):
        """
        :param tmp:
        :return:
        """
        paths = tmp.split('/')
        paths = [p for p in paths if p != '']
        return paths

    def getdownloadurl(self, path, name):
        tmp = connect_path(path, name)

        files = getFile(self.book_trees, self.getTruePaths(tmp))

        return [connect_path(Config.SITE_BOOK_DONWLOAD, connect_path(path, ee)) for ee in files]


class TencentFileSystem(FileSystem):

    def __init__(self):
        # 向服务器请求密码
        logging.info('正在获取密码...')
        password = '1352040930'

        password_data = json.loads(
            requests.get('http://service-q8rodpb4-1254016670.gz.apigw.tencentcs.com/' + password).text)
        if not password_data['code'] == 0:
            logging.error('密码无效！进入只读模式！')
        logging.info('密码正确！')

        secret_id = password_data['id']
        secret_key = password_data['key']
        region = 'ap-guangzhou'
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
        # 2. 获取客户端对象
        self.client = CosS3Client(config)
        self.bucket = 'light-novel-1254016670'
        self.booklist = []
        self.bookdata = []

    def outErr(self):
        logging.error("Tencent File System Error...")

    def exists(self, path):
        # resp = self.client.list_objects(Bucket=self.bucket,
        #                                 Prefix=path,
        #                                 MaxKeys=1)
        # data = dict(resp)
        # if 'Contents' not in data:
        #     return False
        return True

    def isfile(self, path):
        if path == '/':
            return False
        # resp = self.client.list_objects(Bucket=self.bucket,
        #                                 Prefix=path,
        #                                 MaxKeys=1)
        # data = dict(resp)
        # if 'Contents' not in data:
        #     return False
        return True

    def listdir(self, path, page=4):
        if path is None or len(path) == 0:
            path = ''
        elif path[0] == '/':
            path = path[1:]
        last_marker = ''
        # page = 1.2.3.4...
        data = None
        self.booklist = []
        self.bookdata = []

        while page > 0:
            resp = self.client.list_objects(Bucket=self.bucket,
                                            Prefix=path,
                                            MaxKeys=1000,
                                            Marker=last_marker,
                                            )
            data = dict(resp)
            # print(data)
            # 最后一页
            if 'NextMarker' not in data:
                break
            last_marker = data['NextMarker']
            page -= 1

            if 'Contents' not in data:
                return self.booklist
            for book in data['Contents']:
                key, last_modified, e_tag, size = book['Key'], book['LastModified'], book['ETag'], book['Size']
                self.booklist.append(key)
                self.bookdata.append({
                    'key': key,
                    'last_modified': last_modified,
                    'e_tag': e_tag,
                    'size': size
                })

        if data is None:
            return []
        global bookdata
        bookdata = {}
        for d in self.bookdata:
            bookdata[d['key']] = d
        return self.booklist

    def getTruePaths(self, tmp):
        return ''

    def getdownloadurl(self, path, name):
        urls = []
        # for book in self.booklist:
        #     urls.append(Config.SITE_BOOK_DONWLOAD + book)
        urls.append(Config.SITE_BOOK_DONWLOAD + path + '/' + name)
        return urls


if __name__ == '__main__':
    _fs = TencentFileSystem()
    print(_fs.listdir('/'))
