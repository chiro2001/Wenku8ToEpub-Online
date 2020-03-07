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
        $('#wenku8-board').text(d.notice);
    });
}

function wenku8Fun1() {
    var text = $('#wenku8-fun1-text').val();
    if (!(myIsNaN(text) && text.length <= 5)) {
        // 不是id
        mdui.snackbar('输入错误！请输入ID号！');
        return false;
    }
    var bid = text;
    $.ajax({
        url: '/bookinfo/' + bid
    }).then((d) => {
//        console.log(d);
//        console.log('ajax: bid:', bid, d);
        d = JSON.parse(d);
        $('#wenku8-book-card').fadeIn('slow');
        $('#wenku8-bookinfo-name').text(d.name);
        $('#wenku8-bookinfo-id').text(d.id);
        $('#wenku8-bookinfo-author').text(d.author);
        $('#wenku8-bookinfo-brief').text(d.brief);
        $('#wenku8-bookinfo-time').text(d.update_time);
//        $('#wenku8-bookinfo-cover').attr('src', d.cover);
        $('#wenku8-bookinfo-cover').empty();
        $('#wenku8-bookinfo-cover').append($('<iframe scrolling="no" frameborder=0 src="' + d.cover + '">'));
        $('#wenku8-bookinfo-cover').append($('<br>'));
        $('#wenku8-bookinfo-cover').append($('<a rel="noreferrer" target="_blank" href="' + d.cover + '">封面链接</a>'));
    })
}

function wenku8Fun1_1(val=undefined) {
    if (val == undefined)
        val = $('#wenku8-fun1-text').val()
    $('#wenku8-fun2-text').val(val);
    wenku8Fun2();
}
function wenku8Fun1_2(val=undefined) {
    if (val == undefined)
        val = $('#wenku8-fun1-text').val()
    $('#wenku8-fun3-text').val(val);
    wenku8Fun3();
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
    if (!(myIsNaN(text) && text.length <= 5)) {
        // 不是id
        target = '/v2/name/';
    }
    $.ajax({url: target + text}).then(d => {
        if (d.length <= 1) {
            mdui.snackbar('没有这个小说');
            return;
        }
        $(location).attr('href', d);
    })
}

function wenku8Fun3() {
    var bid = $('#wenku8-fun3-text').val();
    if (!(myIsNaN(bid) && bid.length <= 5)) {
        // 不是id
        mdui.snackbar('ID号输入错误')
    }
    remoteDownload(bid);
}

downloading = false;
refreshLock = false;
async function refreshDownloadLogs(bid) {
    $('#wenku8-progress').show();
    console.log('refresh:', 'update')
    if (downloading) {
        setTimeout(function() {
            refreshDownloadLogs(bid);
        }, 5000);
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
    try {
        var messages = await ajax('/v2/cache_logs/' + bid);
    } catch(e) {
        mdui.snackbar(e);
        return;
    }
//    console.log(messages);
//    messages.replace(new RegExp("\n","g"), '<br>');
    var messages = messages.split('\n').reverse();
    var text = '';
    for (m of messages) {
        text = text + m + '\n';
    }
    $('#wenku8-fun3-logs').val(text);
}

always_download = false;

async function remoteDownload(bid, img=false) {
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
    
    //转到锚点
    $('body').animate({scrollTop:$("#wenku8-fun3-logs").offset().top},1000);
    
    if (will_request) {
        target = '/v2/cache/';
        if (img == true) {
            target = '/v2/cache_img/';
        }
        var starting = await ajax(target + bid);
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
    if (!(myIsNaN(bid) && bid.length <= 5)) {
        // 不是id
        mdui.snackbar('ID号输入错误')
    }
    remoteDownload(bid, true);
}

async function search(key) {
    var results = await ajax('/v2/search/' + key);
    results = JSON.parse(results);
    $('#wenku8-search').empty();
    for (book of results) {
        console.log(book);
        var tmp = $('#wenku8-book-card-tmp').clone(true);
        tmp.show();
        
        $('.wenku8-search-title', tmp).text(book.title);
        $('.wenku8-search-id', tmp).text(book.bid);
        $('.wenku8-search-status', tmp).text(book.status);
        $('.wenku8-search-brief', tmp).text(book.brief);
        
        $('.wenku8-search-cover', tmp).empty();
        $('.wenku8-search-cover', tmp).append($('<iframe scrolling="no" frameborder=0 src="' + book.cover + '">'));
        $('.wenku8-search-cover', tmp).append($('<br>'));
        $('.wenku8-search-cover', tmp).append($('<a rel="noreferrer" target="_blank" href="' + book.cover + '">封面链接</a>'));
        
        $('.wenku8-btn-1', tmp).attr('onclick', 'wenku8Fun1_1(' + book.bid + ')');
        $('.wenku8-btn-2', tmp).attr('onclick', 'wenku8Fun1_2(' + book.bid + ')');
        $('.wenku8-btn-3', tmp).attr('onclick', 'wenku8Fun1_3(' + book.bid + ')');
        
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
    var message = $('#wenku8-feedback-message').val();
    $.post('/v2/feedback', {user:user, message:message}).then(d => {
        mdui.snackbar("感谢您的反馈");
    });
}