import os
from flask import *
from manager import *


app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return '<a href="https://github.com/LanceLiang2018/Wenku8ToEpub-Online">' \
           'https://github.com/LanceLiang2018/Wenku8ToEpub-Online</a>'


@app.route('/cache/<int:book_id>')
def cache(book_id: int):
    url = work(book_id)
    return redirect(url)


@app.route('/get/<int:book_id>')
def get(book_id: int):
    wk = Wenku8ToEpub()
    filename_ = wk.id2name(book_id)
    if filename_ == '':
        return '没有这个小说！'
    filename = "%s.epub" % filename_
    return redirect('https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename)


if __name__ == '__main__':
    app.run("0.0.0.0", port=int(os.environ.get('PORT', '5000')), debug=False)

