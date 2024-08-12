# youdaonote-pull

现在有道云笔记不能导出笔记，迁移笔记很麻烦。此脚本可将所有笔记下载到本地。脚本完全本地运行，你不用担心数据安全。

## 功能

- 可将所有笔记（文件）按原格式下载到本地
- 由于「笔记」类型文件下载后默认为 `Xml` 或者是 `Json` 格式，不是正常笔记内容，**默认将其转换为 `Markdown` 格式**
- 由于有道云笔记图床图片不能在有道云笔记外显示，**默认将其下载到本地，或指定上传到 [SM.MS](https://sm.ms)**

## 非技术人员使用

如果你是非技术人员，也提供[可直接本地运行程序](https://github.com/DeppWang/youdaonote-pull/releases/)，不需要安装 Git、Python 和下载代码。具体使用教程请看[更简单的「有道云笔记」导出与备份](https://depp.wang/2024/simple-youdaonote-pull/)

## 使用步骤

- [视频教程](https://www.bilibili.com/video/BV11F411F7vG/?share_source=copy_web&vd_source=8bd019082f4e243f4bb5c3b6fabf4dd8)

### 一、导出前的准备工作

#### 1、安装  [Git](https://git-scm.com/downloads)、clone 项目

- 可根据 [廖雪峰 Git 教程](https://www.liaoxuefeng.com/wiki/896043488029600/896067074338496) 安装 Git，测试是否安装成功

```sh
git --version
```

- 打开命令行软件，如 Terminal (macOS)、PowerShell (Windows)，clone 项目，里面包含脚本

```shell
pwd
git clone https://github.com/DeppWang/youdaonote-pull.git
cd youdaonote-pull
```

#### 2、安装 [Python3](https://www.python.org/downloads/)、安装依赖模块（包）

- 可根据 [廖雪峰 Python 教程](https://www.liaoxuefeng.com/wiki/1016959663602400/1016959856222624) 安装，如果 pull 遇到[此错误](https://github.com/DeppWang/youdaonote-pull/issues/137)，请安装 Python 3.11.7（可使用 pyenv）， 测试是否安装成功

```shell
python3 --version  # macOS/Linux
python --version   # Windows
```

- 安装依赖包

```shell
# macOS
sudo easy_install pip3      # 安装 Python3 Package Installer
python3 -m venv venv        # 使用虚拟环境
. venv/bin/activate         # 激活虚拟环境
sudo pip3 install -r requirements.txt
```
```shell
# Windows
python -m venv venv         # 使用虚拟环境
. venv/bin/activate         # 激活虚拟环境
pip install -r requirements.txt

# 有问题可参考 https://www.liaoxuefeng.com/wiki/1016959663602400/1017493741106496
```
#### 3、设置登录 `Cookies` 文件 `cookies.json`

```json
{
    "cookies": [
        [
            "YNOTE_CSTK",
            "**",
            ".note.youdao.com",
            "/"
        ],
        [
            "YNOTE_LOGIN",
            "**",
            ".note.youdao.com",
            "/"
        ],
        [
            "YNOTE_SESS",
            "**",
            ".note.youdao.com",
            "/"
        ]
    ]
}
```

由于有道云笔记登录升级，加了图形验证吗。**目前脚本不能使用账号密码登录，只能使用 `Cookies` 登录。**

你可以通过安装插件「[Cookie-copy](https://chromewebstore.google.com/detail/cookie-copy/igfcbpdchlohbhjdfbcimhbpajlglaac?hl=zh-CN&utm_source=ext_sidebar)」快速复制 Cookie。

或者直接在浏览器 DevTools 中获取 `Cookies`：

1. 在浏览器如 Chrome 中使用账号密码或者其他方式登录有道云笔记
2. 打开 DevTools (F12)，Network 下找「主」请求（一般是第一个），再找 `Cookie`
3. 复制对应数据替换  `**`

![image.png](https://s2.loli.net/2022/04/04/N47KPEaSGvCpsfX.png)

示例：

```json
{
    "cookies": [
        [
            "YNOTE_CSTK",
            "rR_Pejz0",
            ".note.youdao.com",
            "/"
        ],
        [
            "YNOTE_LOGIN",
            "3||1649054441155",
            ".note.youdao.com",
            "/"
        ],
        [
            "YNOTE_SESS",
            "v2|BdllbnwfaWl5RMUWOfqZ0gShf***6LqFRqB0MYfh4JLR",
            ".note.youdao.com",
            "/"
        ]
    ]
}
```

- 提示：脚本完全本地运行，不用担心你的 `Cookies` 泄露

#### 4、设置脚本参数配置文件 `config.json`

建议使用 [Sublime](https://www.sublimetext.com/3) 等三方编辑器编辑 `config.json`，避免编码格式错误

```json
{
    "local_dir": "",
    "ydnote_dir": "",
    "smms_secret_token": "",
    "is_relative_path": true
}
```

* `local_dir`：选填，本地存放导出文件的文件夹（绝对路径），不填则默认为当前文件夹
* `ydnote_dir`：选填，有道云笔记指定导出文件夹名，不填则导出所有文件
* `smms_secret_token`：选填， [SM.MS](https://sm.ms) 的 `Secret Token`（注册后 -> Dashboard -> API Token），用于上传笔记中有道云图床图片到 SM.MS 图床，不填则只下载到本地（`youdaonote-images` 文件夹），`Markdown` 中使用本地链接
* `is_relative_path`：选填，在 MD 文件中图片 / 附件是否采用相对路径展示，不填或 false 为绝对路径，true 为相对路径    

示例：

- macOS

```json
{
    "local_dir": "/Users/deppwang/Documents/youdaonote-pull/test",
    "ydnote_dir": "",
    "smms_secret_token": "SGSLk9yWdTe4RenXYqEPWkqVrx0Yexample"
}
```

- Windows

```json
{
    "local_dir": "D:/Documents/youdaonote-pull/test",
    "ydnote_dir": "",
    "smms_secret_token": "SGSLk9yWdTe4RenXYqEPWkqVrx0Yexample"
}
```

###  二、运行导出脚本

```shell
python3 pull.py  # macOS/Linux
python pull.py   # Windows
```

效果：

![image-20240430154201191](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/image-20240430154201191.png)

### 三、多次导出

多次导出时，同样使用以下命令：

```shell
python3 pull.py  # macOS/Linux
python pull.py   # Windows
```

根据有道云笔记文件最后修改时间是否大于本地文件最后修改时间来判断是否需要更新。再次导出时，只会导出有道云笔记上次导出后新增、修改或未导出的笔记，不会覆盖本地已经修改的文件。**但有道云笔记和本地不要同时修改同一个文件，这样可能会导致本地修改丢失**！

更新时，会重新下载文件并覆盖原文件，图片也会重新下载。

## 注意事项

1. 如果你自己修改脚本，注意不要将 `cookies.json` 文件 `push` 到 GitHub
2. 如果你不是开发者，可能对上面的命令行操作有所陌生，建议按步骤慢慢操作一遍
3. 请确认代码是否为最新，有问题请先看 [issue](https://github.com/DeppWang/youdaonote-pull/issues?q=is%3Aissue+is%3Aclosed) 是否存在，不存在再提 issue
   ```bash
   git pull origin master  # 更新代码
   ```

## 原理

正常用户浏览器操作时，浏览器（前端）调用服务器（后端）接口，接口返回文件内容由前端渲染显示。原理是[找到有道云笔记的接口](https://depp.wang/2020/06/11/how-to-find-the-api-of-a-website-eg-note-youdao-com)，模拟操作接口，将前端显示改为存放到本地。Xml 转换为 Markdown，借助了 [xml.etree.ElementTreeI](http://docs.python.org/3.7/library/xml.etree.elementtree.html)

## 感谢（参考）

- [YoudaoNoteExport](https://github.com/wesley2012/YoudaoNoteExport)

## 出发点 

原来一直是有道云笔记的忠实用户，后面接触到了「所见即所得」的 [Typora](https://typora.io/)，有点用不惯有道云笔记了，想着有什么法子能电脑本地文件和有道云笔记同步，这样电脑使用 Typora，手机使用有道云笔记。发现有道云笔记有 [Open API](http://note.youdao.com/open/developguide.html) ，打算利用提供的 API，写两个脚本，一个 pull 所有文件到本地，一个 push 本地文件到云笔记。但 API 太难用了，N 多年没更新了，问客服也没更新的意思，开发到最后发现竟然没有 Markdown 文件的接口，醉了。遂放弃。

发现有道云笔记最新的 Mac 客户端和网页端去除了导出所有笔记的功能！这是什么逻辑，怕用户跑了么。所以在原来 pull 脚本的基础上修改得到此脚本。

现在我使用 [Obsidian](https://obsidian.md/) + iCloud + 1Writer 实现自动同步笔记和手机查看编辑的功能，很香。[使用教程](https://depp.wang/2024/my-obsidian-experience/)

## 贡献

欢迎贡献代码，但有几个注意事项：

1. commit 请使用英文；一次 commit 只改一个点；一个 commit 一个 PR
2. 代码注释需要有[中英文空格](https://github.com/sparanoid/chinese-copywriting-guidelines)
3. 请确保通过测试用例：在 macOS 和 Windows 环境中直接执行 `python3 test/test.py` 没有问题
