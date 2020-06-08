#!/usr/bin/python3
# coding=utf-8

import requests
import sys
import time
import hashlib
import os
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import re

# from termcolor import colored, cprint

__author__ = 'DeppWang (deppwxq@gmail.com)'
__github__ = 'https//github.com/deppwang/youdaonote-pull'


def timestamp():
    return str(int(time.time() * 1000))


def isJson(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


class YoudaoNoteSession(requests.Session):
    def __init__(self, localDir, smmsSecretToken):
        requests.Session.__init__(self)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://note.youdao.com/signIn/index.html?&callback=https%3A%2F%2Fnote.youdao.com%2Fweb%2F&from=web'
        }

        if (localDir == ''):
            localDir = os.path.join(os.getcwd(), 'youdaonote')
        self.localDir = localDir
        self.smmsSecretToken = smmsSecretToken

    def login(self, username, password) -> str:
        """模拟用户操作，使用账号密码登录，并保存 Cookie"""

        # 模拟打开首页
        self.get('https://note.youdao.com/web/')
        self.headers['Referer'] = 'https://note.youdao.com/web/'

        # 模拟跳转到登录页
        self.get(
            'https://note.youdao.com/signIn/index.html?&callback=https%3A%2F%2Fnote.youdao.com%2Fweb%2F&from=web')
        self.headers[
            'Referer'] = 'https://note.youdao.com/signIn/index.html?&callback=https%3A%2F%2Fnote.youdao.com%2Fweb%2F&from=web'

        self.get('https://note.youdao.com/login/acc/pe/getsess?product=YNOTE&_=' + timestamp())
        self.get('https://note.youdao.com/auth/cq.json?app=web&_=' + timestamp())
        self.get('https://note.youdao.com/auth/urs/login.json?app=web&_=' + timestamp())

        data = {
            'username': username,
            'password': hashlib.md5(password.encode('utf-8')).hexdigest()
        }
        # print(hashlib.md5(password.encode('utf-8')).hexdigest())
        # 模拟登陆
        self.post(
            'https://note.youdao.com/login/acc/urs/verify/check?app=web&product=YNOTE&tp=urstoken&cf=6&fr=1&systemName=&deviceType=&ru=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&er=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&vcode=&systemName=&deviceType=&timestamp=' + timestamp(),
            data=data, allow_redirects=True)

        self.get('https://note.youdao.com/yws/mapi/user?method=get&multilevelEnable=true&_=' + timestamp())

        self.cstk = self.cookies.get('YNOTE_CSTK')

        self.saveCookies()

        return self.getRootId()

    def saveCookies(self) -> None:
        """将 Cookies 保存到 cookies.json"""

        cookiesDict = {}
        cookies = []

        # requesetCookieJar 相当于是一个 Map 对象
        RequestsCookieJar = self.cookies
        for cookie in RequestsCookieJar:
            cookieEles = []
            cookieEles.append(cookie.name)
            cookieEles.append(cookie.value)
            cookieEles.append(cookie.domain)
            cookieEles.append(cookie.path)
            cookies.append(cookieEles)

        cookiesDict['cookies'] = cookies

        with open('cookies.json', 'w') as f:
            f.write(str(json.dumps(cookiesDict, indent=4, sort_keys=True)))

        print('本次使用账号密码登录，已将 Cookies 保存到 cookies.json 中，下次使用 Cookies 登录')

    def cookiesLogin(self, cookiesDict) -> str:
        """使用 Cookies 登录"""

        RequestsCookieJar = self.cookies
        for cookie in cookiesDict:
            RequestsCookieJar.set(cookie[0], cookie[1], domain=cookie[2], path=cookie[3])

        self.cstk = cookiesDict[0][1]

        print('本次使用 Cookies 登录')

        return self.getRootId()

    def getRootId(self) -> str:
        """获取有道云笔记 rootId"""

        data = {
            'path': '/',
            'entire': 'true',
            'purge': 'false',
            'cstk': self.cstk
        }
        response = self.post(
            'https://note.youdao.com/yws/api/personal/file?method=getByPath&keyfrom=web&cstk=%s' % self.cstk, data=data)
        jsonObj = json.loads(response.content)
        try:
            return jsonObj['fileEntry']['id']
        except:
            return response.content.decode('utf-8')

    def getAll(self, ydnoteDir, rootId) -> None:
        """下载所有文件"""

        # 如果指定的本地文件夹不存在，创建文件夹
        try:
            os.lstat(self.localDir)
        except OSError:
            try:
                os.mkdir(self.localDir)
            except:
                print('请检查 \"' + self.localDir + '\" 上层文件夹是否存在，并使用绝对路径！')
                print('已退出')
                sys.exit(1)

        # 有道云笔记指定导出文件夹名不为 '' 时，获取文件夹 id
        if ydnoteDir != '':
            rootId = self.getDirId(rootId, ydnoteDir)
            if rootId == None:
                print('此文件夹 ' + ydnoteDir + ' 不是顶层文件夹，暂不能下载！')
                print('已退出')
                sys.exit(1)
        self.getFileRecursively(rootId, self.localDir)

    def getDirId(self, rootId, ydnoteDir) -> str:
        """获取有道云笔记指定文件夹 id，目前指定文件夹只能为顶层文件夹，如果要指定文件夹下面的文件夹，请自己改用递归实现"""

        url = 'https://note.youdao.com/yws/api/personal/file/%s?all=true&f=true&len=30&sort=1&isReverse=false&method=listPageByParentId&keyfrom=web&cstk=%s' % (
            rootId, self.cstk)
        response = self.get(url)
        jsonObj = json.loads(response.content)
        for entry in jsonObj['entries']:
            fileEntry = entry['fileEntry']
            name = fileEntry['name']
            if name == ydnoteDir:
                return fileEntry['id']

    def getFileRecursively(self, id, localDir) -> None:
        """递归遍历，找到文件夹下的所有文件"""

        url = 'https://note.youdao.com/yws/api/personal/file/%s?all=true&f=true&len=30&sort=1&isReverse=false&method=listPageByParentId&keyfrom=web&cstk=%s' % (
            id, self.cstk)
        lastId = None
        count = 0
        total = 1
        while count < total:
            if lastId is not None:
                url = url + '&lastId=%s' % lastId
                # print(url)
            response = self.get(url)
            jsonObj = json.loads(response.content)
            total = jsonObj['count']
            for entry in jsonObj['entries']:
                fileEntry = entry['fileEntry']
                id = fileEntry['id']
                name = fileEntry['name']
                # 如果是目录，继续遍历目录下文件
                if fileEntry['dir']:
                    subDir = os.path.join(localDir, name)
                    try:
                        os.lstat(subDir)
                    except OSError:
                        os.mkdir(subDir)
                    self.getFileRecursively(id, subDir)
                else:
                    self.judgeAddOrUpdate(id, name, localDir, fileEntry)

            count = count + 1
            lastId = id

    def judgeAddOrUpdate(self, id, name, localDir, fileEntry) -> None:
        """判断是新增还是更新"""

        # 如果文件名是网址，避免 open() 函数失败（因为目录名错误），替换 /
        if name.startswith('https'):
            name = name.replace('/', '_')
            # print(name)

        nameText = os.path.splitext(name)[0]  # 有道云笔记名称
        youdaoFileSuffix = os.path.splitext(name)[1]  # 笔记后缀
        localFilePath = os.path.join(localDir, name)  # 用于将后缀 .note 转换为 .md
        originalFilePath = os.path.join(localDir, name)  # 保留本身后缀
        localFileName = os.path.join(localDir, nameText)  # 没有后缀的本地文件
        tip = youdaoFileSuffix
        # 本地 .note 文件均为 .md，使用 .md 后缀判断是否在本地存在
        if youdaoFileSuffix == '.note':
            tip = '.md ，「云笔记原格式为 .note」'
            localFilePath = localFileName + '.md'
        # 如果不存在，则更新
        if not os.path.exists(localFilePath):
            self.getFile(id, originalFilePath, youdaoFileSuffix)
            print('新增 %s%s' % (localFileName, tip))
        # 如果已经存在，判断是否需要更新
        else:
            # 如果有道云笔记文件更新时间小于本地文件时间，说明没有更新。跳过本地更新步骤
            if fileEntry['modifyTimeForSort'] < os.path.getmtime(localFilePath):
                # print('正在遍历，请稍后 ...，最好一行动态变化')
                return

            print('-----------------------------')
            print('local file modifyTime: ' + str(int(os.path.getmtime(localFilePath))))
            print('youdao file modifyTime: ' + str(fileEntry['modifyTimeForSort']))
            self.getFile(id, originalFilePath, youdaoFileSuffix)
            print('更新 %s%s' % (localFileName, tip))

    def getFile(self, fileId, filePath, youdaoFileSuffix) -> None:
        """下载文件。先不管什么文件，均下载。如果是 .note 类型，转换为 Markdown"""

        data = {
            'fileId': fileId,
            'version': -1,
            'convert': 'true',
            'editorType': 1,
            'cstk': self.cstk
        }
        url = 'https://note.youdao.com/yws/api/personal/sync?method=download&keyfrom=web&cstk=%s' % self.cstk
        response = self.post(url, data=data)

        if youdaoFileSuffix == '.md':
            content = response.content.decode('utf-8')

            content = self.convertMarkdownFileImageUrl(content, filePath)
            try:
                with open(filePath, 'wb') as fp:
                    fp.write(content.encode())
            except UnicodeEncodeError as err:
                print(format(err))
            return

        with open(filePath, 'wb') as fp:
            fp.write(response.content)

        # 权限问题，导致下载内容为接口错误提醒值。contentStr = response.content.decode('utf-8')

        # 如果文件是 .note 类型，将其转换为 MarkDown 类型
        if youdaoFileSuffix == '.note':
            try:
                self.convertXmlToMarkDown(filePath)
            except FileNotFoundError and ET.ParseError:
                print(filePath + ' 转换失败！请查看文件是否为 xml 格式或是否空！')

    def convertXmlToMarkDown(self, filePath) -> None:
        """转换 xml 为 Markdown"""

        # 如果文件为 null，结束
        if os.path.getsize(filePath) == 0:
            base = os.path.splitext(filePath)[0]
            os.rename(filePath, base + '.md')
            return
        # 使用 xml.etree.ElementTree 将 xml 文件转换为多维数组
        tree = ET.parse(filePath)
        root = tree.getroot()
        flag = 0  # 用于输出转换提示
        nl = '\r\n'  # Windows 系统换行符为 \r\n
        newContent = f''  # f-string 多行字符串
        # 得到多维数组中的文本，因为是数组，不是对象，所以只能遍历
        for child in root[1]:
            if 'para' in child.tag:
                for child2 in child:
                    if 'text' in child2.tag:
                        # 如果等于 None，字符串加 None 将报错
                        if child2.text == None:
                            child2.text = ''
                        newContent += child2.text + f'{nl}{nl}'
                        break

            elif 'image' in child.tag:
                if flag == 0:
                    self.getYdnoteDirName(filePath)

                for child2 in child:
                    if 'source' in child2.tag:
                        imageUrl = ''
                        if child2.text != None:
                            imageUrl = f'![%s](' + self.getNewDownOrUploadUrl(child2.text) + f'){nl}{nl}'
                            flag += 1

                    elif 'text' in child2.tag:
                        imageName = ''
                        if child2.text != None:
                            imageName = child2.text
                        newContent += imageUrl % (imageName)
                        break

            elif 'code' in child.tag:
                for child2 in child:
                    if 'text' in child2.tag:
                        code = f'```%s{nl}' + child2.text + f'{nl}```{nl}{nl}'
                    elif 'language' in child2.tag:
                        language = ''
                        if language != None:
                            language = child2.text
                        newContent += code % (language)
                        break

            elif 'table' in child.tag:
                for child2 in child:
                    if 'content' in child2.tag:
                        newContent += f'```{nl}原来为 table，需要自己转换一下{nl}' + child2.text + f'{nl}```{nl}{nl}'

        base = os.path.splitext(filePath)[0]
        newFilePath = base + '.md'
        os.rename(filePath, newFilePath)
        with open(newFilePath, 'w') as fp:
            fp.write(newContent)

    def convertMarkdownFileImageUrl(self, content, filePath) -> str:
        """将 Markdown 中的有道云图床图片转换为 sm.ms 图床"""

        reg = r'!\[.*?\]\((.*?note\.youdao\.com.*?)\)'
        p = re.compile(reg)
        urls = p.findall(content)
        if len(urls) > 0:
            self.getYdnoteDirName(filePath)
        for url in urls:
            newUrl = self.getNewDownOrUploadUrl(url)
            content = content.replace(url, newUrl)
        return content

    def getYdnoteDirName(self, filePath):

        ydnoteDirName = filePath.replace(self.localDir, '')
        print('正在转换有道云笔记「' + ydnoteDirName + '」中的有道云图床图片链接...')

    def getNewDownOrUploadUrl(self, url) -> str:
        """根据是否存在 smmsSecretToken 判断是否需要上传到 sm.ms """

        if 'note.youdao.com' not in url:
            return url
        if self.smmsSecretToken == '':
            return self.downloadImage(url)
        return self.uploadToSmms(url, self.smmsSecretToken)

    def downloadImage(self, url) -> str:
        """如果 smmsSecretToken 为 null，将其下载到本地，返回相对 url"""

        response = self.get(url)
        if (response.status_code != 200):
            print('下载 ' + url + ' 失败！请登录网页版有道云笔记，查看图片是否能正常显示')
            return url

        try:
            localImageDir = os.path.join(self.localDir, 'youdaonote-images')
            os.lstat(localImageDir)
        except:
            os.mkdir(localImageDir)
        imageName = os.path.basename(urlparse(url).path)
        imagePath = os.path.join(localImageDir, imageName + '.' + response.headers['Content-Type'].split('/')[1])
        try:
            with open(imagePath, 'wb') as f:
                f.write(response.content)
            print('已将图片 ' + url + ' 转换为 ' + imagePath)
        except:
            print(url + ' 图片有误！')
            return url
        return imagePath

    def uploadToSmms(self, oldUrl, smmsSecretToken) -> str:
        smmsUploadApi = 'https://sm.ms/api/v2/upload'
        headers = {'Authorization': smmsSecretToken}
        url = oldUrl
        try:
            smfile = self.get(oldUrl).content
        except:
            print('下载 ' + oldUrl + ' 失败！请登录网页版有道云笔记，查看图片是否能正常显示')
            return url
        files = {'smfile': smfile}

        try:
            res = requests.post(smmsUploadApi, headers=headers, files=files)
        except requests.exceptions.ProxyError as err:
            print('上传 ' + oldUrl + '到 SM.MS 失败！')
            print(format(err))
            return url

        resJson = res.json()

        if (resJson['success'] == False):
            if resJson['code'] == 'image_repeated':
                url = resJson['images']
            elif resJson['code'] == 'flood':
                print('每小时只能上传 100 张图片，' + url + ' 未转换')
                return url
            else:
                print('上传 ' + oldUrl + ' 到 SM.MS 失败，请检查图片 url 或 smmsSecretToken（' + smmsSecretToken + '）是否正确！')
                return url

        if resJson['success'] == True:
            url = resJson['data']['url']
        print('已将图片 ' + oldUrl + ' 转换为 ' + url)
        return url


if __name__ == '__main__':
    startTime = int(time.time())
    with open('config.json', 'r') as fp:
        configStr = fp.read()

    try:
        # 将字符串转换为字典
        configDict = eval(configStr)
    except:
        print('请检查 config.json 格式是否正确！')
        print('已退出')
        sys.exit(1)

    if (configDict['username'] == '' or configDict['password'] == ''):
        print('账号密码不能为空，请检查！')
        print('已退出')
        sys.exit(1)

    print('正在 pull，请稍后 ...')

    session = YoudaoNoteSession(configDict['localDir'], configDict['smmsSecretToken'])

    with open('cookies.json', 'r') as fp:
        cookiesStr = fp.read()
    try:
        cookiesDict = eval(cookiesStr)
    except:
        print('cookies.json 格式错误，请恢复为默认格式！')
        print('已退出')
        sys.exit(1)

    if (len(cookiesDict.get('cookies')) != 0):
        rootId = session.cookiesLogin(cookiesDict['cookies'])
        # 如果 cookies 过期等原因导致 cookies 登录失败，改用使用账号密码登录
        if (isJson(rootId)):
            rootId = session.login(configDict['username'], configDict['password'])
    else:
        rootId = session.login(configDict['username'], configDict['password'])

    if (isJson(rootId)):
        print('请检查账号密码是否正确；也可能因操作频繁导致 ip 被封，请切换网络或等待一段时间后重试！')
        # print('接口返回值：')
        parsed = json.loads(rootId)
        print(json.dumps(parsed, indent=4, sort_keys=True))
        print('已退出')
        sys.exit(1)

    session.getAll(configDict['ydnoteDir'], rootId)

    endTime = int(time.time())
    print('运行完成！耗时 ' + str(endTime - startTime) + ' 秒')
