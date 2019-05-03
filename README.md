### 使用的插件的说明

```
把www.wenku8.net的轻小说在线转换成epub格式。

wk2epub [-h] [-t] [list]

    list            一个数字列表，中间用空格隔开
    
    -t              Text only.
                    只获取文字，忽略图片。
                    但是图像远程连接仍然保留在文中。
                    此开关默认关闭，即默认获取图片。
                    
    -h              Help.
                    显示本帮助。

调用示例:
    wk2epub -t 1 1213

关于:
    https://github.com/LanceLiang2018/Wenku8ToEpub

版本:
    2019/4/5 2:51 AM
```

### 文件下载方式

#### 方式1

[书名形式](https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/小说标题.epub)

小说标题以显示在wenku8网站上的为准，例如

    TIGER×DRAGON！(龙与虎)

示例:

[文学少女](https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/文学少女.epub)

#### 方式2

[ID形式](https://light-novel-1254016670.cos.ap-guangzhou.myqcloud.com/小说ID.html)

    注意等待静态HTML跳转

## 更新：服务器版

- 从缓存中获取。存在此书则直接重定向到下载链接。

    https://wenku8.herokuapp.com/get/书本id

- 更新CDN缓存。更新完成后就会重定向到下载链接，请耐心等候。小书5s，大书30s以上。

    https://wenku8.herokuapp.com/cache/书本id
 