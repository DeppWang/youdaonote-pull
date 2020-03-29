* 两个同步有道云笔记到本地的 Python 脚本

## 使用方式
**1. 安装 Python3 环境，安装教程可参考 [廖大 Python 安装教程](https://www.liaoxuefeng.com/wiki/1016959663602400/1016959856222624)**

**2. clone 项目**
```
git clone git@github.com:DeppWang/youdaonote-pull.git
cd youdaonote-pull
```
**3. 模拟登陆的方式，同步笔记到本地**

```Python
python3 pullAll.py <username> <password> [[localDir] [ydnoteDir]] # MacOS
python pullAll.py <username> <password> [[localDir] [ydnoteDir]] # Windows
```
* username：必填，有道云笔记用户名
* password：必填，有道云笔记密码
* localDir：选填，本地文件夹名，不填则默认为当前文件夹
* ydnoteDir：选填，指定有道云笔记文件夹名，不填则默认同步所有笔记

只在本地运行，不用担心账号密码泄露，所有数据均保存在本地。上一次输入的相关参数会保存到 `pullAll-config` 中，如果参数不变，再次同步时，可以直接输入以下命令：
```Python
python3 pullAll.py # MacOS
python pullAll.py # Windows
```
注意：此种方式采用模拟登陆方式，频繁操作会被封 ip，此时可等待几分钟后重试，若一直被封。也可使用下面这种方式：

**4. 分享文件夹方式，同步文件夹下的笔记到本地**

```Python
python3 pull.py <shareKey> <dirId> [localDir] # MacOS
python pull.py <shareKey> <dirId> [localDir] # Windows
```

先在有道云笔记上分享文件夹：

![image](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150245.png)


* shareKey：必填，当前文件夹的 shareKey（分享链接的 id 也是 shareKey）
* dirId：必填，分享文件夹的 id
* localDir：选填，本地文件夹名，不填则默认为当前文件夹

同理，上一次输入的相关参数会保存到 `config` 中，如果参数不变，再次同步时，可以直接输入以下命令：
```Python
python3 pull.py # MacOS
python pull.py # Windows
```
## 效果
**1. 模拟登陆方式同步笔记到本地**

![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150254.png)

![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150303.png)

**2. 同步分享文件夹下的笔记到本地**

![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150314.png)

![](https://deppwang.oss-cn-beijing.aliyuncs.com/blog/2020-03-29-150319.png)
