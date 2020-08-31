#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sys
import time
import hashlib
import os
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import re
import logging
from markdownify import markdownify as md

# logging.basicConfig(level=logging.INFO)

__author__ = 'Depp Wang (deppwxq@gmail.com)'
__github__ = 'https//github.com/DeppWang/youdaonote-pull'


def timestamp() -> str:
    return str(int(time.time() * 1000))


def check_config(config_name) -> dict:
    """ 检查 config.json 文件格式 """

    with open(config_name, 'rb') as f:
        config_str = f.read().decode('utf-8')
        logging.info('config_str 格式：\n %s', config_str)

    try:
        # 将字符串转换为字典
        config_dict = eval(config_str)
    except SyntaxError:
        raise SyntaxError('请检查「config.json」格式是否为 utf-8 的 json！建议使用 Sublime 编辑「config.json」')

    # 如果某个 key 不存在，抛出异常
    try:
        username = config_dict['username']
        config_dict['password']
        config_dict['local_dir']
        config_dict['ydnote_dir']
        config_dict['smms_secret_token']
    except KeyError:
        raise KeyError('请检查「config.json」的 key 是否分别为 username, password, local_dir, ydnote_dir, smms_secret_token')

    if config_dict['username'] == '' or config_dict['password'] == '':
        raise ValueError('账号密码不能为空，请检查「config.json」！')

    return config_dict


def covert_cookies(file_name) -> list:
    if not os.path.exists(file_name):
        logging.info('%s is null', file_name)
        raise OSError(file_name + ' 不存在')

    with open(file_name, 'r', encoding='utf-8') as f:
        json_str = f.read()

    try:
        # 将字符串转换为字典
        cookies_dict = eval(json_str)
        cookies = cookies_dict['cookies']
    except Exception:
        raise Exception('转换「' + file_name + '」为字典时出现错误')
    return cookies


class LoginError(ValueError):
    pass


class YoudaoNoteSession(requests.Session):
    """ 继承于 requests.Session，能像浏览器一样，完成一个完整的 Session 操作"""

    # 类变量，不随着对象改变
    WEB_URL = 'https://note.youdao.com/web/'
    SIGN_IN_URL = 'https://note.youdao.com/signIn/index.html?&callback=https%3A%2F%2Fnote.youdao.com%2Fweb%2F&from=web'  # 浏览器在传输链接的过程中是否都将符号转换为 Unicode？
    LOGIN_URL = 'https://note.youdao.com/login/acc/urs/verify/check?app=web&product=YNOTE&tp=urstoken&cf=6&fr=1&systemName=&deviceType=&ru=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&er=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&vcode=&systemName=&deviceType=&timestamp='
    COOKIE_URL = 'https://note.youdao.com/yws/mapi/user?method=get&multilevelEnable=true&_=%s'
    ROOT_ID_URL = 'https://note.youdao.com/yws/api/personal/file?method=getByPath&keyfrom=web&cstk=%s'
    DIR_MES_URL = 'https://note.youdao.com/yws/api/personal/file/%s?all=true&f=true&len=30&sort=1&isReverse=false&method=listPageByParentId&keyfrom=web&cstk=%s'
    FILE_URL = 'https://note.youdao.com/yws/api/personal/sync?method=download&keyfrom=web&cstk=%s'

    # 莫有类方法

    def __init__(self):

        # 使用父类的构造函数初始化 self
        requests.Session.__init__(self)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

        # 属于对象变量
        self.cstk = None
        self.local_dir = None
        self.smms_secret_token = None

    def check_and_login(self, username, password) -> str:
        try:
            cookies = covert_cookies('cookies.json')
        except Exception as err:
            logging.info('covert_cookies error: %s', format(err))
            cookies = None

        # 如果 cookies 不为 null，使用 cookies 登录
        if cookies is not None:
            # 如果 Cookies 被修改或过期等原因导致 Cookies 登录失败，改用使用账号密码登录
            try:
                root_id = self.cookies_login(cookies)
                print('本次使用 Cookies 登录')
            except KeyError as err:
                logging.info('cookie 登录出错：%s', format(err))
                root_id = self.login(username, password)
                print('本次使用账号密码登录，已将 Cookies 保存到「cookies.json」中，下次使用 Cookies 登录')
        else:
            root_id = self.login(username, password)
            print('本次使用账号密码登录，已将 Cookies 保存到「cookies.json」中，下次使用 Cookies 登录')

        return root_id

    def login(self, username, password) -> str:
        """ 模拟浏览器用户操作，使用账号密码登录，并保存 Cookie """

        # 模拟打开网页版
        self.get(self.WEB_URL)
        # 模拟设置上一步链接
        self.headers['Referer'] = self.WEB_URL
        # 模拟重定向跳转到登录页
        self.get(self.SIGN_IN_URL)
        # 模拟设置上一步链接
        self.headers['Referer'] = self.SIGN_IN_URL
        # 模拟跳转到登录页后的请求连接
        self.get('https://note.youdao.com/login/acc/pe/getsess?product=YNOTE&_=%s' % timestamp())
        self.get('https://note.youdao.com/auth/cq.json?app=web&_=%s' % timestamp())
        self.get('https://note.youdao.com/auth/urs/login.json?app=web&_=%s' % timestamp())

        data = {
            'username': username,
            'password': hashlib.md5(password.encode('utf-8')).hexdigest()
        }

        logging.info('cookies: %s', self.cookies)

        # 模拟登陆
        self.post(self.LOGIN_URL,
                  data=data, allow_redirects=True)

        # 登录成功后的链接，里面包含可用于登录的最新 Cookie: YNOTE_CSTK
        self.get(self.COOKIE_URL % timestamp())

        logging.info('new cookies: %s', self.cookies)

        # 设置 cookies
        cstk = self.cookies.get('YNOTE_CSTK')

        if cstk is None:
            logging.info('cstk: %s', cstk)
            raise LoginError('请检查账号密码是否正确！也可能因操作频繁导致需要验证码，请切换网络（改变 ip）或等待一段时间后重试！')

        self.cstk = cstk

        self.save_cookies()

        return self.get_root_id()

    def save_cookies(self) -> None:
        """ 将 Cookies 保存到 cookies.json """

        cookies_dict = {}
        cookies = []

        # cookiejar 为 RequestsCookieJar，相当于是一个 Map 对象
        cookiejar = self.cookies
        for cookie in cookiejar:
            cookie_eles = [cookie.name, cookie.value, cookie.domain, cookie.path]
            cookies.append(cookie_eles)

        cookies_dict['cookies'] = cookies

        with open('cookies.json', 'wb') as f:
            f.write(str(json.dumps(cookies_dict, indent=4, sort_keys=True)).encode())

    def cookies_login(self, cookies_dict) -> str:
        """ 使用 Cookies 登录，其实就是设置 cookies """

        cookiejar = self.cookies
        for cookie in cookies_dict:
            cookiejar.set(cookie[0], cookie[1], domain=cookie[2], path=cookie[3])

        self.cstk = cookies_dict[0][1]

        return self.get_root_id()

    def get_root_id(self) -> str:
        """
        获取有道云笔记 root_id
        root_id 始终不会改变？可保存？可能会改变，几率很小。可以保存，保存又会带来新的复杂度。只要登录后，获取一下也没有影响
        """

        data = {
            'path': '/',
            'entire': 'true',
            'purge': 'false',
            'cstk': self.cstk
        }
        response = self.post(self.ROOT_ID_URL % self.cstk, data=data)
        json_obj = json.loads(response.content)
        try:
            return json_obj['fileEntry']['id']
        # Cookie 登录时可能错误
        except KeyError:
            raise KeyError('Cookie 中没有 cstk')
            # parsed = json.loads(response.content.decode('utf-8'))
            # raise LoginError('请检查账号密码是否正确！也可能因操作频繁导致需要验证码，请切换网络（改变 ip）或等待一段时间后重试！接口返回内容：',
            #                  json.dumps(parsed, indent=4, sort_keys=True))

    def get_all(self, local_dir, ydnote_dir, smms_secret_token, root_id) -> None:
        """ 下载所有文件 """

        # 如果本地为指定文件夹，下载到当前路径的 youdaonote 文件夹中
        if local_dir == '':
            local_dir = os.path.join(os.getcwd(), 'youdaonote')

        # 如果指定的本地文件夹不存在，创建文件夹
        if not os.path.exists(local_dir):
            try:
                os.mkdir(local_dir)
            except FileNotFoundError:
                raise FileNotFoundError('请检查「%s」上层文件夹是否存在，并使用绝对路径！' % local_dir)

        # 有道云笔记指定导出文件夹名不为 '' 时，获取文件夹 id
        if ydnote_dir != '':
            root_id = self.get_dir_id(root_id, ydnote_dir)
            logging.info('root_id: %s', root_id)
            if root_id is None:
                raise ValueError('此文件夹「%s」不是顶层文件夹，暂不能下载！' % ydnote_dir)

        self.local_dir = local_dir  # 此处设置，后面会用，避免传参
        self.smms_secret_token = smms_secret_token  # 此处设置，后面会用，避免传参
        self.get_file_recursively(root_id, local_dir)

    def get_dir_id(self, root_id, ydnote_dir) -> str:
        """ 获取有道云笔记指定文件夹 id，目前指定文件夹只能为顶层文件夹，如果要指定文件夹下面的文件夹，请自己改用递归实现 """

        url = self.DIR_MES_URL % (root_id, self.cstk)
        response = self.get(url)
        json_obj = json.loads(response.content)
        try:
            entries = json_obj['entries']
        except KeyError:
            raise KeyError('有道云笔记修改了接口地址，此脚本暂时不能使用！请提 issue')

        for entry in entries:
            file_entry = entry['fileEntry']
            name = file_entry['name']
            if name == ydnote_dir:
                return file_entry['id']

    def get_file_recursively(self, id, local_dir) -> None:
        """ 递归遍历，根据 id 找到目录下的所有文件 """

        url = self.DIR_MES_URL % (id, self.cstk)

        response = self.get(url)
        json_obj = json.loads(response.content)

        try:
            json_obj['count']
        # 如果 json_obj 不是 json，退出
        except KeyError:
            logging.info('json_obj: %s', json_obj)
            raise KeyError('有道云笔记修改了接口地址，此脚本暂时不能使用！请提 issue')

        for entry in json_obj['entries']:
            file_entry = entry['fileEntry']
            id = file_entry['id']
            name = file_entry['name']
            logging.info('name: %s', name)
            # 如果是目录，继续遍历目录下文件
            if file_entry['dir']:
                sub_dir = os.path.join(local_dir, name)
                if not os.path.exists(sub_dir):
                    os.mkdir(sub_dir)
                self.get_file_recursively(id, sub_dir)
            else:
                self.judge_add_or_update(id, name, local_dir, file_entry)

    def judge_add_or_update(self, id, name, local_dir, file_entry) -> None:
        """ 判断是新增还是更新 """

        name = self.optimize_name(name)

        youdao_file_suffix = os.path.splitext(name)[1]  # 笔记后缀
        local_file_path = os.path.join(local_dir, name)  # 用于将后缀 .note 转换为 .md
        original_file_path = os.path.join(local_dir, name)  # 保留本身后缀

        tip = ''

        # 如果有有道云笔记是「笔记」类型，则设置提示类型
        if youdao_file_suffix == '.note':
            tip = '，云笔记原格式为 .note'
            local_file_basename = os.path.join(local_dir, os.path.splitext(name)[0])  # 没有后缀的本地文件
            # 使用 .md 后缀判断是否在本地存在
            local_file_path = local_file_basename + '.md'

        # 如果不存在，则下载
        if not os.path.exists(local_file_path):
            try:
                self.get_file(id, original_file_path, youdao_file_suffix)
                print('新增「%s」%s' % (local_file_path, tip))
            except Exception as error:
                print('「%s」转换为 Markdown 失败！请检查文件！' % original_file_path)
                print('错误提示：%s' % format(error))

        # 如果已经存在，判断是否需要更新
        else:
            # 如果有道云笔记文件更新时间小于本地文件时间，说明没有更新。跳过本地更新步骤
            if file_entry['modifyTimeForSort'] < os.path.getmtime(local_file_path):
                # print('此文件不更新，跳过 ...，最好一行动态变化')
                logging.info('此文件「%s」不更新，跳过', local_file_path)
                return

            print('-----------------------------')
            print('local file modifyTime: ' + str(int(os.path.getmtime(local_file_path))))
            print('youdao file modifyTime: ' + str(file_entry['modifyTimeForSort']))
            try:
                # 考虑到使用 f.write() 直接覆盖原文件，在 Windows 下报错（WinError 183），先将其删除
                if os.path.exists(local_file_path):
                    os.remove(local_file_path)
                self.get_file(id, original_file_path, youdao_file_suffix)
                print('更新「%s」%s' % (local_file_path, tip))
            except Exception as error:
                print('「%s」转换为 Markdown 失败！请检查文件！' % original_file_path)
                print('错误提示：%s' % format(error))

    def optimize_name(self, name):
        """ 避免 open() 函数失败（因为目录名错误），修改文件名 """

        regex = re.compile(r'[\\/:\*\?"<>\|]')  # 替换 \ / : * ? " < > | 为 _
        name = regex.sub('_', name)
        return name

    def get_file(self, file_id, file_path, youdao_file_suffix) -> None:
        """ 下载文件。先不管什么类型文件，均下载。如果是 .note 类型，转换为 Markdown """

        data = {
            'fileId': file_id,
            'version': -1,
            'convert': 'true',
            'editorType': 1,
            'cstk': self.cstk
        }
        url = self.FILE_URL % self.cstk
        response = self.post(url, data=data)

        # 权限问题，导致下载内容为接口错误提醒值。contentStr = response.content.decode('utf-8')
        # 如果登录失败，是否会走到这个方法？不会走到这个方法，前面将中断
        # if is_json(response.content):
        #     pares = json.loads(response)

        if youdao_file_suffix == '.md':
            content = response.content.decode('utf-8')

            content = self.covert_markdown_file_image_url(content, file_path)
            try:
                with open(file_path, 'wb') as f:
                    f.write(content.encode())
            except UnicodeEncodeError as err:
                print('错误提示：%s' % format(err))
            return

        with open(file_path, 'wb') as f:
            f.write(response.content)  # response.content 本身就是字节类型

        # 如果文件是 .note 类型，将其转换为 MarkDown 类型
        if youdao_file_suffix == '.note':
            try:
                self.covert_xml_to_markdown(file_path)
            except ET.ParseError:
                print('此 note 笔记应该为 17 年以前新建，格式为 html，将转换为 Markdown')
                base = os.path.splitext(file_path)[0]
                new_file_path = base + '.md'
                os.rename(file_path, new_file_path)
                self.covert_html_to_markdown(file_path)

    def covert_xml_to_markdown(self, file_path) -> None:
        """ 转换 xml 为 Markdown """

        # 如果文件为 null，结束
        if os.path.getsize(file_path) == 0:
            base = os.path.splitext(file_path)[0]
            os.rename(file_path, base + '.md')
            return

        # 使用 xml.etree.ElementTree 将 xml 文件转换为多维数组
        tree = ET.parse(file_path)
        root = tree.getroot()

        flag = 0  # 用于输出转换提示
        nl = '\r\n'  # 考虑 Windows 系统，换行符设为 \r\n
        new_content = f''  # f-string 多行字符串

        # list_item 的 id 与 type 的对应
        list_item = {}
        for child in root[0]:
            if 'list' in child.tag:
                list_item[child.attrib['id']] = child.attrib['type']

        # 得到多维数组中的文本，因为是数组，不是对象（json），所以只能遍历
        # root[1] 为 body
        for child in root[1]:
            # 正常文本
            if 'para' in child.tag:
                for child2 in child:
                    if 'text' in child2.tag:
                        # 将 None 转为 "
                        if child2.text is None:
                            child2.text = ''
                        new_content += f'%s{nl}{nl}' % child2.text
                        break

            elif 'image' in child.tag:
                if flag == 0:
                    self.print_ydnote_file_name(file_path)

                for child2 in child:
                    # source 在 text 前
                    if 'source' in child2.tag:
                        image_url = ''
                        if child2.text is not None:
                            image_url = self.get_new_down_or_upload_url(child2.text, file_path)
                            flag += 1

                    elif 'text' in child2.tag:
                        image_name = child2.text
                        if child2.text is None:
                            image_name = ''
                        new_content += f'![%s](%s){nl}{nl}' % (image_name, image_url)
                        break

            # 代码块
            elif 'code' in child.tag:
                for child2 in child:
                    # text 在 language 前
                    if 'text' in child2.tag:
                        code = child2.text
                    elif 'language' in child2.tag:
                        language = child2.text
                        if language is None:
                            language = ''
                        new_content += f'```%s{nl}%s{nl}```{nl}{nl}' % (language, code)
                        break

            elif 'list-item' in child.tag:
                # logging.info('list-item child: %s' % child)

                # 无序列表
                if list_item.get(child.attrib['list-id']) == 'unordered':

                    for child2 in child:
                        if 'text' in child2.tag:
                            text = child2.text
                            if text is None:
                                text = ''
                            new_content += f'- %s{nl}{nl}' % text
                # 有序列表
                elif list_item.get(child.attrib['list-id']) == 'ordered':
                    for child2 in child:
                        if 'text' in child2.tag:
                            count = 1
                            text = child2.text
                            if text is None:
                                text = ''
                            new_content += f'%s. %s{nl}{nl}' % (count, text)
                            # count += 1
            # 复选框
            elif 'todo' in child.tag:
                for child2 in child:
                    if 'text' in child2.tag:
                        text = child2.text
                        if text is None:
                            text = ''
                        new_content += f'- [ ] %s{nl}{nl}' % text
            # 引用
            elif 'quote' in child.tag:
                for child2 in child:
                    if 'text' in child2.tag:
                        text = child2.text
                        if text is None:
                            text = ''
                        new_content += f'> %s{nl}{nl}' % text

            # 表格
            elif 'table' in child.tag:
                for child2 in child:
                    if 'content' in child2.tag:
                        new_content += f'```{nl}原来格式为表格（table），转换较复杂，未转换，需要手动复制一下{nl}%s{nl}```{nl}{nl}' % child2.text

            # 其他
            else:
                for child2 in child:
                    if 'text' in child2.tag:
                        text = child2.text
                        if text is None:
                            text = ''
                        new_content += f'%s{nl}{nl}' % text

        self.write_content(file_path, new_content)

    def covert_html_to_markdown(self, file_path):
        with open(file_path, 'rb') as f:
            content_str = f.read().decode('utf-8')
        new_content = md(content_str)
        self.write_content(file_path, new_content)

    def write_content(self, file_path, new_content):
        " File is **.note，new_content is markdown string "

        base = os.path.splitext(file_path)[0]
        new_file_path = base + '.md'
        os.rename(file_path, new_file_path)
        with open(new_file_path, 'wb') as f:
            f.write(new_content.encode())

    def covert_markdown_file_image_url(self, content, file_path) -> str:
        """ 将 Markdown 中的有道云图床图片转换为 sm.ms 图床 """

        reg = r'!\[.*?\]\((.*?note\.youdao\.com.*?)\)'
        p = re.compile(reg)
        urls = p.findall(content)
        if len(urls) > 0:
            self.print_ydnote_file_name(file_path)
        for url in urls:
            new_url = self.get_new_down_or_upload_url(url, file_path)
            content = content.replace(url, new_url)
        return content

    def print_ydnote_file_name(self, file_path) -> None:

        ydnote_dirName = file_path.replace(self.local_dir, '')
        print('正在转换有道云笔记「%s」中的有道云图床图片链接...' % ydnote_dirName)

    def get_new_down_or_upload_url(self, url, file_path) -> str:
        """ 根据是否存在 smms_secret_token 判断是否需要上传到 sm.ms """

        if 'note.youdao.com' not in url:
            return url
        if self.smms_secret_token == '':
            return self.download_image(url, file_path)
        new_url = self.upload_to_smms(url, self.smms_secret_token)
        if new_url != url:
            return new_url
        return self.download_image(url, file_path)

    def download_image(self, url, file_path) -> str:
        """ 如果 smms_secret_token 为 null，将其下载到本地，返回相对 url """

        try:
            response = self.get(url)
        # 如果此处不抓异常，将退出运行
        except requests.exceptions.ProxyError as err:
            print('网络错误，「%s」下载失败' % url)
            print('错误提示：%s' % format(err))
            return url

        content_type = response.headers.get('Content-Type')
        if response.status_code != 200 or content_type is None or ('image' not in content_type):
            self.print_download_yd_image_error(url)
            return url

        # 默认下载图片到 youdaonote-images 文件夹
        image_dirname = 'youdaonote-images'
        local_image_dir = os.path.join(self.local_dir, image_dirname)
        if not os.path.exists(local_image_dir):
            os.mkdir(local_image_dir)
        image_basename = os.path.basename(urlparse(url).path)
        image_name = image_basename + '.' + content_type.split('/')[1]
        local_image_path = os.path.join(local_image_dir, image_name)

        try:
            with open(local_image_path, 'wb') as f:
                f.write(response.content)  # response.content 本身就为字节类型
            print('已将图片「%s」转换为「%s」' % (url, local_image_path))
        except:
            print(url + ' 图片有误！')
            return url

        relative_image_path = self.set_relative_image_path(file_path, image_name, image_dirname)
        return relative_image_path

    def set_relative_image_path(self, file_path, image_name, image_dirname):
        """ 图片设置为相对地址 """

        relative_path = file_path.replace(self.local_dir, '')
        logging.info('relative_path: %s', relative_path)
        layer_count = len(relative_path.split('/'))
        if layer_count == 2:
            new_image_path = os.path.join('./', image_dirname, image_name)
            return new_image_path
        relative = ''
        if layer_count > 2:
            sub_count = layer_count - 2
            for i in range(sub_count):
                relative = os.path.join(relative, '../')
        new_image_path = os.path.join(relative, image_dirname, image_name)
        return new_image_path

    def upload_to_smms(self, old_url, smms_secret_token) -> str:
        """ 上传图片到 sm.ms """

        try:
            smfile = self.get(old_url).content
        except:
            self.print_download_yd_image_error(old_url)
            return old_url

        smms_upload_api = 'https://sm.ms/api/v2/upload'
        headers = {'Authorization': smms_secret_token}
        files = {'smfile': smfile}

        try:
            res = requests.post(smms_upload_api, headers=headers, files=files)
        except requests.exceptions.ProxyError as err:
            logging.info('网络错误，请重试')
            print('网络错误，上传「%s」到 SM.MS 失败！将下载图片到本地' % old_url)
            print('错误提示：%s' % format(err))
            return old_url

        try:
            res_json = res.json()
        except ValueError:
            print('SM.MS 每小时只能上传 100 张图片，「%s」未转换，将下载到本地' % old_url)
            return old_url

        url = old_url
        if res_json['success'] is False:
            if res_json['code'] == 'image_repeated':
                url = res_json['images']
            elif res_json['code'] == 'flood':
                print('SM.MS 每小时只能上传 100 张图片，「%s」未转换，将下载图片到本地' % url)
                return url
            else:
                print(
                    '上传「%s」到 SM.MS 失败，请检查图片 url 或 smms_secret_token（%s）是否正确！将下载图片到本地' % (url, smms_secret_token))
                return url
        else:
            url = res_json['data']['url']
        print('已将图片「%s」转换为「%s」' % (old_url, url))
        return url

    def print_download_yd_image_error(self, url) -> None:
        print('下载「%s」失败！图片可能已失效，可浏览器登录有道云笔记后，查看图片是否能正常显示（验证登录才能显示）' % url)


def main():
    start_time = int(time.time())

    try:
        config_dict = check_config('config.json')
        session = YoudaoNoteSession()
        root_id = session.check_and_login(config_dict['username'], config_dict['password'])
        print('正在 pull，请稍后 ...')
        session.get_all(config_dict['local_dir'], config_dict['ydnote_dir'], config_dict['smms_secret_token'], root_id)

    except requests.exceptions.ProxyError as proxyErr:
        print('请检查网络代理设置；也有可能是调用有道云笔记接口次数达到限制，请等待一段时间后重新运行脚本，若一直失败，可删除「cookies.json」后重试')
        print('错误提示：' + format(proxyErr))
        print('已终止执行')
        sys.exit(1)
    except requests.exceptions.ConnectionError as connectionErr:
        print('网络错误，请检查网络是否正常连接。若突然执行中断，可忽略此错误，重新运行脚本')
        print('错误提示：' + format(connectionErr))
        print('已终止执行')
        sys.exit(1)
    except LoginError as loginErr:
        print('错误提示：' + format(loginErr))
        print('已终止执行')
        sys.exit(1)
    # 链接错误等异常
    except Exception as err:
        print('错误提示：' + format(err))
        print('已终止执行')
        sys.exit(1)

    end_time = int(time.time())
    print('运行完成！耗时 %s 秒' % str(end_time - start_time))


if __name__ == '__main__':
    main()
