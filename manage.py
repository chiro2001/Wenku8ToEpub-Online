import os
from flask import *
from manager import *
import io
# import urllib.parse
import threading
import re
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from database import DataBase
import error_report


db = DataBase()
app = Flask(__name__)
threads = []
my_email = 'LanceLiang2018@163.com'
my_password = '1352040930wenku8'


def get_icon(email):
    return'https://s.gravatar.com/avatar/' + hashlib.md5(email.lower().encode()).hexdigest() + '?s=34'


def has_file(target):
    r = requests.get(target, stream=True)
    if int(r.status_code) == 200:
        return True
    return False


def file_size(target):
    r = requests.get(target, stream=True)
    if int(r.status_code) == 200:
        return int(r.headers['Content-Length'])
    return 0


def local_check(book_id):
    wk = Wenku8ToEpub()
    filename_ = wk.id2name(book_id) + '.epub'
    info = wk.bookinfo(book_id)
    if info is None:
        return '1'  # 需要更新
    # 检查上次上传时间
    last_time = v2_check_time(filename_)
    if last_time is None:
        return '1'
    last_time = last_time[:10]
    if last_time > info['update']:
        return '0'
    return '1'  # 需要更新


def send_email(user, email, message):
    # print(user, message)
    my_sender = 'LanceLiang2018@163.com'  # 发件人邮箱账号
    my_pass = '1352040930smtp'  # 发件人邮箱密码
    # my_user = '1352040930@qq.com'  # 收件人邮箱账号
    try:
        # print('try to send:', user)
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = formataddr(["USER:%s" % user, my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(['Lance Liang', my_sender])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "来自 %s(%s) 的新消息" % (user, email)  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL("smtp.163.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_sender, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as e:
        print(e)
        error_report.report_it(e)


def send_email_2(user, email, message):
    my_sender = 'LanceLiang2018@163.com'  # 发件人邮箱账号
    my_pass = '1352040930smtp'  # 发件人邮箱密码
    # my_user = '1352040930@qq.com'  # 收件人邮箱账号
    try:
        # print('try to send:', user)
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = formataddr(["Lance Liang", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(['%s' % user, email])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "Re:您在wenku8.herokuapp.com的反馈"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL("smtp.163.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [email, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as e:
        print(e)
        error_report.report_it(e)


@app.route('/', methods=['GET'])
def index():
    # return '<a href="https://github.com/LanceLiang2018/Wenku8ToEpub-Online">' \
    #        'https://github.com/LanceLiang2018/Wenku8ToEpub-Online</a>'
    local = False
    if os.environ.get('WENKU8_LOCAL', 'False') == 'True':
        local = True
    urls = make_urls()
    return render_template('index.html', local=local, urls=urls)


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


@app.route('/v2/check/<int:book_id>', methods=['GET'])
def v2_check(book_id):
    wk = Wenku8ToEpub()
    filename_ = wk.id2name(book_id) + '.epub'
    info = wk.bookinfo(book_id)
    if info is None:
        return '1'  # 需要更新
    # 检查上次上传时间
    last_time = v2_check_time(filename_)
    if last_time is None:
        return '1'
    last_time = last_time[:10]
    if last_time > info['update']:
        return '0'
    return '1'  # 不需要更新


@app.route('/v2/search/<string:key>', methods=['GET'])
def v2_search(key: str):
    wk = Wenku8ToEpub()
    results = wk.search(key)
    return json.dumps(results)


@app.route('/v2/name/<string:book_name>')
def v2_jump_by_name(book_name):
    filename = "%s.epub" % book_name
    target = 'https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename
    if has_file(target):
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
                threads.remove(t)
                url = th_results.get(str(book_id))
                if url is None:
                    return '1'
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
    filename = urllib.parse.quote(filename)
    target = 'https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/%s' % filename
    if has_file(target):
        return target
    return ''


@app.route('/v2/comments', methods=['GET'])
def v2_comments():
    data = db.get_comments(show_email=False)
    return json.dumps(data)


@app.route('/v2/feedback', methods=['POST'])
def v2_feedback():
    form = dict(request.form)
    message = form.get('message', '')[0]
    user = form.get('user', '')[0]
    email = form.get('email', '')[0]
    password = form.get('password', '')[0]
    head = get_icon(email)
    logger.info(str((user, email, message, password)))
    if len(password) > 0:
        if password == my_password:
            # 老子是管理员，给别人发消息，user是名字。
            target_email = db.find_email(user)
            if '' == target_email:
                return '邮箱查找失败'
            send_email_2(user, target_email, message)
            db.put_comment('Lance->@%s' % user, my_email, message, head)
            return '管理员操作成功'
        else:
            return '管理员密码错误'
    else:
        send_email(user, email, message)
        db.put_comment(user, email, message, head)
        pass
    return ''


@app.route('/v2/visitors')
def v2_visitors():
    api = 'https://api.baidu.com/json/tongji/v1/ReportService/getData'
    r = requests.post()


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


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return redirect('/static/favicon.ico')


@app.route('/baidu_verify_kBBfcDGnTX.html', methods=['GET'])
def baidu_verify():
    return 'kBBfcDGnTX'


if __name__ == '__main__':
    app.run("0.0.0.0", port=int(os.environ.get('PORT', '80')), debug=False)

