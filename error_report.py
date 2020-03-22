import os
import json
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


def send_report(report):
    my_sender = 'LanceLiang2018@163.com'  # 发件人邮箱账号
    my_pass = '1352040930smtp'  # 发件人邮箱密码
    # my_user = '1352040930@qq.com'  # 收件人邮箱账号
    try:
        if type(report) is dict:
            report = json.dumps(report)
        msg = MIMEText(str(report), 'plain', 'utf-8')
        msg['From'] = formataddr(["Programe errors", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(['Lance Liang', my_sender])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "wk8local程序的新bug report"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL("smtp.163.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_sender, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as e:
        print('错误信息邮件发送失败！', e)
        print('请将程序窗口截图手动发送到 LanceLiang2018@163.com 以协助程序开发。')
        print('...如果您不想发也没关系QAQ...')
        if os.environ.get('WENKU8_LOCAL', 'False') == 'True':
            input()
            exit(1)


def form_report(e):
    report = {
        'string': str(e),
        'file': e.__traceback__.tb_frame.f_globals['__file__'],
        'line': e.__traceback__.tb_lineno
    }
    return report

try:
    from database import DataBase
    _db = DataBase()
except Exception as _e:
    print("产生了无法预知的错误")
    print("错误内容如下:")
    print('初始化远程数据库时出现错误(wk8local.py)')
    _error = form_report(_e)
    print(_error['string'])
    print('文件', _error['file'])
    print('行号', _error['line'])
    print('尝试发送bug报告邮件...')
    send_report(_error)
    print('发送bug报告邮件完成，请关闭窗口。')
    if os.environ.get('WENKU8_LOCAL', 'False') == 'True':
        input()
        exit(1)


def report_it(e, _exit=False):
    print("产生了无法预知的错误")
    print("错误内容如下:")
    error = form_report(e)
    print(error['string'])
    print('文件', error['file'])
    print('行号', error['line'])
    print('正在尝试反馈错误...')
    print('尝试发送bug报告邮件...')
    send_report(error)
    print('发送bug报告邮件成功')
    try:
        print('尝试把bug发送到远程数据库...')
        _db.error_report(error)
    except Exception as e2:
        print('把bug发送到远程数据库失败')
        send_report(e2)
    print('发送bug报告完成，请关闭窗口。')
    if os.environ.get('WENKU8_LOCAL', 'False') == 'True' and _exit:
        input()
        exit(1)