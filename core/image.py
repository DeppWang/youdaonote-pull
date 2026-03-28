import hashlib
import logging
import mimetypes
import os
import posixpath
import re
from typing import Tuple
from urllib import parse
from urllib.parse import urlparse

import requests

from core.config import (
    IMAGE_UPLOADER_ALIYUN_OSS,
    IMAGE_UPLOADER_LOCAL,
    IMAGE_UPLOADER_SMMS,
    AppConfig,
)

REGEX_IMAGE_URL = re.compile(r"!\[.*?\]\((.*?note\.youdao\.com.*?)\)")
REGEX_ATTACH = re.compile(r"\[(.*?)\]\(((http|https)://note\.youdao\.com.*?)\)")
IMAGES = "images"
ATTACH = "attachments"


class ImagePull:
    def __init__(self, youdaonote_api, config: AppConfig):
        self.youdaonote_api = youdaonote_api
        self.config = config
        self.is_relative_path = config.is_relative_path

    @classmethod
    def _url_encode(cls, file_path: str):
        return file_path.replace(" ", "%20")

    def migration_ydnote_url(self, file_path):
        with open(file_path, "rb") as f:
            content = f.read().decode("utf-8")

        image_urls = REGEX_IMAGE_URL.findall(content)
        if image_urls:
            logging.info('正在转换有道云笔记%s中的图片链接...', file_path)
        for image_url in image_urls:
            try:
                new_image_path = self._get_new_image_path(file_path, image_url)
            except Exception as error:
                logging.info(
                    "下载图片%s可能失败，请检查图片。错误提示：%s",
                    image_url,
                    format(error),
                )
                continue
            if image_url == new_image_path:
                continue
            content = content.replace(image_url, self._display_path(file_path, new_image_path))

        attach_name_and_url_list = REGEX_ATTACH.findall(content)
        if attach_name_and_url_list:
            logging.info("正在转换有道云笔记%s中的附件链接...", file_path)
        for attach_name_and_url in attach_name_and_url_list:
            attach_url = attach_name_and_url[1]
            attach_path = self._download_ydnote_url(
                file_path, attach_url, attach_name_and_url[0]
            )
            if not attach_path:
                continue
            content = content.replace(attach_url, self._display_path(file_path, attach_path))

        with open(file_path, "wb") as f:
            f.write(content.encode("utf-8"))

    def _display_path(self, note_file_path, target_path) -> str:
        if self._is_remote_url(target_path):
            return target_path
        if self.is_relative_path:
            target_path = self._set_relative_file_path(note_file_path, target_path)
        return self._url_encode(target_path)

    def _get_new_image_path(self, file_path, image_url) -> str:
        uploader = self.config.image_uploader
        if uploader == IMAGE_UPLOADER_SMMS:
            if self.config.smms_secret_token:
                new_file_url, error_msg = ImageUpload.upload_to_smms(
                    youdaonote_api=self.youdaonote_api,
                    image_url=image_url,
                    smms_secret_token=self.config.smms_secret_token,
                )
                if not error_msg:
                    return new_file_url
                logging.info(error_msg)
            else:
                logging.info("已选择 SM.MS，但未配置 smms_secret_token，将改为下载到本地")
        elif uploader == IMAGE_UPLOADER_ALIYUN_OSS:
            if self._is_aliyun_config_ready():
                new_file_url, error_msg = ImageUpload.upload_to_aliyun_oss(
                    youdaonote_api=self.youdaonote_api,
                    image_url=image_url,
                    aliyun_oss_config=self.config.aliyun_oss,
                )
                if not error_msg:
                    return new_file_url
                logging.info(error_msg)
            else:
                logging.info("已选择阿里云 OSS，但配置不完整，将改为下载到本地")
        elif uploader != IMAGE_UPLOADER_LOCAL:
            logging.info("未知的 image_uploader=%s，将改为下载到本地", uploader)

        image_path = self._download_ydnote_url(file_path, image_url)
        return image_path or image_url

    def _is_aliyun_config_ready(self) -> bool:
        cfg = self.config.aliyun_oss
        return all(
            (
                cfg.endpoint,
                cfg.bucket,
                cfg.access_key_id,
                cfg.access_key_secret,
            )
        )

    def _download_ydnote_url(self, file_path, url, attach_name=None) -> str:
        try:
            response = self.youdaonote_api.http_get(url)
        except requests.exceptions.ProxyError as err:
            logging.info("网络错误，%s下载失败。错误提示：%s", url, format(err))
            return ""

        content_type = response.headers.get("Content-Type", "")
        file_type = "附件" if attach_name else "图片"
        if response.status_code != 200 or not response.content:
            logging.info(
                "下载%s失败，%s 可能已失效，可浏览器登录有道云笔记后检查链接是否还能正常加载",
                url,
                file_type,
            )
            return ""

        file_dirname = ATTACH if attach_name else IMAGES
        local_parent_dir = os.path.dirname(file_path) if os.path.splitext(file_path)[1] else file_path
        local_file_dir = os.path.join(local_parent_dir, file_dirname).replace("\\", "/")
        os.makedirs(local_file_dir, exist_ok=True)

        file_name = self._resolve_download_file_name(
            url=url,
            response_url=response.url,
            content_type=content_type,
            attach_name=attach_name,
        )
        local_file_path = os.path.join(local_file_dir, file_name).replace("\\", "/")

        try:
            with open(local_file_path, "wb") as f:
                f.write(response.content)
            logging.info("已将%s%s转换为%s", file_type, url, local_file_path)
        except Exception:
            logging.info("%s %s 有误", url, file_type)
            return ""

        return local_file_path

    def _resolve_download_file_name(self, url, response_url, content_type, attach_name=None):
        if attach_name:
            return self._sanitize_file_name(attach_name)

        response_query = parse.parse_qs(urlparse(response_url).query)
        hinted_name = (
            response_query.get("filename", [""])[0]
            or response_query.get("download", [""])[0]
        )
        if hinted_name:
            file_name = hinted_name
        else:
            file_name = os.path.basename(urlparse(url).path) or "image"
        file_name = self._sanitize_file_name(file_name)
        if os.path.splitext(file_name)[1]:
            return file_name
        suffix = self._get_file_suffix(content_type)
        return "{}{}".format(file_name, suffix)

    def _sanitize_file_name(self, file_name):
        return re.sub(r'[\\/:\*\?"<>\|]', "_", file_name).strip() or "file"

    def _get_file_suffix(self, content_type):
        guessed = mimetypes.guess_extension(content_type.split(";")[0]) if content_type else None
        return guessed or ".jpg"

    def _set_relative_file_path(self, note_file_path, local_file_path) -> str:
        note_file_dir = os.path.dirname(note_file_path)
        rel_file_path = os.path.relpath(local_file_path, note_file_dir)
        return rel_file_path.replace("\\", "/")

    def _is_remote_url(self, path: str) -> bool:
        return path.startswith("http://") or path.startswith("https://")


class ImageUpload(object):
    """上传到指定图床。"""

    @staticmethod
    def upload_to_smms(youdaonote_api, image_url, smms_secret_token) -> Tuple[str, str]:
        file_bytes, file_name, _, error_msg = ImageUpload._download_source_image(
            youdaonote_api, image_url
        )
        if error_msg:
            return "", error_msg

        files = {"smfile": (file_name, file_bytes)}
        upload_api_url = "https://sm.ms/api/v2/upload"
        headers = {"Authorization": smms_secret_token}
        error_msg = (
            "SM.MS 免费版每分钟限额 20 张图片，每小时限额 100 张图片，大小限制 5 M，上传失败！「{}」未转换，"
            "将下载图片到本地".format(image_url)
        )
        try:
            res_json = requests.post(
                upload_api_url, headers=headers, files=files, timeout=5
            ).json()
        except requests.exceptions.ProxyError as err:
            return "", "网络错误，上传「{}」到 SM.MS 失败，将下载图片到本地。错误提示：{}".format(
                image_url, format(err)
            )
        except Exception:
            return "", error_msg

        if res_json.get("success"):
            url = res_json["data"]["url"]
            logging.info("已将图片%s转换为%s", image_url, url)
            return url, ""
        if res_json.get("code") == "image_repeated":
            url = res_json["images"]
            logging.info("已将图片%s转换为%s", image_url, url)
            return url, ""
        if res_json.get("code") == "flood":
            return "", error_msg

        return (
            "",
            "上传「{}」到 SM.MS 失败，请检查图片 url 或 smms_secret_token 是否正确，将下载图片到本地".format(
                image_url
            ),
        )

    @staticmethod
    def upload_to_aliyun_oss(youdaonote_api, image_url, aliyun_oss_config) -> Tuple[str, str]:
        try:
            import oss2
        except ImportError:
            return "", "使用阿里云 OSS 需要先安装 oss2，请执行 pip install -r requirements.txt"

        file_bytes, file_name, content_type, error_msg = ImageUpload._download_source_image(
            youdaonote_api, image_url
        )
        if error_msg:
            return "", error_msg

        endpoint = ImageUpload._normalize_oss_endpoint(
            aliyun_oss_config.endpoint, aliyun_oss_config.use_https
        )
        auth = oss2.Auth(
            aliyun_oss_config.access_key_id,
            aliyun_oss_config.access_key_secret,
        )
        bucket = oss2.Bucket(auth, endpoint, aliyun_oss_config.bucket)
        object_key = ImageUpload._build_oss_object_key(
            aliyun_oss_config.path,
            file_name,
            file_bytes,
        )

        headers = {"Content-Type": content_type} if content_type else None
        try:
            bucket.put_object(object_key, file_bytes, headers=headers)
        except Exception as error:
            return "", "上传「{}」到阿里云 OSS 失败：{}。将下载图片到本地".format(
                image_url, error
            )

        file_url = ImageUpload._build_oss_file_url(
            aliyun_oss_config,
            object_key,
        )
        logging.info("已将图片%s转换为%s", image_url, file_url)
        return file_url, ""

    @staticmethod
    def _download_source_image(youdaonote_api, image_url):
        try:
            response = youdaonote_api.http_get(image_url)
        except requests.exceptions.ProxyError as err:
            return (
                b"",
                "",
                "",
                "网络错误，下载「{}」失败。错误提示：{}".format(image_url, format(err)),
            )
        except Exception as err:
            return (
                b"",
                "",
                "",
                "下载「{}」失败，图片可能已失效，可浏览器登录有道云笔记后检查图片能否正常加载。错误提示：{}".format(
                    image_url, format(err)
                ),
            )

        if response.status_code != 200 or not response.content:
            return (
                b"",
                "",
                "",
                "下载「{}」失败，图片可能已失效，可浏览器登录有道云笔记后检查图片能否正常加载".format(
                    image_url
                ),
            )

        content_type = response.headers.get("Content-Type", "").split(";")[0]

        # 使用 MD5 哈希文件内容作为文件名，保证唯一性
        file_hash = hashlib.md5(response.content).hexdigest()

        # 获取文件后缀：优先从原始 URL 或 response URL 的文件名中获取
        # 1. 先从 response URL 的 query 参数获取文件名
        response_query = parse.parse_qs(urlparse(response.url).query)
        hinted_name = (
            response_query.get("filename", [""])[0]
            or response_query.get("download", [""])[0]
        )

        # 2. 提取后缀
        suffix = None
        if hinted_name:
            suffix = os.path.splitext(hinted_name)[1]
        if not suffix:
            # 从 response URL path 或原始 URL path 获取后缀
            path_suffix = os.path.splitext(urlparse(response.url).path)[1]
            if path_suffix:
                suffix = path_suffix
            else:
                original_suffix = os.path.splitext(urlparse(image_url).path)[1]
                if original_suffix:
                    suffix = original_suffix

        # 3. 如果还是没有，用 content-type 推断
        if not suffix:
            suffix = mimetypes.guess_extension(content_type) or ".jpg"

        # 使用 MD5 + 后缀作为文件名
        file_name = "{}{}".format(file_hash, suffix)

        return response.content, file_name, content_type, ""

    @staticmethod
    def _build_oss_object_key(path_prefix, file_name, file_bytes):
        suffix = os.path.splitext(file_name)[1]
        if not suffix:
            suffix = ".jpg"
        base_name = os.path.splitext(file_name)[0] or "image"
        object_name = "{}{}".format(base_name, suffix.lower())
        prefix = path_prefix.strip().strip("/")
        return posixpath.join(prefix, object_name) if prefix else object_name

    @staticmethod
    def _normalize_oss_endpoint(endpoint, use_https):
        value = str(endpoint).strip()
        if not value:
            return ""
        if value.startswith("http://") or value.startswith("https://"):
            return value
        scheme = "https" if use_https else "http"
        return "{}://{}".format(scheme, value)

    @staticmethod
    def _build_oss_file_url(aliyun_oss_config, object_key):
        object_key = parse.quote(object_key, safe='/')
        custom_domain = str(aliyun_oss_config.custom_domain).strip()
        if custom_domain:
            if not custom_domain.startswith("http://") and not custom_domain.startswith("https://"):
                scheme = "https" if aliyun_oss_config.use_https else "http"
                custom_domain = "{}://{}".format(scheme, custom_domain)
            return "{}/{}".format(custom_domain.rstrip("/"), object_key)

        endpoint = ImageUpload._normalize_oss_endpoint(
            aliyun_oss_config.endpoint,
            aliyun_oss_config.use_https,
        )
        parsed = urlparse(endpoint)
        netloc = parsed.netloc or parsed.path
        if netloc.startswith("{}.".format(aliyun_oss_config.bucket)):
            netloc = netloc[len(aliyun_oss_config.bucket) + 1 :]
        scheme = parsed.scheme or ("https" if aliyun_oss_config.use_https else "http")
        return "{}://{}.{}/{}".format(
            scheme,
            aliyun_oss_config.bucket,
            netloc.rstrip("/"),
            object_key,
        )
