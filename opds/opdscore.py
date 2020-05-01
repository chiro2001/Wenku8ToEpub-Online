# coding: UTF-8
import logging
import os
from xml.dom.minidom import Document, Text, Element
import datetime
from flask import g
import opds.Config as Config
import opds.Const as Const
from opds.filesystem import LocalFileSystem, QiniuFileSystem, LocalMetadataFileSystem, TencentFileSystem
import opds.utils as utils

__author__ = 'lei'
if Config.filesyste_type == 'LocalFileSystem':
    fs = LocalFileSystem()
elif Config.filesyste_type == 'LocalMetadataFileSystem':
    fs = LocalMetadataFileSystem()
elif Config.filesyste_type == 'TencentFileSystem':
    fs = TencentFileSystem()
else:
    fs = QiniuFileSystem()


def setfeedNS(feed):
    feed.setAttribute("xmlns:app", "http://www.w3.org/2007/app")
    feed.setAttribute("xmlns:opds", "http://opds-spec.org/2010/catalog")
    feed.setAttribute("xmlns:opds", Config.SITE_URL)
    feed.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    # feed.setAttribute("xmlns", "http://www.w3.org/2005/Atom")
    feed.setAttribute("xmlns:dcterms", "http://purl.org/dc/terms/")
    feed.setAttribute("xmlns:thr", "http://purl.org/syndication/thread/1.0")
    feed.setAttribute("xmlns:opensearch", "http://a9.com/-/spec/opensearch/1.1/")


def getCreateDate(file_path):
    # return datetime.datetime.now(os.path.getctime(file_path)).strftime("%Y-%m-%dT%I:%M:%SZ")
    return datetime.datetime.now().strftime("%Y-%m-%dT%I:%M:%SZ")


def create_entry(isFile, path, name):
    '''
    create filesystem return object
    :param isFile:
    :param path:
    :param name:
    :return:
    '''
    entry = Entry()
    if not isFile:
        entry.id = utils.connect_path(utils.connect_path(Config.SITE_BOOK_LIST, path), name)
        entry.links = []
        entry.links.append(Link(entry.id, _get_book_entry_rel(name), name, _get_book_entry_type(name)))
    else:
        entry.id = utils.connect_path(utils.connect_path(Config.SITE_BOOK_LIST, path), name)
        # TODO add Another Links
        links = fs.getdownloadurl(path, name)
        # name=os.path.basename(path)
        entry.links = []
        if links != None:
            for link in links:
                entry.links.append(Link(link, _get_book_entry_rel(link), name, _get_book_entry_type(link)))
    entry.content = name
    entry.title = name
    entry.updated = utils.getUpdateTime(name)
    return entry


def create__single_entry(isFile, path, name):
    '''
    create filesystem return object for file request
    :param isFile:
    :param path:
    :param name:
    :return:
    '''
    entry = Entry()
    if not isFile:
        entry.id = utils.connect_path(utils.connect_path(Config.SITE_BOOK_LIST, path), name)
        entry.links = []
        entry.links.append(Link(entry.id, _get_book_entry_rel(name), name, _get_book_entry_type(name)))
    else:
        entry.id = utils.connect_path(utils.connect_path(Config.SITE_BOOK_LIST, path), name)
        # TODO add Another Links
        links = fs.getdownloadurl(os.path.dirname(path), name)
        entry.links = []
        if links != None:
            for link in links:
                entry.links.append(Link(link, _get_book_entry_rel(link), name, _get_book_entry_type(link)))
    entry.content = name
    entry.title = name
    entry.updated = utils.getNow()
    return entry


def _get_book_entry_type(name):
    """
    get link type
    """
    if name.endswith(".pdf"):
        return Const.book_type_pdf
    elif name.endswith(".epub"):
        return Const.book_type_epub
    elif name.endswith(".jpg"):
        return Const.book_type_picture
    elif name.endswith(".mobi"):
        return Const.book_type_mobi
    elif name.endswith(".txt"):
        return Const.book_type_text
    elif name.find('.') != -1:
        return Const.book_type_content
    else:
        # No subifx
        return Const.book_type_entry_catalog


def _get_book_entry_rel(name):
    """
    get link type
    """
    if name.endswith(".pdf"):
        return Const.book_link_rel__acquisition
    elif name.endswith(".epub"):
        return Const.book_link_rel__acquisition
    elif name.endswith(".jpg"):
        return Const.book_link_rel_image
    elif name.endswith(".mobi"):
        return Const.book_link_rel__acquisition
    elif name.endswith(".txt"):
        return Const.book_link_rel__acquisition
    elif name.find('.') != -1:
        return Const.book_link_rel_subsection
    else:
        # No subifx
        return Const.book_link_rel_subsection


class FeedDoc:
    def __init__(self, doc, path=None):
        """
        Root Element
        :param doc:  Document()
        :return:
        """
        self.doc = doc
        # xml-stylesheet
        if fs.isfile(path):
            self.doc.appendChild(self.doc.createProcessingInstruction("xml-stylesheet",
                                                                      "type=\"text/xsl\" "
                                                                      "href=\"%s/static/bookdetail.xsl\"" %
                                                                      Config.SITE_URL))
        else:
            self.doc.appendChild(self.doc.createProcessingInstruction("xml-stylesheet",
                                                                      "type=\"text/xsl\" "
                                                                      "href=\"%s/static/booklist.xsl\"" %
                                                                      Config.SITE_URL))
        # feed
        self.feed = self.doc.createElement("feed")
        setfeedNS(self.feed)
        self.addNode(self.feed, Const.id, Config.SITE_URL)
        self.addNode(self.feed, Const.author, Config.SITE_EMAIL)
        self.addNode(self.feed, Const.title, Config.SITE_TITLE)
        self.addNode(self.feed, Const.updated, utils.getNow())
        self.addNode(self.feed, Const.description, Config.description)
        # def createLink(self, entry, href, rel, title, type):
        self.createLink(self.feed, Config.SITE_URL, "Home", "Home",
                        "application/atom+xml; profile=opds-catalog; kind=navigation")
        # self.createLink(self.feed, 'search.xml', Const.search, "Search",
        #                 "application/opensearchdescription+xml")


        self.doc.appendChild(self.feed)
        pass

    def addNode(self, element, key, value, link=None):
        """
        add A node to element
        :param element:
        :param key:
        :param value:   can be str & Element
        :param link:  if is link ,this field is Not None.
        :return:
        """
        if isinstance(value, Element):
            element.appendChild(value)
        else:
            node = self.doc.createElement(key)
            node.appendChild(self.doc.createTextNode(value))
            element.appendChild(node)

    def toString(self):
        # return self.doc.toxml("utf-8")
        return self.doc.toprettyxml(encoding='utf-8')

    def createEntry(self, entry):
        entryNode = self.doc.createElement(Const.entry)

        self.addNode(entryNode, Const.entry_title, entry.title)
        self.addNode(entryNode, Const.entry_updated, entry.updated)
        self.addNode(entryNode, Const.entry_id, entry.id)
        self.addNode(entryNode, Const.entry_content, entry.content)
        for link in entry.links:
            self.createLink(entryNode, link.href, link.rel, link.title, link.type)
        self.feed.appendChild(entryNode)

    def createLink(self, entry, href, rel, title, type):
        link = self.doc.createElement(Const.link)
        link.setAttribute("href", href)
        link.setAttribute("rel", rel)
        link.setAttribute("title", title)
        link.setAttribute("type", type)
        text = self.doc.createTextNode(href)
        link.appendChild(text)
        entry.appendChild(link)
        return link


class Entry:
    def __init__(self, title=None, updated=None, id=None, content=None, links=[]):
        self.links = links
        self.content = content
        self.id = id
        self.updated = updated
        self.title = title


class Link:
    """
    Link Entity
    """

    def __init__(self, href, rel, title, type):
        self.href = href
        self.rel = rel
        self.title = title
        self.type = type


class OpdsProtocol:
    """
    All Opds File System Must Realized this Class
    """

    def listBooks(self, path):
        """
        :return: {entiry ...}
        """
        rslist = []

        # not exist!

        if path != '/' and not fs.exists(path):
            logging.info("dest Path [%s] is Not Exist." % path)
            return rslist

        if fs.isfile(path):
            logging.info("dest Path [%s] is a File Not Right." % path)
            g.book_process = "detail"
            rslist.append(create__single_entry(True, path, os.path.basename(path)))
            return rslist

        bookmap = {}

        for name in fs.listdir(path):
            try:
                name = name.decode("utf-8")
            except Exception:
                try:
                    name = name.decode("gbk")

                except Exception as e:
                    pass

            file_path = utils.connect_path(path, name)

            rslist.append(create_entry(fs.isfile(file_path), path, name))

        return rslist

    def dowloadBook(self, path):
        """
        file
        :param path:
        :return: file
        """

        return utils.connect_path(Config.base, path)

    def showhtml(self):
        return ("No Realized")
        pass
