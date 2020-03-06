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
        $('#wenku8-bookinfo-cover').append($('<a rel="noreferrer" href="' + d.cover + '">封面链接</a>'));
    })
}

function wenku8Fun1_1() {
    $('#wenku8-fun2-text').val($('#wenku8-fun1-text').val());
    wenku8Fun2();
}
function wenku8Fun1_2() {
    $('#wenku8-fun3-text').val($('#wenku8-fun1-text').val());
    wenku8Fun3();
}
function wenku8Fun1_3() {
    $('#wenku8-fun4-text').val($('#wenku8-fun1-text').val());
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
    messages.replace(new RegExp("\n","g"), '<br>');
    $('#wenku8-fun3-logs').html(messages);
}

async function remoteDownload(bid, img=false) {
    if (downloading == true) {
        mdui.snackbar("下载已经开始");
        return;
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
