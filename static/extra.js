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

function setVisitCount(data) {
    console.log('setVisitCount', data)
}

function getVisitCount() {
    var api = 'https://api.baidu.com/json/tongji/v1/ReportService/getData'
    $.ajax(api, {
        data: {
            "header": {
                "account_type": 1,
                "password": "1352040930lxR",
                "token": "b6494769824c97221e6ae94eb51423ee",
                "username": "LanceLiang2018"
            },
            "body": {
                "siteId":"14515636",
                "method": "visit/district/a",
                "start_date": "20200301",
                "end_date": "20220101",
                "metrics": "pv_count"
            }
        },
        //dataType: 'JSONP',
        //jsonpCallback: setVisitCount,
        //contentType: "application/json;charset=utf-8"
        type: 'POST'
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

getVisitCount();