#!/usr/bin/python3
# coding=utf-8

import requests
import sys
import time
import hashlib
import os
import json
import xml.etree.ElementTree as ET

__author__ = "DeppWang (deppwxq@gmail.com)"


def timestamp():
    return str(int(time.time() * 1000))


class YoudaoNoteSession(requests.Session):
    def __init__(self):
        requests.Session.__init__(self)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }

    def login(self, username, password):
        self.get('https://note.youdao.com/web/')  # 模拟打开首页
        self.headers['Referer'] = 'https://note.youdao.com/web/'

        self.get(
            'https://note.youdao.com/signIn/index.html?&callback=https%3A%2F%2Fnote.youdao.com%2Fweb%2F&from=web')  # 模拟跳转到登录页
        self.headers[
            'Referer'] = 'https://note.youdao.com/signIn/index.html?&callback=https%3A%2F%2Fnote.youdao.com%2Fweb%2F&from=web'

        self.get('https://note.youdao.com/login/acc/pe/getsess?product=YNOTE&_=' + timestamp())
        self.get('https://note.youdao.com/auth/cq.json?app=web&_=' + timestamp())
        self.get('https://note.youdao.com/auth/urs/login.json?app=web&_=' + timestamp())

        data = {
            "username": username,
            "password": hashlib.md5(password.encode('utf-8')).hexdigest()
        }
        # print(hashlib.md5(password.encode('utf-8')).hexdigest())
        self.post(
            'https://note.youdao.com/login/acc/urs/verify/check?app=web&product=YNOTE&tp=urstoken&cf=6&fr=1&systemName=&deviceType=&ru=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&er=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&vcode=&systemName=&deviceType=&timestamp=' + timestamp(),
            data=data, allow_redirects=True)  # 模拟登陆
        self.get('https://note.youdao.com/yws/mapi/user?method=get&multilevelEnable=true&_=' + timestamp())
        self.cstk = self.cookies.get('YNOTE_CSTK')

    def getAll(self, localDir, ydnoteDir):
        rootId = self.getRootId()
        try:
            os.lstat(localDir)
        except OSError:
            os.mkdir(localDir)
        if ydnoteDir is not None:
            dirId = self.getDirId(rootId, ydnoteDir)
            self.getFileRecursively(dirId, localDir)
        else:
            self.getFileRecursively(rootId, localDir)

    # 获取有道云笔记 rootId
    def getRootId(self):
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
            print('请检查账号密码是否正确；也可能因操作频繁导致 ip 被封，请切换网络或等待一段时间后重试！')
            print(response.content.decode())

    # 获取有道云笔记指定文件夹 id，目前指定文件夹只能为顶层文件夹，要指定文件夹下面的文件夹，可改用递归实现
    def getDirId(self, rootId, ydnoteDir):
        url = 'https://note.youdao.com/yws/api/personal/file/%s?all=true&f=true&len=30&sort=1&isReverse=false&method=listPageByParentId&keyfrom=web&cstk=%s' % (
            rootId, self.cstk)
        response = self.get(url)
        jsonObj = json.loads(response.content)
        for entry in jsonObj['entries']:
            fileEntry = entry['fileEntry']
            name = fileEntry['name']
            if name == ydnoteDir:
                return fileEntry['id']

    def getFileRecursively(self, id, localDir):
        url = 'https://note.youdao.com/yws/api/personal/file/%s?all=true&f=true&len=30&sort=1&isReverse=false&method=listPageByParentId&keyfrom=web&cstk=%s' % (
            id, self.cstk)
        lastId = None
        count = 0
        total = 1
        while count < total:
            if lastId is None:
                response = self.get(url)
            else:
                url = url + '&lastId=%s' % lastId
                # print(url)
                response = self.get(url)
            jsonObj = json.loads(response.content)
            total = jsonObj['count']
            for entry in jsonObj['entries']:
                fileEntry = entry['fileEntry']
                id = fileEntry['id']
                name = fileEntry['name']
                # 如果是目录，遍历目录下文件
                if fileEntry['dir']:
                    subDir = os.path.join(localDir, name)
                    try:
                        os.lstat(subDir)
                    except OSError:
                        os.mkdir(subDir)
                    self.getFileRecursively(id, subDir)
                else:
                    ## 如果文件名是网址，避免 open() 函数失败（因为目录名错误），替换 /
                    if name.startswith('https'):
                        name = name.replace('/', '_')
                        # print(name)
                    filePath = os.path.join(localDir, name)
                    if not os.path.exists(filePath):
                        self.getNote(id, filePath)
                        print('新增 %s' % (filePath))
                    else:
                        # 如果有道云笔记文件更新时间大于本地文件时间，则更新
                        if fileEntry['modifyTimeForSort'] < os.path.getmtime(filePath):
                            continue

                        print("-----------------------------")
                        print("local file modifyTime: " + str(os.path.getmtime(filePath)))
                        print("youdao file modifyTime: " + str(fileEntry['modifyTimeForSort']))

                        self.getNote(id, filePath)
                        print('更新 %s' % (filePath))
                    # 如果文件是 note 类型，将其转换为 MarkDown 类型
                    base = os.path.splitext(filePath)[0]
                    sufix = os.path.splitext(filePath)[1]
                    if sufix == ".note":
                        try:
                            self.convertXmlToMarkDown(filePath)
                            print("成功将" + filePath + "「转换为」" + base + ".md")
                        except FileNotFoundError and ET.ParseError:
                            print("转换失败！请查看文件是否为 xml 格式或是否空！")

            count = count + 1
            lastId = id

    def getNote(self, fileId, filePath):
        data = {
            'fileId': fileId,
            'version': -1,
            'convert': 'true',
            'editorType': 1,
            'cstk': self.cstk
        }
        url = 'https://note.youdao.com/yws/api/personal/sync?method=download&keyfrom=web&cstk=%s' % self.cstk
        response = self.post(url, data=data)
        with open(filePath, 'wb') as fp:
            fp.write(response.content)

    def convertXmlToMarkDown(self, filePath):
        if os.path.getsize(filePath) == 0:
            base = os.path.splitext(filePath)[0]
            os.rename(filePath, base + '.md')
            return
        # 使用 xml.etree.ElementTree 将 xml 文件转换为数组
        tree = ET.parse(filePath)
        root = tree.getroot()
        nl = '\n'
        newContent = f""
        for child in root[1]:
            if "para" in child.tag:
                for child2 in child:
                    if "text" in child2.tag:
                        if child2.text != None:
                            newContent += child2.text + f"{nl}{nl}"
                        else:
                            newContent += f"{nl}{nl}"
                        break

            elif "image" in child.tag:
                for child2 in child:
                    if "source" in child2.tag:
                        imageUrl = ""
                        if child2.text != None:
                            imageUrl = f"![%s](" + child2.text + f"){nl}{nl}"
                    elif "text" in child2.tag:
                        imageName = ""
                        if child2.text != None:
                            imageName = child2.text
                        newContent += imageUrl % (imageName)
                        break


            elif "code" in child.tag:
                for child2 in child:
                    # code = ""
                    if "text" in child2.tag:
                        code = f"```%s{nl}" + child2.text + f"{nl}```{nl}{nl}"
                    elif "language" in child2.tag:
                        language = ""
                        if language != None:
                            language = child2.text
                        newContent += code % (language)
                        break

            if "table" in child.tag:
                for child2 in child:
                    if "content" in child2.tag:
                        newContent += f"```{nl}原来为 table 需要自己转换一下{nl}" + child2.text + f"{nl}```{nl}{nl}"

        base = os.path.splitext(filePath)[0]
        newFilePath = base + '.md'
        os.rename(filePath, newFilePath)
        with open(newFilePath, 'w') as fp:
            fp.write(newContent)

if __name__ == '__main__':
    startTime = int(time.time())
    # sys.argv = ['pullAll.py']
    if len(sys.argv) >= 3:
        if len(sys.argv) == 4:
            if sys.argv[3].find('/') > -1:
                d = {'username': sys.argv[1], 'password': sys.argv[2],
                     'localDir': sys.argv[3],
                     'ydnoteDir': None}
            else:
                d = {'username': sys.argv[1], 'password': sys.argv[2],
                     'localDir': os.getcwd(),
                     'ydnoteDir': sys.argv[3]}
        else:
            d = {'username': sys.argv[1], 'password': sys.argv[2],
                 'localDir': os.getcwd() if len(sys.argv) == 3 else sys.argv[3],
                 'ydnoteDir': None if len(sys.argv) == 3 else sys.argv[4]}

        with open('pullAll-config', 'w') as fp:
            fp.write(str(d))
    else:
        with open('pullAll-config', 'r') as fp:
            dictStr = fp.read()
        d = eval(dictStr)
        if len(d) == 0:
            print('args: <username> <password> [[localDir] [ydnoteDir]]')
            sys.exit(1)

    print('正在 pull，请稍后 ....')
    sess = YoudaoNoteSession()
    sess.login(d['username'], d['password'])
    sess.getAll(d['localDir'], d['ydnoteDir'])
    endTime = int(time.time())
    print('运行完成！耗时 ' + str(endTime - startTime) + ' 秒')
