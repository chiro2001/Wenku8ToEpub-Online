import io
from wenku8toepub import *
from tqdm import trange
from manage import *


# 刷新一遍缓存
path = 'books/'
file = 'progress.txt'
errors = 'errors.txt'
if not os.path.exists(path):
    os.mkdir(path)
if not os.path.exists(file):
    with open(file, 'w') as f:
        f.write('1')
if not os.path.exists(errors):
    with open(errors, 'w') as f:
        f.write('')


def max_bid():
    # url_main = 'https://www.wenku8.net/index.php'
    # soup = Soup(requests.get(url_main).content, 'html.parser')
    # print(soup.find_all(attrs={'class': ''}))
    return 2706


def main():
    with open(file, 'r') as f:
        now = int(f.read())
    # get max:
    mbid = max_bid()
    for bid in trange(now, mbid):
        wk = Wenku8ToEpub()
        wk.login()
        title = wk.id2name(bid)
        filename = "%s.epub" % title
        try:
            # 先判断一波：是否需要下载？
            # 没版权的都更新一遍。
            has_copyright = wk.copyright(bid)
            # 最新版本的跳过。
            if local_check(bid) == '0' and has_copyright:
                logger.debug('BID %s最新版本而且有版权，跳过。' % bid)
                continue
            # 之后再手动上传。
            wk.get_book(bid, savepath=path, fetch_image=False)
        except Exception:
            logger.warn('错误:', bid, '尝试备用方案')
            with open(errors, 'a') as p:
                p.write(str(bid) + '\n')
            data = wk.txt2epub(bid)
            with open(os.path.join(path, "%s.epub" % title), 'wb') as f:
                f.write(data)
        finally:
            with open(file, 'w') as f:
                f.write(str(bid))
        try:
            client.put_object_from_local_file(
                Bucket=bucket,
                Key=filename,
                LocalFilePath=os.path.join(path, filename)
            )
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    main()