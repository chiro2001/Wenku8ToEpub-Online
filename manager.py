from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosClientError
import sys
import getopt
import json
import base_logger
from tqdm import *
from wenku8toepub import Wenku8ToEpub, lock, MLogger, logger
import requests
import threading
import urllib
import os
import io

# logger = base_logger.getLogger()
th_results = {}

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
region2 = 'ap-chengdu'

# NO提高超时时间
# config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Timeout=120)
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
config2 = CosConfig(Region=region2, SecretId=secret_id, SecretKey=secret_key)
# 2. 获取客户端对象
# NO增大重试次数
# client = CosS3Client(config, retry=5)
client = CosS3Client(config)
client2 = CosS3Client(config2)

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


def my_upload_file(key, data):
    # 最后尝试
    data.seek(0)
    client.upload_file_from_buffer(
        Bucket=bucket,
        Body=data,
        # Key=filename_md5,
        Key=key,
        StorageClass='STANDARD',
        # PartSize=1,
        # MAXThread=10
    )


def v2_work(book_id: int, filename: str = None, mlogger=None, image=False):
    wk = Wenku8ToEpub()
    if filename is None:
        filename_ = wk.id2name(book_id)
        if filename == '':
            return
        filename = "%s.epub" % filename_
    # 设置最大图像规模为3MB
    if os.environ.get('WENKU8_LOCAL', 'False') == 'True':
        image_size = None
    else:
        image_size = 3 * 1024 * 1024
    data = wk.get_book(book_id, bin_mode=True, fetch_image=image, mlogger=mlogger, image_size=image_size)
    mlogger.info('小说获取完毕，准备上传到腾讯云...')
    try:
        if os.environ.get('WENKU8_LOCAL', 'False') == 'True':
            response1 = client.put_object(
                Bucket=bucket,
                Body=data,
                # Key=filename_md5,
                Key="%s" % (filename,),
                StorageClass='STANDARD',
                EnableMD5=False
            )
        else:
            raise CosClientError("腾讯云上传取消。")
        # 小心内存过大
    except Exception as e:
        mlogger.warn("%s 腾讯云上传错误，准备直接返回临时下载链接..." % str(e))
        # 保存到本地
        with open('static/%s' % filename, 'wb') as f:
            f.write(data)
        url = '/static/%s' % filename
        lock.acquire()
        th_results[str(book_id)] = url
        lock.release()
        # 再开个线程再次尝试上传
        # threading.Thread(target=my_upload_file, args=("%s" % (filename,), bio)).start()
        return url
    mlogger.info("%s OK. %s" % (filename, str(response1)))
    if os.environ.get('WENKU8_LOCAL', 'False') == 'True':
        with open('static/%s' % filename, 'wb') as f:
            f.write(data)
        url = '/static/%s' % filename
    else:
        url = 'https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename
    lock.acquire()
    th_results[str(book_id)] = url
    lock.release()
    return url


def v2_check_time(key):
    response = client.list_objects(
        Bucket=bucket,
        Prefix=key
    )
    if 'Contents' not in response or len(response['Contents']) == 0:
        return None
    return response['Contents'][0]['LastModified']


def make_urls():
    method = 'GET'
    # 30分钟有效
    expired = 30 * 60
    req = {
        'static-1254016670': ['wk8local.exe', 'wenku8toepub.exe', 'Wenku8下载_1.1.apk',
                                         '网易云音乐下载器_1.2.apk', '方寸之间_2.31.apk']
    }
    urls = []
    for r in req:
        for k in req[r]:
            urls.append(client2.get_presigned_download_url(
                Bucket=r,
                Key=k,
                Expired=expired
            ))
    return urls


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