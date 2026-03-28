import copy
import json
import os
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Tuple

from core.common import get_script_directory

IMAGE_UPLOADER_LOCAL = "local"
IMAGE_UPLOADER_SMMS = "smms"
IMAGE_UPLOADER_ALIYUN_OSS = "aliyun_oss"
SUPPORTED_IMAGE_UPLOADERS = (
    IMAGE_UPLOADER_LOCAL,
    IMAGE_UPLOADER_SMMS,
    IMAGE_UPLOADER_ALIYUN_OSS,
)


@dataclass
class AliyunOssConfig:
    endpoint: str = ""
    bucket: str = ""
    access_key_id: str = ""
    access_key_secret: str = ""
    path: str = ""
    custom_domain: str = ""
    use_https: bool = True


@dataclass
class AppConfig:
    local_dir: str = ""
    ydnote_dir: str = ""
    smms_secret_token: str = ""
    is_relative_path: bool = True
    image_uploader: str = IMAGE_UPLOADER_LOCAL
    picgo_config_path: str = ""
    aliyun_oss: AliyunOssConfig = field(default_factory=AliyunOssConfig)

    @classmethod
    def from_dict(cls, config_dict: Dict) -> "AppConfig":
        merged = default_config()
        merged.update(
            {
                "local_dir": config_dict.get("local_dir", ""),
                "ydnote_dir": config_dict.get("ydnote_dir", ""),
                "smms_secret_token": config_dict.get("smms_secret_token", ""),
                "is_relative_path": config_dict.get("is_relative_path", True),
                "image_uploader": config_dict.get("image_uploader", ""),
                "picgo_config_path": config_dict.get("picgo_config_path", ""),
            }
        )
        aliyun_oss = merged["aliyun_oss"]
        aliyun_oss.update(config_dict.get("aliyun_oss", {}))
        merged["aliyun_oss"] = AliyunOssConfig(**aliyun_oss)

        image_uploader = merged["image_uploader"]
        if not image_uploader:
            image_uploader = (
                IMAGE_UPLOADER_SMMS
                if merged["smms_secret_token"]
                else IMAGE_UPLOADER_LOCAL
            )
        merged["image_uploader"] = image_uploader
        return cls(**merged)

    def to_dict(self) -> Dict:
        return asdict(self)


def default_config_path() -> str:
    return os.path.join(get_script_directory(), "config.json")


def default_config() -> Dict:
    return {
        "local_dir": "",
        "ydnote_dir": "",
        "smms_secret_token": "",
        "is_relative_path": True,
        "image_uploader": IMAGE_UPLOADER_LOCAL,
        "picgo_config_path": "",
        "aliyun_oss": {
            "endpoint": "",
            "bucket": "",
            "access_key_id": "",
            "access_key_secret": "",
            "path": "",
            "custom_domain": "",
            "use_https": True,
        },
    }


def load_config(config_path=None) -> Tuple[AppConfig, str]:
    config_path = config_path if config_path else default_config_path()
    try:
        with open(config_path, "rb") as f:
            config_str = f.read().decode("utf-8-sig")
    except OSError as error:
        return AppConfig(), "读取配置文件失败：{}".format(error)

    try:
        config_dict = json.loads(config_str)
    except Exception:
        return (
            AppConfig(),
            "请检查「config.json」格式是否为 utf-8 格式的 json！建议使用 Sublime 编辑「config.json」",
        )

    if not isinstance(config_dict, dict):
        return AppConfig(), "请检查「config.json」内容是否为 json 对象"

    required_keys = ("local_dir", "ydnote_dir", "smms_secret_token", "is_relative_path")
    missing_keys = [key for key in required_keys if key not in config_dict]
    if missing_keys:
        return (
            AppConfig(),
            "请检查「config.json」的 key 是否至少包含 local_dir, ydnote_dir, smms_secret_token, is_relative_path",
        )

    config = AppConfig.from_dict(config_dict)
    if config.image_uploader not in SUPPORTED_IMAGE_UPLOADERS:
        return (
            AppConfig(),
            "image_uploader 只支持 local、smms、aliyun_oss",
        )
    return config, ""


def save_config(config: AppConfig, config_path=None):
    config_path = config_path if config_path else default_config_path()
    with open(config_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(config.to_dict(), f, ensure_ascii=False, indent=4)
        f.write("\n")


def update_config_from_dict(config: AppConfig, data: Dict) -> AppConfig:
    merged = config.to_dict()
    next_config = copy.deepcopy(merged)
    for key, value in data.items():
        if key == "aliyun_oss" and isinstance(value, dict):
            next_config["aliyun_oss"].update(value)
            continue
        next_config[key] = value
    return AppConfig.from_dict(next_config)


def detect_picgo_config_paths() -> List[str]:
    candidates = []
    home_dir = os.path.expanduser("~")
    app_data = os.environ.get("APPDATA", "")
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "")

    for base_path in (
        os.path.join(home_dir, ".picgo", "config.json"),
        os.path.join(home_dir, ".picgo", "data.json"),
        os.path.join(home_dir, ".config", "picgo", "data.json"),
        os.path.join(home_dir, ".config", "PicGo", "data.json"),
        os.path.join(home_dir, "Library", "Application Support", "picgo", "data.json"),
        os.path.join(home_dir, "Library", "Application Support", "PicGo", "data.json"),
    ):
        if base_path:
            candidates.append(base_path)

    if app_data:
        candidates.extend(
            [
                os.path.join(app_data, "picgo", "data.json"),
                os.path.join(app_data, "PicGo", "data.json"),
            ]
        )
    if xdg_config_home:
        candidates.extend(
            [
                os.path.join(xdg_config_home, "picgo", "data.json"),
                os.path.join(xdg_config_home, "PicGo", "data.json"),
            ]
        )

    normalized = []
    seen = set()
    for path in candidates:
        normalized_path = os.path.abspath(path)
        if normalized_path in seen:
            continue
        seen.add(normalized_path)
        normalized.append(normalized_path)
    return normalized


def detect_picgo_config_path() -> str:
    for path in detect_picgo_config_paths():
        if os.path.exists(path):
            return path
    return ""


def load_picgo_config(picgo_config_path=None) -> Tuple[Dict, str, str]:
    target_path = picgo_config_path if picgo_config_path else detect_picgo_config_path()
    if not target_path:
        return {}, "", "未找到本地 PicGo 配置文件"

    try:
        with open(target_path, "r", encoding="utf-8-sig") as f:
            try:
                picgo_config = json.load(f)
            except Exception as error:
                return {}, target_path, "读取 PicGo 配置失败：{}".format(error)
    except OSError as error:
        return {}, target_path, "读取 PicGo 配置失败：{}".format(error)

    if not isinstance(picgo_config, dict):
        return {}, target_path, "PicGo 配置格式不正确"
    return picgo_config, target_path, ""


def import_config_from_picgo(picgo_config_path=None) -> Tuple[Dict, str]:
    picgo_config, target_path, error_msg = load_picgo_config(picgo_config_path)
    if error_msg:
        return {}, error_msg

    pic_bed = picgo_config.get("picBed", {})
    if not isinstance(pic_bed, dict):
        return {}, "PicGo 配置中缺少 picBed"

    aliyun_config = _extract_picgo_aliyun(pic_bed)
    smms_token = _extract_picgo_smms_token(pic_bed)
    current_uploader = str(pic_bed.get("current", "")).strip().lower()

    if current_uploader == "aliyun" and aliyun_config:
        return {
            "image_uploader": IMAGE_UPLOADER_ALIYUN_OSS,
            "aliyun_oss": aliyun_config,
            "picgo_config_path": target_path,
        }, ""

    if current_uploader == "smms" and smms_token:
        return {
            "image_uploader": IMAGE_UPLOADER_SMMS,
            "smms_secret_token": smms_token,
            "picgo_config_path": target_path,
        }, ""

    if aliyun_config:
        return {
            "image_uploader": IMAGE_UPLOADER_ALIYUN_OSS,
            "aliyun_oss": aliyun_config,
            "picgo_config_path": target_path,
        }, ""

    if smms_token:
        return {
            "image_uploader": IMAGE_UPLOADER_SMMS,
            "smms_secret_token": smms_token,
            "picgo_config_path": target_path,
        }, ""

    return {}, "PicGo 配置中未找到可导入的 SM.MS 或阿里云 OSS 配置"


def _extract_picgo_smms_token(pic_bed: Dict) -> str:
    smms = pic_bed.get("smms", {})
    if not isinstance(smms, dict):
        return ""
    token = smms.get("token", "")
    return str(token).strip()


def _extract_picgo_aliyun(pic_bed: Dict) -> Dict:
    aliyun = pic_bed.get("aliyun", {})
    if not isinstance(aliyun, dict):
        return {}

    access_key_id = str(aliyun.get("accessKeyId", "")).strip()
    access_key_secret = str(aliyun.get("accessKeySecret", "")).strip()
    bucket = str(aliyun.get("bucket", "")).strip()
    endpoint = _normalize_picgo_oss_endpoint(
        aliyun.get("endpoint") or aliyun.get("area") or aliyun.get("region") or ""
    )
    if not any((access_key_id, access_key_secret, bucket, endpoint)):
        return {}

    custom_domain = str(
        aliyun.get("customUrl") or aliyun.get("customDomain") or ""
    ).strip()
    use_https = not str(endpoint).startswith("http://")
    return {
        "endpoint": endpoint,
        "bucket": bucket,
        "access_key_id": access_key_id,
        "access_key_secret": access_key_secret,
        "path": str(aliyun.get("path", "")).strip(),
        "custom_domain": custom_domain,
        "use_https": use_https,
    }


def _normalize_picgo_oss_endpoint(raw_endpoint) -> str:
    endpoint = str(raw_endpoint).strip()
    if not endpoint:
        return ""
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint
    if endpoint.startswith("oss-"):
        return "https://{}.aliyuncs.com".format(endpoint)
    if "." not in endpoint:
        return "https://oss-{}.aliyuncs.com".format(endpoint)
    return "https://{}".format(endpoint)
