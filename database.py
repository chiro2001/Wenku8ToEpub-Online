import requests
import time
import pymongo


'''
DATA:
{
    username: ...,
    email: ...,
    message: ...
}
'''


class DataBase:
    def __init__(self):
        self.client = None
        self.db = None
        self.col = None
        self.connect_init()

    def connect_init(self):
        # 下面这个是哪个数据库来着？？？
        # self.client = pymongo.MongoClient("mongodb+srv://LanceLiang:1352040930database@lanceliang-lktmq.azure."
        #                                   "mongodb.net/test?retryWrites=true&w=majority")
        self.client = pymongo.MongoClient("mongodb+srv://lanceliang:1352040930database@lanceliang-9kkx3.azure."
                                          "mongodb.net/test?retryWrites=true&w=majority")
        # self.client = pymongo.MongoClient()
        self.db = self.client.wenku8_comments
        self.col = self.db.wenku8_comments

    def db_init(self):
        collection_names = self.db.list_collection_names()
        if 'wenku8_comments' in collection_names:
            self.db.drop_collection('wenku8_comments')
        self.col = self.db.wenku8_comments

    def put_comment(self, username: str, email: str, message: str, head: str):
        self.col.insert_one({'username': username, 'email': email, 'message': message, 'head': head})

    def get_comments(self, count=5000, show_email=True):
        result = list(self.col.find({}, {'username': 1, 'email': 1, 'message': 1, 'head': 1, '_id': 0}).limit(count))
        if not show_email:
            for i in range(len(result)):
                result[i]['email'] = ''
        return result

    def find_email(self, username: str):
        data = list(self.col.find({'username': username}, {'username': 1, 'email': 1, 'message': 1, '_id': 0}))
        if len(data) == 0:
            return ''
        return data[-1]['email']

    def error_report(self, error):
        self.db.wenku8_bugs.insert_one({'time': time.asctime(), 'error': error})


if __name__ == '__main__':
    _db = DataBase()
    _db.db_init()
    _db.put_comment('lance', 'lanceliang2018@163.com', 'messagefsiafjaiso')
    print(_db.get_comments(show_email=True))
