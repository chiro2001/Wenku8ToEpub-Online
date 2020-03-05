from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import getopt
import json
import base_logger
from tqdm import *
from wenku8toepub import Wenku8ToEpub, MLogger
import requests
import urllib

logger = base_logger.getLogger()

# 向服务器请求密码
logger.info('正在获取密码...')
password = '1352040930'

password_data = json.loads(requests.get('http://service-q8rodpb4-1254016670.gz.apigw.tencentcs.com/' + password).text)
if not password_data['code'] == 0:
    logger.error('密码无效！进入只读模式！')
logger.info('密码正确！')

secret_id = password_data['id']
secret_key = password_data['key']
region = 'ap-guangzhou'
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
# 2. 获取客户端对象
client = CosS3Client(config)

bucket = 'light-novel-1254016670'


str_jump = '''<head><meta http-equiv="refresh" content="5;url=%s"></head>'''


def work2(book_id: int, filename: str = None):
    wk = Wenku8ToEpub()
    if filename is None:
        filename_ = wk.id2name(book_id)
        if filename == '':
            return
        filename = "%s.epub" % filename_
    response = client.put_object(
        Bucket=bucket,
        Body=(str_jump % filename).encode('gbk'),
        # Body=(str_jump % ("https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/" + urllib.quote(filename))).encode('utf-8'),
        # Key=filename_md5,
        Key="%s.html" % (book_id, ),
        StorageClass='STANDARD',
        EnableMD5=False
    )
    logger.info("%s OK." % filename)


def work(book_id: int, filename: str = None):
    wk = Wenku8ToEpub()
    if filename is None:
        filename_ = wk.id2name(book_id)
        if filename == '':
            return
        filename = "%s.epub" % filename_
    data = wk.get_book(book_id, bin_mode=True, fetch_image=False)
    response1 = client.put_object(
        Bucket=bucket,
        Body=data,
        # Key=filename_md5,
        Key="%s" % (filename, ),
        StorageClass='STANDARD',
        EnableMD5=False
    )
    # response2 = client.put_object(
    #     Bucket=bucket,
    #     Body=(str_jump % filename).encode('gbk'),
    #     # Key=filename_md5,
    #     Key="%s.html" % (book_id, ),
    #     StorageClass='STANDARD',
    #     EnableMD5=False
    # )
    # logger.info("%s OK. %s %s" % (filename, str(response1), str(response2)))
    logger.info("%s OK. %s" % (filename, str(response1)))
    return 'https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename


def work3(book_id: int, filename: str = None):
    wk = Wenku8ToEpub()
    if filename is None:
        filename_ = wk.id2name(book_id)
        if filename == '':
            return
        filename = "%s.epub" % filename_
    data = wk.get_book(book_id, bin_mode=True, fetch_image=True)
    # response1 = client.put_object(
    #     Bucket=bucket,
    #     Body=data,
    #     # Key=filename_md5,
    #     Key="%s" % (filename, ),
    #     StorageClass='STANDARD',
    #     EnableMD5=False
    # )
    # response2 = client.put_object(
    #     Bucket=bucket,
    #     Body=(str_jump % filename).encode('gbk'),
    #     # Key=filename_md5,
    #     Key="%s.html" % (book_id, ),
    #     StorageClass='STANDARD',
    #     EnableMD5=False
    # )
    # logger.info("%s OK. %s %s" % (filename, str(response1), str(response2)))
    # return 'https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename
    logger.info("%s OK。(No Cache.)" % (filename,))
    return data


def work4(book_id: int, filename: str = None):
    wk = Wenku8ToEpub()
    if filename is None:
        filename_ = wk.id2name(book_id)
        if filename == '':
            return
        filename = "%s.epub" % filename_
    data = wk.get_book(book_id, bin_mode=True, fetch_image=True)
    response1 = client.put_object(
        Bucket=bucket,
        Body=data,
        # Key=filename_md5,
        Key="%s" % (filename, ),
        StorageClass='STANDARD',
        EnableMD5=False
    )
    response2 = client.put_object(
        Bucket=bucket,
        Body=(str_jump % filename).encode('gbk'),
        # Key=filename_md5,
        Key="%s.html" % (book_id, ),
        StorageClass='STANDARD',
        EnableMD5=False
    )
    logger.info("%s OK. %s %s" % (filename, str(response1), str(response2)))
    return 'https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename
    # logger.info("%s OK。(No Cache.)" % (filename,))
    # return data


def v2_work(book_id: int, filename: str = None, mlogger = None):
    wk = Wenku8ToEpub()
    if filename is None:
        filename_ = wk.id2name(book_id)
        if filename == '':
            return
        filename = "%s.epub" % filename_
    data = wk.get_book(book_id, bin_mode=True, fetch_image=False, mlogger=mlogger)
    response1 = client.put_object(
        Bucket=bucket,
        Body=data,
        # Key=filename_md5,
        Key="%s" % (filename, ),
        StorageClass='STANDARD',
        EnableMD5=False
    )
    logger.info("%s OK. %s" % (filename, str(response1)))
    return 'https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], '-s:-e:-b', [])
    start = 1
    end = 3000
    for name, val in opts:
        if name == '-s':
            try:
                start = int(val)
            except ValueError as e:
                logger.error(str(e))
                sys.exit()
        if name == '-e':
            try:
                end = int(val)
            except ValueError as e:
                logger.error(str(e))
                sys.exit()
        if name == '-b':
            for _book_id in trange(start, end + 1, 1):
                try:
                    work2(_book_id)
                except Exception as e:
                    logger.critical(str(e))
            sys.exit()

    for _book_id in trange(start, end + 1, 1):
        try:
            work(_book_id)
        except Exception as e:
            logger.critical(str(e))