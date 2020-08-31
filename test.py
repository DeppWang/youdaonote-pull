import unittest
import pull
import os
import shutil
import sys
import logging
from markdownify import markdownify as md

# 级别由低到高 DEBUG、INFO，WARN、ERROR
# 设置为
# logging.basicConfig(level=logging.INFO)


__description__ = """
                    目的，确保 *pull.py* 在各种条件下运行通过
                    所有测试方法均通过时，才 push
                    先运行 test_login_right 和 test_cookies_login，再运行 python3 test.py
                    
                    原来针对每个方法写测试用例，还是太麻烦。
                    """

class Passport:
    username = "your_youdao_username"
    password = "your_youdao_password"

def set_right_cookies():
    with open('cookies-right.json', 'rb') as f:
        byte_cookies = f.read()

    with open('cookies.json', 'wb') as f2:
        f2.write(byte_cookies)


def set_right_config():
    with open('config-right.json', 'rb') as f:
        byte_config = f.read()

    with open('config.json', 'wb') as f:
        f.write(byte_config)


def remove_local_dir():
    local_dir = "/Users/yanjie/Documents/youdaonote-pull/test1"
    if os.path.exists(local_dir):
        shutil.rmtree(local_dir)
        
        
class Test(unittest.TestCase):
    def test_html_to_markdown(self):
        new_content = md(f"""<div><span style='color: rgb(68, 68, 68); line-height: 1.5; font-family: "Monaco","Consolas","Lucida Console","Courier New","serif"; font-size: 12px; background-color: rgb(247, 247, 247);'><a href="http://bbs.pcbeta.com/viewthread-1095891-1-1.html">http://bbs.pcbeta.com/viewthread-1095891-1-1.html</a><br></span></div><span style='color: rgb(68, 68, 68); line-height: 1.5; font-family: "Monaco","Consolas","Lucida Console","Courier New","serif"; font-size: 12px; background-color: rgb(247, 247, 247);'><div><span style='color: rgb(68, 68, 68); line-height: 1.5; font-family: "Monaco","Consolas","Lucida Console","Courier New","serif"; font-size: 12px; background-color: rgb(247, 247, 247);'><br></span></div>sudo perl -pi -e 's|\x75\x30\x89\xd8|\xeb\x30\x89\xd8|' /System/Library/Extensions/AppleRTC.kext/Contents/MacOS/AppleRTC</span>
""")
        print(new_content)


class TestAPI(unittest.TestCase):

    def test_get_dir_api(self):
        print('----------------')
        # print('验证使用 Cookies 是否能成功登录\m')

        session = pull.YoudaoNoteSession()
        cookies_dict = pull.covert_json_str_to_dict('cookies.json')
        logging.info(cookies_dict)
        session.cookies_login(cookies_dict['cookies'])
        # root_id = session.get_root_id()
        # print(root_id)
        url = 'https://note.youdao.com/yws/api/personal/file?method=listPath&fileId=9d8a2385eeec77338211b4f04bbf844d&keyfrom=web&cstk=01PvSwwu'
        data = {
            'fileId': 'WEB8bcb99a589ab9660a10aa5f87ca61675',
            'cstk': '01PvSwwu'
        }
        content = session.post(url, data).content.decode('utf-8')
        logging.info(content)

    def test_get_file_api(self):
        print('----------------')
        # print('验证使用 Cookies 是否能成功登录\m')

        session = pull.YoudaoNoteSession()
        cookies_dict = pull.covert_json_str_to_dict('cookies.json')
        logging.info(cookies_dict)
        session.cookies_login(cookies_dict['cookies'])
        # root_id = session.get_root_id()
        # print(root_id)
        url = 'https://note.youdao.com/yws/api/personal/sync?method=download&keyfrom=web&cstk=01PvSwwu'
        data = {
            'fileId': 'WEB4aa8bf8074d61befea1dd20f5593f01c',
            'version': -1,
            'convert': 'true',
            'editorType': 1,
            'cstk': '01PvSwwu'
        }
        content = session.post(url, data).content.decode('utf-8')
        logging.info(content)

    def test_get_note_file_api(self):
        print('----------------')
        # print('验证使用 Cookies 是否能成功登录\m')

        session = pull.YoudaoNoteSession()
        cookies_dict = pull.covert_json_str_to_dict('cookies.json')
        # logging.info(cookies_dict)
        session.cookies_login(cookies_dict['cookies'])
        # root_id = session.get_root_id()
        # print(root_id)
        url = 'https://note.youdao.com/yws/api/personal/resource?method=listThumbsInfo&keyfrom=web&cstk=ZzXatKpy'
        data = {
            'fileId': 'WEB8bcb99a589ab9660a10aa5f87ca61675',
            'cstk': 'ZzXatKpy'
        }
        content = session.post(url, data)
        logging.info(content)

    def test_image_url(self):
        image_url = '![%s](https://www.zhihu.com/equation?tex=+k+%3D+%5Cleft%5B%5Cfrac%7Blog%28-z_%7Bvs%7D+%2F+near%29%7D%7Blog%281+%2B+%5Cfrac%7B2tan%5Ctheta%7D%7BS_y%7D%29%7D+%5Cright%5D+)' % 'test'
        print(image_url)


class TestErrorExit(unittest.TestCase):
    """ 测试 config.json """

    # def test_local_config_format_pull_py(self):
    #     """  """
    #     pull.main()

    def f_test_local_config_format(self):
        """ 用于测试本地 config.json 文件出错的情况 """

        with self.assertRaises(SystemExit):
            pull.main()

    def test_config_format(self):
        print('----------------')
        print('验证 config.json 格式错误（花括号位置），是否结束执行并输出提示\n')

        # 跟 config.json 的字符串相比，字符串首行换行将增加空格符，导致 eval 无法将 string 转换为 json
        # '
        #         {
        #             "username": "***",
        #             "password": "***",
        #             "local_dir": "/Users/yanjie/Documents/youdaonote-pull/deppwang2",
        #             "ydnote_dir": "",
        #             "smms_secret_token": ""
        #         }'
        config_str = """
        {
            "username": "%s",
            "password": "%s",
            "local_dir": "/Users/yanjie/Documents/youdaonote-pull/deppwang2",
            "ydnote_dir": "",
            "smms_secret_token": ""
        }""" % (Passport.username, Passport.password)

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        with self.assertRaises(SystemExit):
            pull.main()

    def test_config_format2(self):
        print('----------------')
        print('验证 config.json 格式错误（有注释），是否结束执行并输出提示\n')

        config_str = """{
            "username": "%s",
            "password": "%s",  // 添加注释
            "local_dir": "/Users/yanjie/Documents/youdaonote-pull/deppwang2",
            "ydnote_dir": "",
            "smms_secret_token": ""
        }""" % (Passport.username, Passport.password)

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        with self.assertRaises(SystemExit):
            pull.main()

    def test_config_key(self):
        print('----------------')
        print('测试 config 的 key 被修改时 \n')

        config_str = """{
            "username": "%s",
            "password": "%s",
            "local_dir": "/Users/yanjie/Documents/youdaonote-pull/deppwang2",
            "ydaonote_dir": "",
            "smms_secret_token": ""
        }""" % (Passport.username, Passport.password)

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        with self.assertRaises(SystemExit):
            pull.main()

    def test_config_username_password(self):
        print('----------------')
        print('验证账号密码为空时，是否结束执行并输出提示\n')

        config_str = """{
            "username": "",
            "password": "",
            "local_dir": "",
            "ydnote_dir": "",
            "smms_secret_token": ""
        }"""

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        with self.assertRaises(SystemExit):
            pull.main()

    def test_config_ydnote_dir_err(self):
        print('----------------')
        print('当 ydnote_dir 不存在时，是否结束并提示\n')
        # self.cookie_login_and_get_all('', 'GitHub', '')

        config_str = """{
            "username": "%s",
            "password": "%s",
            "local_dir": "/Users/yanjie/Documents/youdaonote-pull/deppwang2",
            "ydnote_dir": "GitHub",
            "smms_secret_token": ""
        }""" % (Passport.username, Passport.password)

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        set_right_cookies()

        with self.assertRaises(SystemExit):
            pull.main()

    def test_config_local_dir_err(self):
        print('----------------')
        print('当 local_dir 错误时（为相对路径），是否结束并提示\n')

        config_str = """{
            "username": "%s",
            "password": "%s",
            "local_dir": "~/Documents/youdaonote",
            "ydnote_dir": "",
            "smms_secret_token": ""
        }""" % (Passport.username, Passport.password)

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        set_right_cookies()

        with self.assertRaises(SystemExit):
            pull.main()

    def test_config_local_dir_err2(self):
        print('----------------')
        print('当 local_dir 错误时（不存在上层文件夹），是否结束并提示\n')

        config_str = """{
            "username": "%s",
            "password": "%s",
            "local_dir": "/Users/yanji/Documents/youdaonote-pull",
            "ydnote_dir": "",
            "smms_secret_token": ""
        }""" % (Passport.username, Passport.password)

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        set_right_cookies()

        with self.assertRaises(SystemExit):
            pull.main()

    def test_get_all_youdao_url_change(self):
        print('----------------')
        print('有道云笔记修改接口，是否提示\n')

        # 修改了将不变？
        pull.YoudaoNoteSession.DIR_MES_URL = 'https://note.youdao.com/yws/api/personal2/file/%s?all=true&f=true&len=30&sort=1&isReverse=false&method=listPageByParentId&keyfrom=web&cstk=%s'

        with open('config-right.json', 'rb') as f:
            byte_config = f.read()

        with open('config.json', 'wb') as f:
            f.write(byte_config)

        with self.assertRaises(SystemExit):
            pull.main()

        pull.YoudaoNoteSession.DIR_MES_URL = 'https://note.youdao.com/yws/api/personal/file/%s?all=true&f=true&len=30&sort=1&isReverse=false&method=listPageByParentId&keyfrom=web&cstk=%s'

    def test_get_all_network_err(self):
        print('----------------')
        print('网络未连接，是否提示\n')

        with open('config-right.json', 'rb') as f:
            byte_config = f.read()

        with open('config.json', 'wb') as f:
            f.write(byte_config)

        with self.assertRaises(SystemExit):
            pull.main()


class TestDownLoad(unittest.TestCase):

    def test_get_all_with_no_token(self):
        """
        是否可以抛出错误，但继续执行？不能抛出错误，只能打印错误
        """

        print('----------------')
        print('验证 smms_secret_token 为 null 时，是否能完整下载成功\n')

        local_dir = "/Users/yanjie/Documents/youdaonote-pull/test1"
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir)

        config_str = """{
            "username": "%s",
            "password": "%s",
            "local_dir": "%s",
            "ydnote_dir": "test",
            "smms_secret_token": ""
        }""" % (Passport.username, Passport.password, local_dir)

        set_right_cookies()

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        self.assertIsNone(pull.main())

    def test_get_test_with_no_token(self):
        """
        是否可以抛出错误，但继续执行？不能抛出错误，只能打印错误
        """

        print('----------------')
        print('验证 smms_secret_token 为 null 时，是否能完整下载成功\n')

        local_dir = "/Users/yanjie/Documents/youdaonote-pull/test1"
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir)

        config_str = """{
            "username": "%s",
            "password": "%s",
            "local_dir": "%s",
            "ydnote_dir": "",
            "smms_secret_token": ""
        }""" % (Passport.username, Passport.password, local_dir)

        set_right_cookies()

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        self.assertIsNone(pull.main())

    def test_get_all_with_token(self):
        print('----------------')
        print('验证 smms_secret_token 不为 null 时，是否能完整下载\n')

        local_dir = "/Users/yanjie/Documents/youdaonote-pull/test1"
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir)

        config_str = """{
            "username": "%s",
            "password": "%s",
            "local_dir": "%s",
            "ydnote_dir": "test",
            "smms_secret_token": "SGSLk9yWcTe4RenXYqEPMkqVrx0Y8qI0"
        }""" % (Passport.username, Passport.password, local_dir)

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        self.assertIsNone(pull.main())

    def test_get_all_with_err_token(self):
        print('----------------')
        print('验证 smms_secret_token 错误时，是否能完整下载\n')

        local_dir = "/Users/yanjie/Documents/youdaonote-pull/test1"
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir)

        config_str = """{
            "username": "%s",
            "password": "%s",
            "local_dir": "%s",
            "ydnote_dir": "test",
            "smms_secret_token": "SGSLk9yWcTe4RenXYqEPMkqVrx0Y8error"
        }""" % (Passport.username, Passport.password, local_dir)

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        self.assertIsNone(pull.main())

    def test_get_all_with_chinese_dir(self):
        print('----------------')
        print('验证目录包含中文时，能否正常下载\n')

        local_dir = "/Users/yanjie/Documents/youdaonote-pull/测试"
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir)

        config_str = """{
            "username": "%s",
            "password": "%s",
            "local_dir": "%s",
            "ydnote_dir": "test",
            "smms_secret_token": ""
        }""" % (Passport.username, Passport.password, local_dir)

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        self.assertIsNone(pull.main())

    def test_get_all_update(self):
        print('----------------')
        print('验证更新\n')

        local_dir = "/Users/yanjie/Documents/youdaonote-pull/test1"

        config_str = """{
            "username": "%s",
            "password": "%s",
            "local_dir": "%s",
            "ydnote_dir": "test",
            "smms_secret_token": ""
        }""" % (Passport.username, Passport.password, local_dir)

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        self.assertIsNone(pull.main())


class LoginTest(unittest.TestCase):

    def test_login_right(self):
        """
        验证账号密码登录
        """
        remove_local_dir()
        set_right_config()

        if os.path.exists('cookies.json'):
            os.remove('cookies.json')

        self.assertIsNone(pull.main())

    def test_cookies_login(self):

        print('----------------')
        print('验证使用 Cookies 是否能成功登录\m')

        remove_local_dir()
        set_right_config()
        set_right_cookies()

        self.assertIsNone(pull.main())

    def test_login_forbid(self):
        """
        验证账号被封时，当运行测试失败时运行
        需要是账号密码登录
        ip 被封、没有 Cookie、账号密码密码正确。么有提示？
        """

        remove_local_dir()
        set_right_config()

        if os.path.exists('cookies.json'):
            os.remove('cookies.json')

        with self.assertRaises(SystemExit):
            pull.main()

    def test_username_password_err(self):
        """ 验证账号密码错误，无 Cookies，是否登录失败
        需要账号密码登录，此测试容易封 ip，
        将保存错误 Cookies 到 cookies.json

        账号密码错误时的提示：{'canTryAgain': False, 'scope': 'SECURITY', 'error': '207', 'message': 'Message[AUTHENTICATION_FAILURE]: User token must be authenticated.', 'objectUser': None}
          验证码错误时的提示：{'canTryAgain': False, 'scope': 'SECURITY', 'error': '207', 'message': 'Message[AUTHENTICATION_FAILURE]: User token must be authenticated.', 'objectUser': None}"
        """

        config_str = """{
            "username": "error_username",
            "password": "error_password",
            "local_dir": "/Users/yanjie/Documents/youdaonote-pull/test1",
            "ydnote_dir": "test",
            "smms_secret_token": ""
        }"""

        with open('config.json', 'wb') as f:
            f.write(config_str.encode('utf-8'))

        if os.path.exists('cookies.json'):
            os.remove('cookies.json')

        with self.assertRaises(SystemExit):
            pull.main()

    def test_cookies_error(self):
        print('----------------')
        print('验证人为修改，导致 cookies.json 格式错误，是否输出提示。不影响运行\n')

        set_right_config()

        conkies_str = """{
        cookies: [[],[
        }"""

        with open('cookies.json', 'wb') as f:
            f.write(conkies_str.encode('utf-8'))

        with self.assertRaises(SystemExit):
            pull.main()

    def test_cookies_error2(self):
        print('----------------')
        print('验证人为修改，导致 cookies.json 格式错误，是否输出提示。\n')

        set_right_config()

        conkies_str = """{}"""

        with open('cookies.json', 'wb') as f:
            f.write(conkies_str.encode('utf-8'))

        self.assertIsNone(pull.main())

        set_right_cookies()


# config = TestErrorExit

def error_exit_suite():
    suite = unittest.TestSuite()
    # suite.addTest(TestErrorExit('test_local_config_format'))
    suite.addTest(TestErrorExit('test_config_format'))
    suite.addTest(TestErrorExit('test_config_format2'))
    suite.addTest(TestErrorExit('test_config_key'))
    suite.addTest(TestErrorExit('test_config_username_password'))
    suite.addTest(TestErrorExit('test_config_ydnote_dir_err'))
    suite.addTest(TestErrorExit('test_config_local_dir_err'))
    suite.addTest(TestErrorExit('test_config_local_dir_err2'))
    suite.addTest(TestErrorExit('test_get_all_youdao_url_change'))
    return suite


def download_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDownLoad('test_get_all_with_no_token'))
    suite.addTest(TestDownLoad('test_get_all_with_token'))
    suite.addTest(TestDownLoad('test_get_all_with_err_token'))
    suite.addTest(TestDownLoad('test_get_all_with_chinese_dir'))
    suite.addTest(TestDownLoad('test_get_all_update'))
    return suite


def login_suite():
    suite = unittest.TestSuite()
    suite.addTest(LoginTest('test_login_right'))

    return suite


if __name__ == '__main__':
    # 如何模拟 Windows 环境与 Unix 环境运行脚本。在本地是没法做到的
    # 如何检查 logging 级别，时测试级别改为 Debug

    runner = unittest.TextTestRunner()

    error = error_exit_suite()
    download = download_suite()
    login = login_suite()

    logging.info(len(sys.argv))
    if len(sys.argv) == 1:
        print('--------------------------------')
        print('运行错误退出测试\n')
        runner.run(error)
        print('--------------------------------')
        print('运行下载测试\n')
        runner.run(download)
        # print('--------------------------------')
        # print('测试是否能正常登录\n')
        # runner.run(login)
        sys.exit(1)

    suite = eval(sys.argv[1])

    # 因为容易封 ip，单独测试 login
    if suite is login:
        with open('cookies.json', 'rb') as f:
            cookies = f.read().decode('utf-8')
        # print(cookies)
        runner.run(suite)
        with open('cookies.json', 'wb') as f:
            f.write(cookies.encode('utf-8'))
        sys.exit(1)

    runner.run(suite)
