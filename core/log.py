import logging
import os
import sys
from datetime import datetime

LOG_FORMAT = "%(asctime)s %(levelname)s %(processName)s-%(threadName)s-%(thread)d %(filename)s:%(lineno)d %(funcName)-10s : %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S "


def get_script_directory():
    """获取脚本所在的目录"""
    if getattr(sys, "frozen", False):
        # 如果是打包后的可执行文件
        return os.path.dirname(sys.executable)
    else:
        # 如果是普通脚本
        return "."


def init_logging():
    log_dir = os.path.join(get_script_directory(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(
        log_dir, f"pull-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    )
    logging.basicConfig(
        handlers=[
            logging.FileHandler(log_filename, "a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )
