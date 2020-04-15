import requests
import bs4
from bs4 import BeautifulSoup as Soup
from ebooklib import epub
import os
import json
import sys
import getopt
from base_logger import getLogger
import threading
import io
import copy
import re
import asyncio


class MLogger:
    def __init__(self):
        self.data = io.StringIO()

    def write(self, content: str):
        self.data.write(content + '\n')
        print(content)

    def read_all(self):
        data2 = copy.deepcopy(self.data)
        data2.seek(0)
        d = data2.read()
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


class Dmzj2Epub:
    def __init__(self, logger=None):
        self.novel_data_file = 'dmzj_novel_data_full.json'
        # self.novel_data_file = 'dmzj_novel_data.json'
        self.api_novel = 'http://v2.api.dmzj.com/novel/%d.json'
        self.api_chapter = 'http://v2.api.dmzj.com/novel/chapter/%d.json'
        # 'http://v2.api.dmzj.com/novel/download/%d_%d_%d.txt'%(BookId,volume_id,chapter_id)
        self.api_download = 'http://v2.api.dmzj.com/novel/download/%d_%d_%d.txt'

        self.sumi = 0
        self.book = None

        if logger is None:
            self.logger = getLogger()
        else:
            self.logger = logger

        if not os.path.exists(self.novel_data_file):
            raise FileNotFoundError('Can not find ' + self.novel_data_file)
        with open(self.novel_data_file, 'r', encoding='utf8') as f:
            self.novel_data = json.load(f)

    def search(self, key: str):
        results = []
        if len(key) == 0:
            return None
        for d in self.novel_data:
            if key in d['name'] or key in d['authors']:
            # if key in d['title'] or key in d['author']:
                results.append(d)
        return results

    def info(self, bid: int):
        # for d in self.novel_data:
        #     if bid == d['id']:
        #         return d
        # return None
        response = requests.get(self.api_novel % bid).content
        info = json.loads(response)
        if type(info) is list:
            return None
        return info

    def get_volumes_chapters(self, bid: int):
        response = json.loads(requests.get(self.api_chapter % bid).content)
        return response

    def download_img(self, url):
        data = requests.get(url).content
        return data

    def download_chapter(self, bid: int, volume_id: int, chapter_id: int, fetch_image: bool = False):
        content = requests.get(self.api_download % (bid, volume_id, chapter_id)).content
        if fetch_image:
            text = content.decode('utf8', errors='ignore')
            imgs = re.findall('https://xs.dmzj.com/img/[0-9]+/[0-9]+/[a-fA-F0-9]{32,32}.jpg', text)
            # self.logger.debug(str(imgs))
            for img in imgs:
                filename = os.path.basename(img)
                data = self.download_img(img)
                text = text.replace(img, 'images/%s' % filename)
                file_type = filename.split('.')[-1]
                item_img = epub.EpubItem(file_name="images/%s" % filename,
                                    media_type="image/%s" % file_type, content=data)
                self.book.add_item(item_img)
                self.logger.info('<-Done image: ' + img)
            content = text.encode()
        return content
        # soup = Soup(content, 'html.parser')
        # return soup.get_text()

    def download_book(self,
                      bid: int,
                      fetch_image: bool = False):
        self.book = epub.EpubBook()
        self.sumi = 0
        book_info = self.info(bid)
        if book_info is None:
            return None
        title = book_info['name']
        author = book_info['authors']
        cover_url = book_info['cover']
        self.logger.info('#' * 15 + '开始下载' + '#' * 15)
        self.logger.info('标题: ' + title + " 作者: " + author)
        self.book.set_identifier("%s, %s" % (title, author))
        self.book.set_title(title)
        self.book.add_author(author)
        data_cover = requests.get(cover_url).content
        self.book.set_cover('cover.jpg', data_cover)

        toc = []
        spine = []

        volume_chapters = self.get_volumes_chapters(bid)
        for volume in volume_chapters:
            self.logger.info('volume: ' + volume['volume_name'])
            # 先增加卷
            toc.append((epub.Section(volume['volume_name']), []))
            page_volume = epub.EpubHtml(title=volume['volume_name'], file_name='%s.html' % self.sumi)
            self.sumi = self.sumi + 1
            page_volume.set_content(("<h1>%s</h1><br>" % volume['volume_name']).encode())
            self.book.add_item(page_volume)
            for chapter in volume['chapters']:
                self.logger.info('  chapter: ' + chapter['chapter_name'])
                chapter_content = self.download_chapter(bid, volume['volume_id'], chapter['chapter_id'], fetch_image=fetch_image)
                page = epub.EpubHtml(title=chapter['chapter_name'], file_name='%s.xhtml' % self.sumi)
                self.sumi = self.sumi + 1
                page.set_content(chapter_content)
                self.book.add_item(page)
                toc[-1][1].append(page)
                spine.append(page)

        self.book.toc = toc
        self.book.spine = spine
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        stream = io.BytesIO()
        epub.write_epub(stream, self.book)
        return stream.getvalue()


if __name__ == '__main__':
    _de = Dmzj2Epub()
    # print(_de.search('入间人间'))
    # print(_de.info(6))
    # print(_de.get_chapters(6))
    _info = _de.info(2637)
    print(_info)
    _data = _de.download_book(2637)
    with open('%s - %s.epub' % (_info['name'], _info['authors']), 'wb') as f:
        f.write(_data)