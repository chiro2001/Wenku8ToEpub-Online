import requests
import bs4
from bs4 import BeautifulSoup as Soup
from ebooklib import epub
import os
import sys
import getopt
from base_logger import getLogger
import threading
import io
import copy
import re


class MLogger:
    def __init__(self):
        self.data = io.StringIO()

    def write(self, content: str):
        self.data.write(content + '\n')
        print(content)

    def read_all(self):
        lock.acquire()
        data2 = copy.deepcopy(self.data)
        data2.seek(0)
        d = data2.read()
        lock.release()
        return d

    def info(self, message):
        self.write(message)

    def error(self, message):
        self.write(message)

    def warning(self, message):
        self.write(message)

    def warn(self, message):
        self.write(message)

    def critical(self, message):
        self.write(message)

    def debug(self, message):
        self.write(message)


class Wenku8ToEpub:
    def __init__(self):
        # api格式
        # 参数1：id千位开头
        # 参数2：id
        self.api = "https://www.wenku8.net/novel/%s/%d/"
        self.api_info = "https://www.wenku8.net/book/%d.htm"
        self.api_img = "http://img.wkcdn.com/image/%s/%d/%ds.jpg"
        self.img_splits = ['http://pic.wenku8.com/pictures/',
                           'http://pic.wkcdn.com/pictures/',
                           'http://picture.wenku8.com/pictures/']
        self.api_login = 'http://www.wenku8.net/login.php?do=submit"'
        self.api_serach = 'http://www.wenku8.net/modules/article/search.php?searchtype=articlename&searchkey=%s'
        self.api_txt = 'http://dl.wenku8.com/down.php?type=txt&id=%d'
        self.cookies = ''
        self.cookie_jar = None
        self.book = epub.EpubBook()
        self.thread_img_pool = []
        self.thread_pool = []
        # 用于章节排序的文件名
        self.sumi = 0
        # 目录管理
        self.toc = []
        # 主线
        self.spine = ['cover', 'nav']
        # 当前章节
        self.chapters = []
        self.book_id = 0
        self.logger = logger

    # 登录，能够使用搜索功能。
    def login(self, username='lanceliang', password='1352040930lxr'):
        payload = {'action': 'login',
                   'jumpurl': '',
                   'username': username,
                   'password': password}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", self.api_login, headers=headers, data=payload)
        html = response.content.decode('gbk')
        if '登录成功' not in html:
            self.logger.error("登录失败")
            return
        cookie_value = ''
        for key, value in response.cookies.items():
            cookie_value += key + '=' + value + ';'
        self.cookies = cookie_value
        self.cookie_jar = response.cookies

    # 搜索，应该先登录
    def search(self, key: str):
        results = {
            'key': key,
            'books': []
        }
        self.login()
        if len(self.cookies) == 0 or self.cookie_jar is None:
            # 还没有登录
            self.logger.error("请先登录再使用搜索功能")
            return results
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
            'Content-Type': 'multipart/form-data; boundary=--------------------------607040101744888865545920',
            'Cookie': self.cookies
        }
        # 注意编码问题
        # 云 -> %D4%C6
        encodings = key.encode('gbk').hex().upper()
        key_arg = ''
        for i in range(0, len(encodings), 2):
            key_arg = key_arg + '%' + encodings[i] + encodings[i+1]
        response = requests.request("GET", self.api_serach % key_arg, headers=headers, cookies=self.cookie_jar)
        html = response.content.decode("gbk", errors='ignore')
        soup = Soup(html, 'html.parser')

        if '推一下' in html:
            # 直接进入了单本状态
            # print(soup)
            # print(title, bid, cover, status, brief)
            title = soup.find_all('b')[1].get_text()
            bid = ''
            for n in re.findall('\d', response.url)[1:]:
                bid = bid + n
            bid = int(bid)
            try:
                cover = soup.find_all('img')[1].get_attribute_list('src')[0]
            except IndexError:
                cover = None
            try:
                status = soup.find_all('table')[0].find_all('tr')[2].get_text().replace('\n', ' ')
            except IndexError:
                status = None
            try:
                brief = soup.find_all('table')[2].find_all('td')[1].find_all('span')[4].get_text()
            except IndexError:
                spans = soup.find_all('span')
                for i in range(len(spans)):
                    if '内容简介' in spans[i].get_text():
                        brief = spans[i+1].get_text()
            book = {
                'title': title, 'bid': bid, 'cover': cover, 'status': status, 'brief': brief
            }
            return [book, ]

        '''
        # 暂时只搜索一页内容
        links = soup.find_all('a')
        books = []
        for a in links:
            if a.has_attr('href') and len(a.get_attribute_list('href')) != 0:
                href = a.get_attribute_list('href')[0]
                if '//www.wenku8.net/book/' in href and href not in books:
                    books.append(href)
        # print(books)
        bids = []
        for book in books:
            numbers = re.findall('\d', book)[1:]
            bid = ''
            for n in numbers:
                bid = bid + n
            bids.append(int(bid))
        print(bids)
        '''
        td = soup.find('td')
        books = []
        for content in td.children:
            if not isinstance(content, bs4.element.Tag):
                continue
            # print(content)
            # print('#' * 64)
            title = content.find_all('a')[1].get_text()
            url = content.find_all('a')[1].get_attribute_list('href')[0]
            numbers = re.findall('\d', url)[1:]
            bid = ''
            for n in numbers:
                bid = bid + n
            bid = int(bid)
            cover = content.find_all('img')[0].get_attribute_list('src')[0]
            status = content.find_all('p')[0].get_text()
            brief = content.find_all('p')[1].get_text()[3:]
            # print(title, bid, cover, status, brief)
            book = {
                'title': title, 'bid': bid, 'cover': cover, 'status': status, 'brief': brief
            }
            books.append(book)

        return books

    # 获取书籍信息。
    # {
    #   id, name, author, brief, cover, copyright
    # }
    def bookinfo(self, book_id: int):
        url_cat = "%s%s" % (self.api % (("%04d" % book_id)[0], book_id), "index.htm")
        soup_cat = Soup(requests.get(url_cat).content, 'html.parser')
        table = soup_cat.select('table')
        if len(table) == 0:
            self.logger.error("遇到错误")
            return None
        table = table[0]

        if len(soup_cat.select("#title")) == 0:
            self.logger.error('该小说不存在！id = ' + str(book_id))
            return None
        title = soup_cat.select("#title")[0].get_text()
        author = soup_cat.select("#info")[0].get_text().split('作者：')[-1]
        url_cover = self.api_img % (("%04d" % book_id)[0], book_id, book_id)
        # print(title, author, url_cover)

        brief = ''
        url_cat2 = self.api_info % (book_id)
        soup_cat2 = Soup(requests.get(url_cat2).content, 'html.parser')
        update = ''
        for td in soup_cat2.find_all('td'):
            if '最后更新' in td.get_text():
                update = td.get_text()[5:]
        iscopyright = True
        if '因版权问题，文库不再提供该小说的在线阅读与下载服务！' in soup_cat2.get_text():
            iscopyright = False
        spans = soup_cat2.select('span')
        for i in range(len(spans)):
            span = spans[i]
            if '内容简介' in span.get_text():
                brief = spans[i + 1].get_text()
        return {
            "id": book_id,
            "name": title,
            "author": author,
            "brief": brief,
            "cover": url_cover,
            'copyright': iscopyright,
            'update': update
        }

    # 获取版权状态
    def copyright(self, book_id=None):
        if book_id is None:
            book_id = self.book_id
        data = requests.get(self.api_info % book_id).content
        soup = Soup(data, 'html.parser')
        if '因版权问题，文库不再提供该小说的在线阅读与下载服务！' in soup.get_text():
            return False
        return True

    def id2name(self, book_id: int):
        url_cat = "%s%s" % (self.api % (("%04d" % book_id)[0], book_id), "index.htm")
        soup_cat = Soup(requests.get(url_cat).content, 'html.parser')
        table = soup_cat.select('table')
        if len(table) == 0:
            self.logger.error("遇到错误")
            return ''
        table = table[0]

        if len(soup_cat.select("#title")) == 0:
            self.logger.error('该小说不存在！id = ' + str(book_id))
            return ''
        title = soup_cat.select("#title")[0].get_text()
        # author = soup_cat.select("#info")[0].get_text().split('作者：')[-1]
        # url_cover = self.api_img % (("%04d" % self.book_id)[0], self.book_id, self.book_id)
        return title

    def get_page(self, url_page: str, title: str = ''):
        data = requests.get(url_page).content
        soup = Soup(data, 'html.parser')
        content = soup.select('#content')[0]
        # 去除ul属性
        [s.extract() for s in content("ul")]
        return ("<h1>%s</h1>%s" % (title, content.prettify())).encode()

    def fetch_img(self, url_img):
        self.logger.info('Fetching image: ' + url_img + '...')
        data_img = requests.get(url_img).content
        filename = url_img
        for sp in self.img_splits:
            filename = url_img.split(sp)[-1]
        filetype = url_img.split('.')[-1]
        # print('done. filename:', filename, "filetype", filetype)
        img = epub.EpubItem(file_name="images/%s" % filename,
                            media_type="image/%s" % filetype, content=data_img)
        lock.acquire()
        self.book.add_item(img)
        lock.release()
        self.logger.info('\tDone image: ' + url_img)

    def fetch_chapter(self, a, order: int, fetch_image: bool):
        if a.get_text() == '插图':
            self.logger.info('Images: ' + a.get_text())
        else:
            self.logger.info('chapter: ' + a.get_text())

        title_page = a.get_text()

        url_page = "%s%s" % (self.api % (("%04d" % self.book_id)[0], self.book_id), a.get('href'))

        data_page = self.get_page(url_page, title=title_page)
        page = epub.EpubHtml(title=title_page, file_name='%s.xhtml' % self.sumi)
        # 多线程模式下文件名会不按照顺序...
        self.sumi = self.sumi + 1

        if fetch_image is True:
            soup_tmp = Soup(data_page, 'html.parser')
            imgcontent = soup_tmp.select(".imagecontent")
            self.thread_img_pool = []
            for img in imgcontent:
                url_img = img.get("src")
                th = threading.Thread(target=self.fetch_img, args=(url_img,))
                self.thread_img_pool.append(th)
                th.setDaemon(True)
                th.start()

            for it in self.thread_img_pool:
                it.join()

            for url in self.img_splits:
                data_page = (data_page.decode().replace(url, 'images/')).encode()

        page.set_content(data_page)
        lock.acquire()
        self.book.add_item(page)
        lock.release()

        # self.toc[-1][1].append(page)
        # self.spine.append(page)
        self.chapters[order] = page

    def get_book_no_copyright(self, targets,
                              bin_mode: bool = False,
                              savepath: str = '',
                              author: str = 'undefind'):
        # txt = requests.get(self.api_txt % self.book_id).content.decode('gbk', errors='ignore')
        response = requests.get(self.api_txt % self.book_id, stream=True)
        chunk_size = 1024 * 100  # 单次请求最大值
        # print(response.headers)
        content_size = 0  # 内容体总大小
        self.logger.info('该书没有版权，开始下载TXT文件转化为EPUB')
        data_download = io.BytesIO()
        for data in response.iter_content(chunk_size=chunk_size):
            data_download.write(data)
            content_size = int(content_size + len(data))
            self.logger.info('已经下载 %s KB' % (content_size // 1024))
        # with open('%s.txt' % self.book_id, 'w', encoding='gbk') as f:
        #     f.write(txt)
        # with open('%s.txt' % self.book_id, 'r', encoding='gbk') as f:
        #     txt = f.read()
        data_download.seek(0)
        txt = data_download.read().decode('gbk', errors='ignore')
        self.logger.info('TXT下载完成')
        title = re.findall('<.+>', txt[:81])[0][1:-1]
        txt = txt[40 + len(title):-76]
        # print(txt)
        # print(title)

        volumes = []
        chapters = []
        for tar in targets:
            if tar.get_attribute_list('class')[0] == 'vcss':
                volumes.append(tar.get_text())
                chapters.append({
                    'volume': tar.get_text(),
                    'chapters': []
                })
                continue
            if tar.get_attribute_list('class')[0] == 'ccss' \
                and tar.get_text().encode() != b'\xc2\xa0':
                chapters[-1]['chapters'].append(tar.get_text())
                continue

        last_end = 0
        length = len(txt)
        # for v in chapters:
        for i in range(len(chapters)):
            v = chapters[i]
            txts = []
            volume_text = v['volume']
            self.logger.info('volume: ' + volume_text)
            for c in v['chapters']:
                anchor = "%s %s" % (volume_text, c)
                next_end = txt.find(anchor, last_end, length)
                # print('next_end', next_end)
                if next_end <= 6:
                    continue
                txt_slice = txt[last_end: next_end]
                last_end = next_end
                txt2 = ''
                for line in txt_slice.splitlines():
                    txt2 = txt2 + '<p>%s</p>' % line
                txt_slice = txt2
                txts.append(txt_slice)
            if i + 1 == len(chapters):
                txts.append(txt[last_end:])
            else:
                point = txt.find(chapters[i+1]['volume'], last_end, length)
                # print('point', point)
                txts.append(txt[last_end:point])
                last_end = point-1

            if len(txts) != len(v['chapters']):
                # print('err')
                # 虽然不知道为啥，这么写就对了
                txts = txts[1:]

            # 先增加卷
            self.toc.append((epub.Section(volume_text), []))
            volume = epub.EpubHtml(title=volume_text, file_name='%s.html' % self.sumi)
            self.sumi = self.sumi + 1
            volume.set_content(("<h1>%s</h1><br>" % volume_text).encode())
            self.book.add_item(volume)

            # 增加章节
            for i in range(len(v['chapters'])):
                chapter_title = v['chapters'][i]
                self.logger.info('chapter: ' + chapter_title)
                page = epub.EpubHtml(title=chapter_title, file_name='%s.xhtml' % self.sumi)
                self.sumi = self.sumi + 1
                page.set_content(txts[i])
                lock.acquire()
                self.book.add_item(page)
                lock.release()
                self.toc[-1][1].append(page)
                self.spine.append(page)

        # print('de')
        # exit()

        self.book.toc = self.toc

        # add navigation files
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # create spine
        self.book.spine = self.spine
        if bin_mode is True:
            stream = io.BytesIO()
            epub.write_epub(stream, self.book)
            stream.seek(0)
            return stream.read()
        else:
            epub.write_epub(os.path.join(savepath, '%s - %s.epub' % (title, author)), self.book)

    def get_book(self, book_id: int, savepath: str = '',
                 fetch_image: bool = True,
                 multiple: bool = True, bin_mode: bool = False,
                 mlogger=None):
        if mlogger is not None:
            self.logger = mlogger
        self.book_id = book_id

        url_cat = "%s%s" % (self.api % (("%04d" % self.book_id)[0], self.book_id), "index.htm")
        soup_cat = Soup(requests.get(url_cat).content, 'html.parser')
        table = soup_cat.select('table')
        if len(table) == 0:
            self.logger.error("遇到错误")
            return False
        table = table[0]

        if len(soup_cat.select("#title")) == 0:
            self.logger.error('该小说不存在！id = ' + str(self.book_id))
            return
        title = soup_cat.select("#title")[0].get_text()
        author = soup_cat.select("#info")[0].get_text().split('作者：')[-1]
        url_cover = self.api_img % (("%04d" % self.book_id)[0], self.book_id, self.book_id)
        data_cover = requests.get(url_cover).content
        # print(title, author, url_cover)
        self.logger.info('#' * 15 + '开始下载' + '#' * 15)
        self.logger.info('标题: ' + title + " 作者: " + author)
        self.book.set_identifier("%s, %s" % (title, author))
        self.book.set_title(title)
        self.book.add_author(author)
        self.book.set_cover('cover.jpg', data_cover)

        targets = table.select('td')
        iscopyright = self.copyright()
        if not iscopyright:
        # if iscopyright:
            # 没有版权的时候
            return self.get_book_no_copyright(targets, bin_mode=bin_mode, author=author)

        order = 0
        for tar in targets:
            a = tar.select('a')
            # 这是本卷的标题
            text = tar.get_text()
            # 排除空白表格
            if text.encode() == b'\xc2\xa0':
                # print('排除了', text, text.encode() == b'\xc2\xa0')
                continue
            if len(a) == 0:
                volume_text = tar.get_text()
                self.logger.info('volume: ' + volume_text)

                # 上一章节的chapter
                for th in self.thread_pool:
                    th.join()
                # 已经全部结束
                if len(self.thread_pool) != 0:
                    self.thread_pool = []
                    for chapter in self.chapters:
                        if chapter is None:
                            continue
                        self.toc[-1][1].append(chapter)
                        self.spine.append(chapter)

                self.chapters = [None for i in range(len(targets))]
                order = 0
                self.toc.append((epub.Section(volume_text), []))
                volume = epub.EpubHtml(title=volume_text, file_name='%s.html' % self.sumi)
                self.sumi = self.sumi + 1
                volume.set_content(("<h1>%s</h1><br>" % volume_text).encode())
                self.book.add_item(volume)
                continue
            # 是单章
            a = a[0]

            th = threading.Thread(target=self.fetch_chapter, args=(a, order, fetch_image))
            order = order + 1
            self.thread_pool.append(th)
            th.setDaemon(True)
            th.start()

        # 最后一个章节的chapter
        for th in self.thread_pool:
            th.join()
        # 已经全部结束
        if len(self.thread_pool) != 0:
            self.thread_pool = []
            for chapter in self.chapters:
                if chapter is None:
                    continue
                self.toc[-1][1].append(chapter)
                self.spine.append(chapter)

        self.book.toc = self.toc

        # add navigation files
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # create spine
        self.book.spine = self.spine
        if bin_mode is True:
            stream = io.BytesIO()
            epub.write_epub(stream, self.book)
            stream.seek(0)
            return stream.read()
        else:
            epub.write_epub(os.path.join(savepath, '%s - %s.epub' % (title, author)), self.book)


help_str = '''
把www.wenku8.net的轻小说在线转换成epub格式。wenku8.net没有版权的小说则下载TXT文件然后转换为epub文件。

wk2epub [-h] [-t] [-m] [-b] [list]

    list            一个数字列表，中间用空格隔开

    -t              只获取文字，忽略图片。
                    但是图像远程连接仍然保留在文中。
                    此开关默认关闭，即默认获取图片。

    -m              多线程模式。
                    该开关已默认打开。

    -i              显示该书信息。

    -b              把生成的epub文件直接从stdio返回。
                    此时list长度应为1。
                    调试用。

    -h              显示本帮助。

调用示例:
    wk2epub -t 1 1213

关于:
    https://github.com/LanceLiang2018/Wenku8ToEpub

版本:
    2020/3/8 1:45 AM
'''

logger = getLogger()
lock = threading.Lock()

if __name__ == '__main__':
    # wk = Wenku8ToEpub()
    # wk.get_book(1614)
    # wk.get_book(1016)
    # wk.get_book(1447)
    # print(wk.bookinfo(1))
    # wk.login()
    # print(wk.search('云'))
    # print(wk.search('东云'))
    # print(wk.get_book_no_copyright(1614))
    exit()

    opts, args = getopt.getopt(sys.argv[1:], '-h-t-m-b-i', [])
    _fetch_image = True
    _multiple = True
    _bin_mode = False
    _show_info = False
    if len(args) == 0:
        print(help_str)
        sys.exit()
    for name, val in opts:
        if '-h' == name:
            print(help_str)
            sys.exit()
        if '-t' == name:
            _fetch_image = False
        if '-m' == name:
            _multiple = True
        if '-b' == name:
            _bin_mode = True
        if '-i' == name:
            _show_info = True
    try:
        args = list(map(int, args))
    except Exception as e:
        logger.error("错误: 参数只接受数字。")
        print(help_str)
        sys.exit()

    for _id in args:
        wk = Wenku8ToEpub()
        _bookinfo = wk.bookinfo(_id)
        print('信息：ID:%s\t书名:%s\t作者:%s' % (_bookinfo['id'], _bookinfo['name'], _bookinfo['author']))
        print('简介：\n%s' % _bookinfo['brief'])
        res = wk.get_book(_id, fetch_image=_fetch_image, multiple=_multiple, bin_mode=_bin_mode)
        if _bin_mode is True:
            print(res)


