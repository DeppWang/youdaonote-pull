#!/usr/bin/python3
# coding=utf-8


import requests
import sys
import time
import os
import json

__author__ = "DeppWang (deppwxq@gmail.com)"


class YoudaoNotePull:
    def __init__(self, shareKey):
        self.shareKey = shareKey

    def getFileRecursively(self, dirId, localDir):

        url = 'https://note.youdao.com/yws/public/notebook/%s/subdir/%s?cstk=null' % (self.shareKey, dirId)
        response = requests.get(url)
        if response.status_code != 200:
            print('请检查 shareKey 和 dirId 是否正确！')
            sys.exit(1)
        jsonArray = json.loads(response.content)
        for jsonObj in jsonArray:
            if isinstance(jsonObj, list):
                for fileEntry in jsonObj:
                    name = fileEntry['tl']
                    ids = fileEntry['p'].split('/')
                    if len(ids) == 2:
                        dir = os.path.join(localDir, name)
                        try:
                            os.lstat(dir)
                        except OSError:
                            os.mkdir(dir)
                        self.getFileRecursively(ids[1], dir)
                    else:
                        localPath = os.path.join(localDir, name)
                        if not os.path.exists(localPath):
                            self.getNote(ids[2], localPath)
                            print('新增 %s' % (localPath))
                        else:
                            if os.path.getsize(localPath) == fileEntry['sz']:
                                continue
                            self.getNote(ids[2], localPath)
                            print('更新 %s' % (localPath))

    def getNote(self, fileId, localPath):
        url = 'https://note.youdao.com/yws/api/personal/file/%s?method=download&read=true&shareKey=%s&cstk=null' % (
            fileId, self.shareKey)
        response = requests.get(url)
        with open(localPath, 'wb') as fp:
            fp.write(response.content)


if __name__ == '__main__':

    startTime = int(time.time())
    if len(sys.argv) >= 3:
        d = {'shareKey': sys.argv[1], 'dirId': sys.argv[2], 'localDir': os.getcwd() if len(sys.argv) == 3 else sys.argv[3]}
        with open('config', 'w') as fp:
            fp.write(str(d))
    else:
        with open('config', 'r') as fp:
            dictStr = fp.read()
        d = eval(dictStr)
        if len(d) == 0:
            print('args: <shareKey> <dirId> [localDir]')
            sys.exit(1)

    print('正在 pull，请稍后 ....')
    client = YoudaoNotePull(d['shareKey'])
    client.getFileRecursively(d['dirId'], d['localDir'])
    endTime = int(time.time())
    print('运行完成！耗时 ' + str(endTime - startTime) + ' 秒')
