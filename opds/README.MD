#cockybook
演示地址: [http://opds.cockybook.com/][2]

OPDS 标准核心功能是支持 EPUB 标准和基于 Atom XML 的目录格式. 可以使用阅读器进行在线书库添加，比如FBReader、静读天下（Moon+ Reader）、Aldiko、Stanza等等

##cockybook简介
cockybook是python开发的一个opds server 的简易书籍共享服务。
使用python Flask实现。
他的数据源可以是本地存储，也可以是云存储如百度网盘、七牛云存储。当然你可以很方便的自定义实现自己的数据源接口。

##What is OPDS？
OPDS全称是Open Publication Distribution System开放式出版发布系统，使用 Atom 格式，意在为电子书在线目录建立一个公开标准。OPDS 将 RSS 信息源，替换为电子书目录，包括链接到书籍封面和简短摘要的可选链接。使用 OPDS，用户无需到处点击链接，通过电子书应用程序，只需订阅并搜索这些目录，然后就可以将电子书下载到 ebook 阅读器中，不需要再使用浏览器或其他应用程序。
OPDS 标准核心功能是支持 EPUB 标准和基于 Atom XML 的目录格式。

##OPDS协议

可以参考博客：[http://www.cockybook.com/?p=159][3]

##入口
`opdsserver.py`
可以直接启动`opdsserver.py`
这里你可以找到:

```
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                )
    app.debug = True
    app.run(host='0.0.0.0')
```

##程序结构
文件系统接口，你好可以自由扩展。
`opdscore.py` 中主要类：
这个类描述需要实现的主要接口。
```
class OpdsProtocol:
    def listBooks(self, path):
        return ("No Realized")
        pass
    def dowloadBook(self, path):
        return ("No Realized")
        pass
    def showhtml(self):
        return ("No Realized")
        pass
```

`filesystem.py`
你可以在这个类中实现你的数据源文件操作。
目前实现的有LocalFileSystem、QiniuFileSystem。

```
class LocalMetadataFileSystem(FileSystem):
class QiniuFileSystem(FileSystem):
```


##部署
1. 目前可以在[sinaapp][1]中直接部署。index.wsgi 已经写好。
2. 可以直接运行`opdsserver.py`进行发布。


[1]: http://sinaapp.com/
[2]: http://opds.cockybook.com/
[3]: http://www.cockybook.com/?p=159