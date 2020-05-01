# coding: UTF-8

from xml.dom.minidom import Document
from flask import Flask, send_file, make_response, g
import opds.Const as Const
from opds.opdscore import FeedDoc, Link, OpdsProtocol, Entry
import os

import opds.Config as Config

import opds.utils as utils

import logging

__author__ = 'lei'

app = Flask(__name__)


@app.route("/static/<path:stcpath>")
def css(stcpath):
    return app.send_static_file(stcpath)


@app.route("/")
def root():
    d = Document()
    f = FeedDoc(d)
    entry = Entry()
    entry.id = Config.SITE_BOOK_LIST
    entry.content = "all Books List By Type"
    entry.title = "Book List"

    entry.updated = utils.getNow()
    # TODO add Another Links
    entry.links = [Link(entry.id, Const.book_link_rel_subsection, "Book List", Const.book_type_entry_catalog)]
    f.createEntry(entry)
    resp = make_response(f.toString())
    resp.headers['Content-Type'] = 'application/xml; profile=opds-catalog; kind=navigation'
    # print(f.toString())

    return resp


@app.route('/list')
@app.route('/list/<string:path>')
def listbooks(path="/"):
    feed = FeedDoc(Document(), path)

    # TODO add *** to feed.toString()
    l = getOpdsProtocol().listBooks(path)
    # print(l)

    for entry in l:
        feed.createEntry(entry)

    resp = make_response(feed.toString())
    resp.headers['Content-Type'] = 'text/xml; profile=opds-catalog; kind=navigation'
    # print(feed.toString().decode())
    return resp


@app.route('/download/<path:path>')
def download(path):
    """
    download book
    """
    filePath = getOpdsProtocol().dowloadBook(path)
    return send_file(filePath)


@app.route('/show/<path:path>')
def showhtml(path):
    return "show file:" + path


def getOpdsProtocol():
    return OpdsProtocol()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        )
    # app.debug = False
    # app.run(host='0.0.0.0', port=10086)
    app.run("0.0.0.0", port=int(os.environ.get('PORT', '5000')), debug=False)