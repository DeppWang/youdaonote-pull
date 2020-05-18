## 一、导出所有笔记

> 导出格式为原来默认的格式，如：Markdown 文件就是以 .md 结尾，笔记文件以 .note 结尾

1、导出前的准备工作

- clone 项目，里面包含脚本

```shell
git clone git@github.com:DeppWang/youdaonote-pull.git
cd youdaonote-pull
```

- macOS 使用 Homebrew 安装 Python3 环境，其他可参考 [廖大 Python 安装教程](https://www.liaoxuefeng.com/wiki/1016959663602400/1016959856222624)

```shell
brew install python3 # Homebrew 安装 python3
sudo easy_install pip3 # 安装 Python3 Package Installer
pip3 install requests # 安装 requests 包，脚本依赖 requests
```

2、运行导出脚本

```shell
python3 pullAll.py <username> <password> [localDir] # macOS
python pullAll.py <username> <password> [localDir] # Windows
```

* username：**必填**，你的有道云笔记用户名
* password：**必填**，你的有道云笔记密码
* localDir：选填，本地存放导出文件的文件夹，不填则默认为当前文件夹

3、示例：

```shell
python3 pullAll.py deppwang@163.com 1234567 ~/Dropbox/youdaonote
```

4、**两个问题**

1. 如果你笔记的类型是「笔记」，那么导出的文件后缀是 .note，你使用 [sublime](https://www.sublimetext.com/3) 打开后会发现它是一个 xml 文件。此时只能在有道云笔记手动复制粘贴，如果你有大量这种类型文档，可以提个 issue，我尝试用代码看是否能解决。ps：强烈建议使用 Markdown。
2. 你上传的图片不能显示。因为 md 文件的图片地址没有使用绝对地址，而是使用相对地址，导致图片不能正确显示。

5、pullAll-config

上一次输入的相关参数会保存到 `pullAll-config` 中，如果参数不变，再次同步时，可以直接输入以下命令：

```shell
python3 pullAll.py # macOS
python pullAll.py # Windows
```

ps：脚本单纯本地运行，不用担心你的账号密码泄露

## 二、导出指定文件夹

如果你可不想导出所有文件夹，你可以导出指定文件夹

1、运行脚本

```python
python3 pullAll.py <username> <password> [[localDir] [ydnoteDir]] # MacOS
python pullAll.py <username> <password> [[localDir] [ydnoteDir]] # Windows
```

- ydnoteDir：有道云笔记指定导出文件夹名

2、示例

```shell
python3 pullAll.py deppwang@163.com 1234567 ~/GitHub GitHub
```

3、效果

![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150254.png)

pullAll.py 脚本采用模拟登陆方式，频繁操作会被封 ip，此时可等待几分钟后重试，若一直被封。也可使用下面这种方式

### 分享文件夹方式

1、先在有道云笔记上分享文件夹

![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150245.png)


* shareKey：必填，当前文件夹的 shareKey（分享链接（url）的 id 也是 shareKey）
* dirId：必填，分享文件夹的 id
* localDir：选填，本地文件夹名，不填则默认为当前文件夹

2、运行脚本

```shell
python3 pull.py <shareKey> <dirId> [localDir] # macOS
python pull.py <shareKey> <dirId> [localDir] # Windows
```

- localDir：选填，本地存放导出文件的文件夹，不填则默认为当前文件夹

3、示例

```shell
python3 pull.py <shareKey> WEB0868de6ab385d5f607b29e8cb13ffecc ~/GitHub # macOS
```

4、效果

![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150314.png)

5、一个问题

因为这个脚本我原来只导出 Markdown 格式笔记，经测试，导出的文件的 .note 文件不能正常打开，如果你有这方面的需求，请提 issue。

6、config

跟上面一样，上一次输入的相关参数会保存到 `config` 中，如果参数不变，再次同步时，可以直接输入以下命令：

```shell
python3 pull.py # macOS
python pull.py # Windows
```

![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-05-17-121251.png)

## 三、感谢（参考）

- [youdaonote-github](https://github.com/junzixiehui/youdaonote-github)
- [YoudaoNoteExport](https://github.com/wesley2012/YoudaoNoteExport)

## 四、出发点

原来一直是有道云笔记的忠实用户，后面接触到了所见即所得的 [Typora](https://typora.io/)，有点用不惯有道云笔记了，想着有什么法子能电脑本地文件和有道云笔记同步，这样电脑使用 Typora，手机使用有道云笔记。发现有道云笔记有 [Open API](http://note.youdao.com/open/developguide.html) ，打算利用提供的 API，写两个脚本，一个 pull 所有文件到本地，一个 push 本地文件到云笔记。但 API 太难用了，N 多年没更新了，问客服也没更新的意思，开发到最后发现竟然没有 Markdown 文件的接口，醉了。遂放弃。

现在我使用 Typora + [Dropbox](https://www.dropbox.com/) + [MWeb](https://www.mweb.im/) 实现同步笔记和手机查看编辑的功能，很香。

最近给朋友推荐此方式，但发现有道云笔记最新的 Mac 客户端和网页端去除了导出所有笔记的功能！这是什么逻辑，怕用户跑了么。不怕，正好我原来写了导出所有笔记的脚本。

<!--[](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150319.png)-->

<!--[](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150303.png)-->


