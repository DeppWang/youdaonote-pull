## 使用提示

1. 脚本单纯本地运行，不用担心你的账号密码泄露
2. 默认将 note 格式笔记转换为 Markdown 格式，table 未转换，需要手动转换
3. pullAll.py 脚本采用模拟登陆方式，频繁操作会被封 ip，此时可等待几分钟或切换网络后重试
4. 如果你不是开发者，可能对下面的命令行操作有所陌生，建议按步骤慢慢操作一遍，后续我会更加完善此文档，并根据需求看是否应该提供直接下载压缩包的方式
5. 目前此脚本还没有实现有道云图床图片迁移功能
6. 有问题请提交 issue

## 使用步骤

<!--针对普通用户-->

1、导出前的准备工作

- 安装 [Git](https://git-scm.com/downloads)，打开命令行软件，如 Terminal (macOS)，clone 项目，里面包含脚本

```shell
git clone https://github.com/DeppWang/youdaonote-pull.git
cd youdaonote-pull
```

- 安装后 Python3 后安装依赖模块（包）

```shell
# macOS/Linux
sudo easy_install pip3 # 安装 Python3 Package Installer
pip3 install requests # 安装 requests 包，脚本依赖 requests
pip3 install xml.etree.ElementTree # 依赖此包转换 xml
```

```shell
# Windows
pip install requests # 安装 requests 包，脚本依赖 requests
pip install xml.etree.ElementTree # 依赖此包转换 xml

# 有问题可参考 https://www.liaoxuefeng.com/wiki/1016959663602400/1017493741106496
```

2、运行导出脚本

```shell
python3 pullAll.py <username> <password> [localDir] # macOS/Linux
python pullAll.py <username> <password> [localDir] # Windows
```

* username：**必填**，你的有道云笔记用户名
* password：**必填**，你的有道云笔记密码
* localDir：选填，本地存放导出文件的文件夹，不填则默认为当前文件夹

3、示例：

```shell
python3 pullAll.py deppwang@163.com 12345678 ~/Dropbox/youdaonote
```

4、pullAll-config

上一次输入的相关参数会保存到 `pullAll-config` 中，如果参数不变，再次导出时，可以直接输入以下命令：

```shell
python3 pullAll.py # macOS/Linux
python pullAll.py # Windows
```

再次同步时，只会导出有道云笔记上次导出后新增、修改的笔记。

## 后续开发计划

- [x] 将 Note 文件转换为 MarkDown 文件
- [ ] 解决图片不能显示问题，实现方式为上传到指定图床，再替换图片链接<!--针对普通用户，提供服务器一键下载压缩包-->
- [ ] 首次使用密码登录，再次登录时使用 cookie 登录，避免频繁操作时 ip 被封
- [ ] 并发执行加快速度

## 原理

- 使用模拟登陆有道云笔记
- 使用 [xml.etree.ElementTreeI](http://docs.python.org/3.7/library/xml.etree.elementtree.html) 得到 xml 元素

## 感谢（参考）

- [youdaonote-github](https://github.com/junzixiehui/youdaonote-github)
- [YoudaoNoteExport](https://github.com/wesley2012/YoudaoNoteExport)

## 出发点

原来一直是有道云笔记的忠实用户，后面接触到了所见即所得的 [Typora](https://typora.io/)，有点用不惯有道云笔记了，想着有什么法子能电脑本地文件和有道云笔记同步，这样电脑使用 Typora，手机使用有道云笔记。发现有道云笔记有 [Open API](http://note.youdao.com/open/developguide.html) ，打算利用提供的 API，写两个脚本，一个 pull 所有文件到本地，一个 push 本地文件到云笔记。但 API 太难用了，N 多年没更新了，问客服也没更新的意思，开发到最后发现竟然没有 Markdown 文件的接口，醉了。遂放弃。

现在我使用 Typora + [Dropbox](https://www.dropbox.com/) + [MWeb](https://www.mweb.im/) 实现同步笔记和手机查看编辑的功能，很香。

最近给朋友推荐此方式，但发现有道云笔记最新的 Mac 客户端和网页端去除了导出所有笔记的功能！这是什么逻辑，怕用户跑了么。不怕，正好我原来写了导出所有笔记的脚本。

<!--[](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150319.png)-->

<!--[](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150303.png)-->

## 导出指定文件夹

如果你可不想导出所有文件夹，你可以导出指定文件夹

1、运行脚本

```python
python3 pullAll.py <username> <password> [[localDir] [ydnoteDir]] # macOS/Linux
python pullAll.py <username> <password> [[localDir] [ydnoteDir]] # Windows
```

- ydnoteDir：有道云笔记指定导出文件夹名

2、示例

```shell
python3 pullAll.py deppwang@163.com 1234567 ~/GitHub GitHub
```

<!--3、效果-->

<!--![(https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150254.png)-->

pullAll.py 脚本采用模拟登陆方式，频繁操作会被封 ip，此时可等待几分钟后重试，若一直被封。也可使用下面这种方式

### 分享文件夹方式

1、先在有道云笔记上分享文件夹

![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150245.png)


* shareKey：必填，当前文件夹的 shareKey（分享链接（url）的 id 也是 shareKey）
* dirId：必填，分享文件夹的 id
* localDir：选填，本地文件夹名，不填则默认为当前文件夹

2、运行脚本

```shell
python3 pull.py <shareKey> <dirId> [localDir] # macOS/Linux
python pull.py <shareKey> <dirId> [localDir] # Windows
```

- localDir：选填，本地存放导出文件的文件夹，不填则默认为当前文件夹

3、示例

```shell
python3 pull.py <shareKey> WEB0868de6ab385d5f607b29e8cb13ffecc ~/GitHub # macOS
```

<!--4、效果-->

<!--!(https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150314.png)-->

5、一个问题

因为这个脚本我原来只导出 Markdown 格式笔记，经测试，导出的文件的 .note 文件不能正常打开，如果你有这方面的需求，请提 issue。

6、config

跟上面一样，上一次输入的相关参数会保存到 `config` 中，如果参数不变，再次同步时，可以直接输入以下命令：

```shell
python3 pull.py # macOS/Linux
python pull.py # Windows
```

<!--!(https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-05-17-121251.png)-->

## 