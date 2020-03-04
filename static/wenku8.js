function myIsNaN(value) {
    return !isNaN(value);
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
//        $('#wenku8-bookinfo-cover').attr('src', d.cover);
        $('#wenku8-bookinfo-cover').empty();
        $('#wenku8-bookinfo-cover').append($('<iframe scrolling="no" frameborder=0 src="' + d.cover + '">'));
    })
}