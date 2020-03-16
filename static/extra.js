console.log('EXTRA JAVASCRIPT LOADED!')

function check_local() {
    return window.location.port == '' ? false : true;
}

function local_action() {
    $.ajax({url:'https://cdn-1254016670.cos.ap-chengdu.myqcloud.com/board/board.json'}).then(d => {
        if (window.location.port < d.local_latest) {
            // 有版本更新！
            document.write('<p>You are a local user! port = ' + window.location.port + '</p>')
            document.write('<p>请更新本地软件到最新版本(' + d.local_latest + ')：</p>')
            document.write('<a href="https://static-1254016670.cos.ap-chengdu.myqcloud.com/wk8local.exe">下载最新版本</a>')
        }
    });
}

if (check_local()) {
    local_action()
}

(function(){
    var bp = document.createElement('script');
    var curProtocol = window.location.protocol.split(':')[0];
    if (curProtocol === 'https') {
        bp.src = 'https://zz.bdstatic.com/linksubmit/push.js';
    }
    else {
        bp.src = 'http://push.zhanzhang.baidu.com/push.js';
    }
    var s = document.getElementsByTagName("script")[0];
    s.parentNode.insertBefore(bp, s);
})();