wenku8_progress = $('#wenku8-progress');

function myIsNaN(value) {
    return !isNaN(value);
}

async function ajax(url) {
    return new Promise(function (resolve, reject) {
        var ajaxSetting = {
            url: url,
            success: function (response) {
                resolve(response);
            },
            error: function () {
                reject("请求失败");
            }
        }
        $.ajax(ajaxSetting);
    });
}

function showBoard() {
    $.ajax({url:'https://cdn-1254016670.cos.ap-chengdu.myqcloud.com/board/board.json'}).then(d => {
//    $.ajax({url:'/static/board.json'}).then(d => {
        console.log("news:", d);
        $('#wenku8-board').text(d.notice);
        $('#wenku8-instructions').html(d.instructions);
    });
}

function wenku8Fun1() {
    var text = $('#wenku8-fun1-text').val();
    if (text.startsWith('dmzj_')) {
        var bid = text.slice(5, text.length);
        if (!(myIsNaN(bid) && bid.length <= 5)) {
            // 不是id
            mdui.snackbar('输入错误！请输入ID号！');
            return false;
        }
        wenku8_progress.show();
        $.ajax({
            url: '/bookinfo_dmzj/' + bid
        }).then((d) => {
            wenku8_progress.hide();
            d = JSON.parse(d);
            $('#wenku8-book-card').fadeIn('slow');
            $('#wenku8-bookinfo-name').text(d.name);
            $('#wenku8-bookinfo-id').text('dmzj_' + d.id);
            $('#wenku8-bookinfo-author').text(d.authors);
            $('#wenku8-bookinfo-brief').text(d.introduction);
            $('#wenku8-bookinfo-time').text(d.update_time);
            $('#wenku8-bookinfo-copyright').text('√');
            $('#wenku8-bookinfo-cover').empty();
            $('#wenku8-bookinfo-cover').append($('<img src="' + d.cover + '" height=205px>'));
            $('#wenku8-bookinfo-cover').append($('<br>'));
            $('#wenku8-bookinfo-cover').append($('<a rel="noreferrer" target="_blank" href="' + d.cover + '">封面链接</a>'));
        })
        return;
    }
    if (!(myIsNaN(text) && text.length <= 5)) {
        // 不是id
        mdui.snackbar('输入错误！请输入ID号！');
        return false;
    }
    var bid = text;
    wenku8_progress.show();
    $.ajax({
        url: '/bookinfo/' + bid
    }).then((d) => {
        wenku8_progress.hide();
//        console.log(d);
//        console.log('ajax: bid:', bid, d);
        d = JSON.parse(d);
        $('#wenku8-book-card').fadeIn('slow');
        $('#wenku8-bookinfo-name').text(d.name);
        $('#wenku8-bookinfo-id').text(d.id);
        $('#wenku8-bookinfo-author').text(d.author);
        $('#wenku8-bookinfo-brief').text(d.brief);
        $('#wenku8-bookinfo-time').text(d.update_time);
        if (d.copyright == false) {
            $('#wenku8-bookinfo-copyright').text('无版权，可下载');
        } else {
            $('#wenku8-bookinfo-copyright').text('有版权');
        }
//        $('#wenku8-bookinfo-cover').attr('src', d.cover);
        $('#wenku8-bookinfo-cover').empty();
        $('#wenku8-bookinfo-cover').append($('<iframe scrolling="no" frameborder=0 src="' + d.cover + '">'));
        $('#wenku8-bookinfo-cover').append($('<br>'));
        $('#wenku8-bookinfo-cover').append($('<a rel="noreferrer" target="_blank" href="' + d.cover + '">封面链接</a>'));
        $('#wenku8-bookinfo-cover').append($('<a rel="noreferrer" target="_blank" href="' + 'http://dl.wenku8.com/down.php?type=txt&id=' + d.id + '&fname=' + d.name + '"> 下载TXT(GBK)</a>'));
        $('#wenku8-bookinfo-cover').append($('<a rel="noreferrer" target="_blank" href="' + 'http://dl.wenku8.com/down.php?type=utf8&id=' + d.id + '&fname=' + d.name + '"> 下载TXT(UTF8)</a>'));
    })
}

function wenku8Fun1_1(val=undefined) {
    if (val == undefined)
        val = $('#wenku8-fun1-text').val()
    $('#wenku8-fun2-text').val(val);
    wenku8Fun2();
}
function wenku8Fun1_4(val=undefined) {
    if (val == undefined)
        val = $('#wenku8-fun1-text').val()
    $('#wenku8-fun2-text').val(val);
    wenku8Fun6();
}
function wenku8Fun1_2(val=undefined) {
    if (val == undefined)
        val = $('#wenku8-fun1-text').val()
    $('#wenku8-fun3-text').val(val);
    console.log('wenku8Fun1_2:', val);
    wenku8Fun3(val);
}
function wenku8Fun1_3(val=undefined) {
    if (val == undefined)
        val = $('#wenku8-fun1-text').val()
    $('#wenku8-fun4-text').val(val);
    wenku8Fun4();
}

function wenku8Fun2() {
    var text = $('#wenku8-fun2-text').val();
    var target = '/v2/get/'
    if (text.startsWith('dmzj_')) {
        target = '/v2_dmzj/get/'
        text = text.slice(5, text.length);
    } else if (!(myIsNaN(text) && text.length <= 5)) {
        // 不是id
        target = '/v2/name/';
    }
    wenku8_progress.show();
    $.ajax({url: target + text}).then(d => {
        if (d.length <= 1) {
            mdui.snackbar('没有这个小说');
            wenku8_progress.hide();
            return;
        }
        wenku8_progress.hide();
        $(location).attr('href', d);
    })
}

function wenku8Fun3(bid=undefined) {
    if (bid == undefined)
        bid = $('#wenku8-fun3-text').val();
    console.log('wenku8Fun3()', bid);
    if ((!(myIsNaN(bid) && bid.length <= 5)) && !bid.startsWith('dmzj_')) {
        // 不是id
        mdui.snackbar('ID号输入错误')
    }
    remoteDownload(bid);
}

downloading = false;
refreshLock = false;
async function refreshDownloadLogs(bid) {
    console.log('refreshDownloadLogs(bid)', bid);
    $('#wenku8-progress').show();
    
    try {
        var messages = await ajax('/v2/cache_logs/' + bid);
    } catch(e) {
        mdui.snackbar(e);
    }
//    console.log(messages);
//    messages.replace(new RegExp("\n","g"), '<br>');
    var messages = messages.split('\n').reverse();
    var text = '';
    for (m of messages) {
        text = text + m + '\n';
    }
    $('#wenku8-fun3-logs').val(text);
    
    console.log('refresh:', 'update')
    if (downloading) {
        setTimeout(function() {
            refreshDownloadLogs(bid);
        }, 3000);
    }
    try {
        var status = await ajax('/v2/cache_status/' + bid);
    } catch(e) {
        mdui.snackbar(e);
        return;
    }
    if (status == 1) {
        downloading = false;
        $('#wenku8-progress').hide();
        return;
    }
    if (status != 0) {
        $('#wenku8-fun3-url').attr('href', status)
        $('#wenku8-fun3-url').fadeIn('slow');
        $('#wenku8-progress').hide();
        mdui.snackbar("下载已经完成，5秒后开始下载");
        downloading = false;
        setTimeout(function() {
            $(location).attr('href', status);
        }, 5000);
        return;
    }
}

always_download = false;

async function remoteDownload(bid, img=false) {
    console.log('remoteDownload', bid)
    if (downloading == true) {
        mdui.snackbar("下载已经开始");
        return;
    }
    
    if (!always_download) {
        var should = await ajax('/v2/check/' + bid);
        console.log('should:', should);
        if (should == 0) {
            // 不需要，提示
            mdui.confirm("该小说在网盘缓存已经为最新版本，是否仍然开始离线缓存？选择取消则开始下载离线缓存内容，确定则开始离线缓存。", function() {
                always_download = true;
                remoteDownload(bid, img);
            }, function() {
                wenku8Fun1_1(bid);
            });
            return;
        }
    }
    
    var will_request = true;
    
    // 先请求一下状态
    var status = await ajax('/v2/cache_status/' + bid);
    if (status == 0) {
        // 已经开始了下载
        mdui.snackbar("下载已经开始");
        // 那么就不再请求
        will_request = false;
    }
    
    // 显示进度
    $("#wenku8-fun3-logs-outline").show();
    // 转到锚点
    $('body').animate({scrollTop:$("#wenku8-fun3-logs-outline").offset().top},1000);
    
    if (will_request) {
        if (bid.startsWith('dmzj_')) {
            target = '/v2_dmzj/cache/';
            if (img == true) {
                target = '/v2_dmzj/cache_img/';
            }
        } else {
            target = '/v2/cache/';
            if (img == true) {
                target = '/v2/cache_img/';
            }
        }
        var starting = await ajax(target + bid.slice(5, bid.length));
        console.log('starting', starting)
        if (starting != 0) {
            if (starting == 1)
                mdui.snackbar("下载已经开始");
            return;
        }
    }
    downloading = true;
    mdui.snackbar("开始下载");
    refreshDownloadLogs(bid);
}

function wenku8Fun4() {
    var bid = $('#wenku8-fun4-text').val();
    if ((!(myIsNaN(bid) && bid.length <= 5)) && !bid.startsWith('dmzj_')) {
        // 不是id
        mdui.snackbar('ID号输入错误')
    }
    remoteDownload(bid, true);
}

async function search(key) {
    wenku8_progress.show();
    var results = await ajax('/v2/search/' + key);
    results = JSON.parse(results);
    $('#wenku8-search').empty();
    for (book of results) {
        console.log(book);
        var tmp = $('#wenku8-book-card-tmp').clone(true);
        tmp.show();
        tmp.addClass('wenku8-search-' + book.bid);
        
        $('.wenku8-search-title', tmp).text(book.title);
        $('.wenku8-search-id', tmp).text(book.bid);
        $('.wenku8-search-status', tmp).text(book.status);
        $('.wenku8-search-brief', tmp).text(book.brief);
        
        $('.wenku8-search-cover', tmp).empty();
        $('.wenku8-search-cover', tmp).append($('<iframe scrolling="no" frameborder=0 src="' + book.cover + '">'));
        $('.wenku8-search-cover', tmp).append($('<br>'));
        $('.wenku8-search-cover', tmp).append($('<a rel="noreferrer" target="_blank" href="' + book.cover + '">封面链接</a>'));
        $('.wenku8-search-cover', tmp).append($('<a rel="noreferrer" target="_blank" href="' + 'http://dl.wenku8.com/down.php?type=txt&id=' + book.bid + '&fname=' + book.title + '"> 下载TXT(GBK)</a>'));
        $('.wenku8-search-cover', tmp).append($('<a rel="noreferrer" target="_blank" href="' + 'http://dl.wenku8.com/down.php?type=utf8&id=' + book.bid + '&fname=' + book.title + '"> 下载TXT(UTF8)</a>'));
        
        $('.wenku8-btn-1', tmp).attr('onclick', 'wenku8Fun1_4(' + book.bid + ')');
        $('.wenku8-btn-2', tmp).attr('onclick', 'wenku8Fun1_2(' + book.bid + ')');
        $('.wenku8-btn-3', tmp).attr('onclick', 'wenku8Fun1_3(' + book.bid + ')');
        
        $('#wenku8-search').append(tmp);
        $('#wenku8-search').append($('<br>'));
    }
    var results2 = await ajax('/v2_dmzj/search/' + key);
    results2 = JSON.parse(results2);
    wenku8_progress.hide();
    if (results.length == 0 && results2.length == 0) {
        $('#wenku8-search').append($('<p>抱歉，没有搜索到相关内容。</p>'));
    }
    for (book of results2) {
        book['id'] = 'dmzj_' + book['id']
        console.log(book);
        var tmp = $('#wenku8-book-card-tmp').clone(true);
        tmp.show();
        tmp.addClass('wenku8-search-' + book.id);
        
        $('.wenku8-search-title', tmp).text(book.name);
        $('.wenku8-search-id', tmp).text(book.id);
        $('.wenku8-search-status', tmp).text(book.status + ' 作者:' + book.authors);
        $('.wenku8-search-brief', tmp).text(book.introduction);
        
        $('.wenku8-search-cover', tmp).empty();
        $('.wenku8-search-cover', tmp).append($('<img src="' + book.cover + '" height=205px>'));
        $('.wenku8-search-cover', tmp).append($('<br>'));
        $('.wenku8-search-cover', tmp).append($('<a rel="noreferrer" target="_blank" href="' + book.cover + '">封面链接</a>'));
        
        $('.wenku8-btn-1', tmp).attr('onclick', 'wenku8Fun1_4("' + book.id + '")');
        $('.wenku8-btn-2', tmp).attr('onclick', 'wenku8Fun1_2("' + book.id + '")');
        $('.wenku8-btn-3', tmp).attr('onclick', 'wenku8Fun1_3("' + book.id + '")');
        
        $('#wenku8-search').append(tmp);
        $('#wenku8-search').append($('<br>'));
    }
}

function wenku8Fun5() {
    var text = $('#wenku8-fun5-text').val();
    search(text);
}

function wenku8Feedback() {
    var user = $('#wenku8-feedback-user').val();
    var email = $('#wenku8-feedback-email').val();
    var password = $('#wenku8-feedback-password').val();
    var message = $('#wenku8-feedback-message').val();
    if (user.length == 0 || user == undefined) {
        mdui.snackbar("请至少输入您的名字");
        return;
    }
    if (message.length == 0 || message == undefined) {
        mdui.snackbar("请输入消息内容");
        return;
    }
    wenku8_progress.show();
    $.post('/v2/feedback', {user:user, message:message, email:email, password:password}).then(d => {
        wenku8_progress.hide();
        if (d == '')
            mdui.snackbar("感谢您的反馈");
        else
            mdui.snackbar(d);
        commentLoad();
    });
}

function wenku8Fun6() {
    var bid = $('#wenku8-fun2-text').val();
    ajax('/v2/check/' + bid).then(should => {
        if (should == 0) {
            wenku8Fun2();
        } else {
            always_download = true;
            console.log('wenku8Fun1_2(bid)', bid);
            wenku8Fun1_2(bid);
        }
    });
}

function wenku8ShowAdmin() {
    $('.wenku8-feedback-admin').fadeIn('slow');
}

function commentLoad() {
    ajax('/v2/comments').then(d => {
        data = JSON.parse(d);
        data = data.reverse()
//        console.log('comments:', data);
        $('.wenku8-chat-spinner').fadeOut('fast');
        var outter = $('#wenku8-chat-box-outline');
        var box = $('.wenku8-chat-box', outter);
        var chat = $('#wenku8-chat');
        $(chat).empty();
        $(chat).append(outter);
        if (data.length == 0) {
            $(chat).append($('<p>暂时没有评论。</p>'))
            return;
        }
        for (c of data) {
            var tmp = $(box).clone(true);
            $('.wenku8-chat-head', tmp).attr('src', c.head);
            $('.wenku8-chat-user', tmp).text(c.username);
            $('.wenku8-chat-message', tmp).text(c.message);
            $(chat).append(tmp);
        }
    })
}

function chatLoad(c) {
    var chat = $('#wenku8-chat2');
    if (c['user'] == 'me') {
        var tmp = $($('#wenku8-chat2-me-box-outline')).clone(true);
        $(tmp).fadeIn('slow');
        $('.wenku8-chat2-me-message', tmp).text(c.message);
        $(chat).append(tmp);
    } else {
        var tmp = $($('#wenku8-chat2-xb-box-outline')).clone(true);
        $(tmp).fadeIn('slow');
        $('.wenku8-chat2-xb-message', tmp).text(c.message);
        $(chat).append(tmp);
    }
    var div = document.getElementById('wenku8-chat2');
    div.scrollTop = div.scrollHeight;
}

function foo(d) {
    console.log(d);
//    debugger;
    var message = '';
    if (d.code == 0) {
        message = d.data;
    } else {
        message = d.other;
    }
    var c = {
        'user': 'XiaoIce',
        'message': message
    };
    chatLoad(c);
}

function wenku8Chat() {
    var message = $('#wenku8-chat-me-message').val();
    $('#wenku8-chat-me-message').val('');
    if (message.length == 0 || message == undefined) {
        mdui.snackbar("请输入消息内容");
        return;
    }
    var c = {
        'user': 'me',
        'message': message
    };
    chatLoad(c);
    wenku8_progress.show();
    $.ajax({
        url: '/chat/' + message + '?callback=foo',
        dataType :'JSONP',
        jsonp: "foo",
        jsonpCallback:"foo",
        contentType: "application/json;charset=utf-8",
        success: function (d) {
            wenku8_progress.hide();
        }
    })
//    $.post('/v2/chat', {user:user, message:message, email:email, password:password}).then(d => {
//        if (d == '')
//            mdui.snackbar("感谢您的反馈");
//        else
//            mdui.snackbar(d);
//        commentLoad();
//    });
}