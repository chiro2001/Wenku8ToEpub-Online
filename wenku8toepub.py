import requests
from bs4 import BeautifulSoup as Soup
from ebooklib import epub
import os
import sys
import getopt
from base_logger import getLogger
import threading
import io


class Wenku8ToEpub:
    def __init__(self):
        # api格式
        # 参数1：id千位开头
        # 参数2：id
        self.api = "https://www.wenku8.net/novel/%s/%d/"
        self.api_img = "http://img.wkcdn.com/image/%s/%d/%ds.jpg"
        self.img_splits = ['http://pic.wenku8.com/pictures/',
                           'http://pic.wkcdn.com/pictures/']
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

    def id2name(self, book_id: int):
        url_cat = "%s%s" % (self.api % (("%04d" % book_id)[0], book_id), "index.htm")
        soup_cat = Soup(requests.get(url_cat).content, 'html.parser')
        table = soup_cat.select('table')
        if len(table) == 0:
            logger.error("遇到错误")
            return ''
        table = table[0]

        if len(soup_cat.select("#title")) == 0:
            logger.error('该小说不存在！id = ' + str(book_id))
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
        logger.info('Fetching image: ' + url_img + '...')
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
        logger.info('\tDone image: ' + url_img)

    def fetch_chapter(self, a, order: int, fetch_image: bool):
        if a.get_text() == '插图':
            logger.info('Images: ' + a.get_text())
        else:
            logger.info('chapter: ' + a.get_text())

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

            data_page = (data_page.decode().replace('http://pic.wkcdn.com/pictures/', 'images/')).encode()

        page.set_content(data_page)
        lock.acquire()
        self.book.add_item(page)
        lock.release()

        # self.toc[-1][1].append(page)
        # self.spine.append(page)
        self.chapters[order] = page

    def get_book(self, book_id: int, savepath: str = '',
                 fetch_image: bool = True,
                 multiple: bool = True, bin_mode: bool = False):
        self.book_id = book_id
        url_cat = "%s%s" % (self.api % (("%04d" % self.book_id)[0], self.book_id), "index.htm")
        soup_cat = Soup(requests.get(url_cat).content, 'html.parser')
        table = soup_cat.select('table')
        if len(table) == 0:
            logger.error("遇到错误")
            return False
        table = table[0]

        if len(soup_cat.select("#title")) == 0:
            logger.error('该小说不存在！id = ' + str(self.book_id))
            return
        title = soup_cat.select("#title")[0].get_text()
        author = soup_cat.select("#info")[0].get_text().split('作者：')[-1]
        url_cover = self.api_img % (("%04d" % self.book_id)[0], self.book_id, self.book_id)
        data_cover = requests.get(url_cover).content
        # print(title, author, url_cover)
        logger.info('#' * 15 + '开始下载' + '#' * 15)
        logger.info('标题: ' + title + " 作者: " + author)
        self.book.set_identifier("%s, %s" % (title, author))
        self.book.set_title(title)
        self.book.add_author(author)
        self.book.set_cover('cover.jpg', data_cover)

        targets = table.select('td')
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
                logger.info('volume: ' + volume_text)

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
把www.wenku8.net的轻小说在线转换成epub格式。

wk2epub [-h] [-t] [-m] [-b] [list]

    list            一个数字列表，中间用空格隔开

    -t              只获取文字，忽略图片。
                    但是图像远程连接仍然保留在文中。
                    此开关默认关闭，即默认获取图片。

    -m              多线程模式。
                    该开关已默认打开。

    -b              把生成的epub文件直接从stdio返回。
                    此时list长度应为1。
                    调试用。

    -h              显示本帮助。

调用示例:
    wk2epub -t 1 1213

关于:
    https://github.com/LanceLiang2018/Wenku8ToEpub

版本:
    2019/4/5 2:51 AM
'''

logger = getLogger()
lock = threading.Lock()

if __name__ == '__main__':
    # wk = Wenku8ToEpub()
    # wk.get_book(2019)
    opts, args = getopt.getopt(sys.argv[1:], '-h-t-m-b', [])
    _fetch_image = True
    _multiple = True
    _bin_mode = False
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

    try:
        args = list(map(int, args))
    except Exception as e:
        logger.error("错误: 参数只接受数字。")
        print(help_str)
        sys.exit()

    for _id in args:
        wk = Wenku8ToEpub()
        res = wk.get_book(_id, fetch_image=_fetch_image, multiple=_multiple, bin_mode=_bin_mode)
        if _bin_mode is True:
            print(res)


