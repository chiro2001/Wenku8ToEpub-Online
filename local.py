import time
import webbrowser
from manage import *


def open_browser(url, sleep_time=3):
    time.sleep(sleep_time)
    webbrowser.open(url)


if __name__ == '__main__':
    # 新开一个线程，延时然后打开浏览器
    local_url = 'http://localhost:5000/'
    logger.info('5秒钟后将自动打开浏览器。')
    logger.info('使用完毕请关闭本窗口。')
    logger.info('如果打开失败请刷新浏览器或者重新输入“%s”。' % local_url)
    threading.Thread(target=open_browser, args=(local_url, 5)).start()
    app.run("0.0.0.0", port=int(os.environ.get('PORT', '5000')), debug=False)