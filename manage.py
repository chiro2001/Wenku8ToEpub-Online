import os
from flask import *
from manager import *
import io
import urllib.parse
import threading


app = Flask(__name__)

threads = []


@app.route('/', methods=['GET'])
def index():
    # return '<a href="https://github.com/LanceLiang2018/Wenku8ToEpub-Online">' \
    #        'https://github.com/LanceLiang2018/Wenku8ToEpub-Online</a>'
    return render_template('index.html')


@app.route('/bookinfo/<int:book_id>', methods=['GET'])
def get_bookinfo(book_id: int):
    wk = Wenku8ToEpub()
    filename_ = wk.id2name(book_id) + '.epub'
    info = wk.bookinfo(book_id)
    if info is None:
        return json.dumps({})
    # 检查上次上传时间
    last_time = v2_check_time(filename_)
    info['update_time'] = last_time
    return json.dumps(info)


# @app.route('/v2/')
@app.route('/v2/name/<string:book_name>')
def v2_jump_by_name(book_name):
    filename = "%s.epub" % book_name
    target = 'https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename
    r = requests.get(target, stream=True)
    if int(r.status_code) == 200:
        return target
    return ''


@app.route('/v2/cache/<int:book_id>')
def v2_cache(book_id: int, image=False):
    wk = Wenku8ToEpub()
    filename_ = wk.id2name(book_id)
    if filename_ == '':
        return '1'
    for t in threads:
        if t['bid'] == book_id:
            return '2'
    mlogger = MLogger()
    th = threading.Thread(target=v2_work, args=(book_id, None, mlogger, image))
    th.setDaemon(True)
    th.start()
    # filename = "%s.epub" % filename_
    # url = 'https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename
    threads.append({
        'bid': book_id,
        'th': th,
        'messages': mlogger,
        # 'result': url
    })
    # url = work(book_id)
    return '0'


@app.route('/v2/cache_img/<int:book_id>')
def v2_cache_img(book_id: int):
    return v2_cache(book_id, image=True)


@app.route('/v2/cache_status/<int:book_id>')
def v2_cache_status(book_id: int):
    for t in threads:
        if t['bid'] == book_id:
            if t['th'].isAlive():
                return '0'
            else:
                # url = t['result']
                url = results[str(book_id)]
                threads.remove(t)
                return url
    return '1'


@app.route('/v2/cache_logs/<int:book_id>')
def v2_cache_logs(book_id: int):
    for t in threads:
        if t['bid'] == book_id:
            data = t['messages'].read_all()
            return data
    return ''


@app.route('/v2/get/<int:book_id>')
def v2_get(book_id: int):
    wk = Wenku8ToEpub()
    filename_ = wk.id2name(book_id)
    if filename_ == '':
        return ''
    filename = "%s.epub" % filename_
    return 'https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename


@app.route('/cache/<int:book_id>')
def cache(book_id: int):
    wk = Wenku8ToEpub()
    filename_ = wk.id2name(book_id)
    if filename_ == '':
        return '没有这个小说！'
    url = work(book_id)
    return redirect(url)


@app.route('/cache_img/<int:book_id>')
def cache_img(book_id: int):
    wk = Wenku8ToEpub()
    filename_ = wk.id2name(book_id)
    if filename_ == '':
        return '没有这个小说！'
    url = work4(book_id)
    return redirect(url)


@app.route('/no_cache/<int:book_id>')
def no_cache(book_id: int):
    wk = Wenku8ToEpub()
    filename_ = wk.id2name(book_id)
    if filename_ == '':
        return '没有这个小说！'

    data = work3(book_id)
    fp = io.BytesIO(data)

    # urlencode方案
    # filename_ = urllib.parse.urlencode({'': filename_})[1:] + '.epub'
    # latin-1 方案

    filename_ = ("%s.epub" % filename_).encode().decode('latin-1')
    response = make_response(send_file(fp, attachment_filename="%s" % filename_))
    response.headers["Content-Disposition"] = "attachment; filename=%s;" % filename_
    return response

    # url = work3(book_id)
    # return redirect(url)


@app.route('/get/<int:book_id>')
def get(book_id: int):
    wk = Wenku8ToEpub()
    filename_ = wk.id2name(book_id)
    if filename_ == '':
        return '没有这个小说！'
    filename = "%s.epub" % filename_
    return redirect('https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename)


@app.route('/name/<string:book_name>')
def jump_by_name(book_name: str):
    filename = "%s.epub" % book_name
    return redirect('https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename)


@app.route('/search')
def search():
    args0 = dict(request.args)
    args = {}
    for arg in args0:
        v = args0[arg]
        if type(v) is list:
            args[arg] = v[0]
        else:
            args[arg] = v
    # print(args)
    method = args['method']
    search_key = args['search_key']
    bid = None
    if method == 'id':
        try:
            bid = int(search_key)
        except ValueError:
            return "ID输入错误！"
        return redirect('/get/%s' % bid)
    elif method == 'name':
        return redirect('/name/%s' % search_key)
    elif method == 'cache':
        return redirect('/cache/%s' % search_key)
    elif method == 'cache_img':
        return redirect('/cache_img/%s' % search_key)
    else:
        return '参数不正确'


if __name__ == '__main__':
    app.run("0.0.0.0", port=int(os.environ.get('PORT', '5000')), debug=False)

