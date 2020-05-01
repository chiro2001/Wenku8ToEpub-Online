# coding: UTF-8

__author__ = 'lei'

# #############################
# root for opds server website
# SITE_URL = "http://10.10.113.237:5000"
# SITE_URL = "http://opds.cockybook.com"
SITE_URL = '/opds'
# SITE_URL = 'http://192.168.43.203:10086'
# SITE_URL = 'https://light-opds.herokuapp.com'
SITE_TITLE = "Light Novels OPDS Site"
SITE_EMAIL = "LanceLiang2018@163.com"
SITE_BOOK_LIST = SITE_URL + "/list"

# for local filesyste
base = "/home/lance/Books"

# Used In opdscore.py
# filesyste_type = 'LocalFileSystem'
# filesyste_type = 'QiniuFileSystem'
filesyste_type = 'TencentFileSystem'
# filesyste_type = 'LocalMetadataFileSystem'

# download URL is SITE_BOOK_DONWLOAD/$path/$filename.$postfix
# SITE_BOOK_DONWLOAD = 'http://7sbqcs.com1.z0.glb.clouddn.com'
if filesyste_type == 'TencentFileSystem':
    SITE_BOOK_DONWLOAD = 'https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com'
else:
    SITE_BOOK_DONWLOAD = 'http://192.168.43.203:10086/static/Books'


description = u"""
     OPDS 标准核心功能是支持 EPUB 标准和基于 Atom XML 的目录格式.
可以使用阅读器进行在线书库添加，比如FBReader、静读天下（Moon+ Reader）、Aldiko、Stanza等等.
添加地址为:   %s
（轻小说书源提供&修改代码by LanceLiang2018@163.com）
""" % SITE_URL
