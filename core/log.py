import io
import logging
import os
import sys
from datetime import datetime

from core.common import get_script_directory

LOG_FORMAT = "%(asctime)s %(levelname)s %(processName)s-%(threadName)s-%(thread)d %(filename)s:%(lineno)d %(funcName)-10s : %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S "


def _safe_stdout():
    """
    Windows 控制台默认使用 GBK 编码，笔记文件名中若含 \xa0、emoji 等
    字符，logging.StreamHandler(sys.stdout) 写日志时会抛出
    UnicodeEncodeError，并在 stderr 打印 "--- Logging error ---"。

    这里强制以 UTF-8 + errors="replace" 输出，保证日志不会中断拉取流程。
    非 Windows 平台或无 buffer 属性时回退到原 stdout。
    """
    buffer = getattr(sys.stdout, "buffer", None)
    if buffer is None:
        return sys.stdout
    return io.TextIOWrapper(
        buffer, encoding="utf-8", errors="replace", line_buffering=True
    )


def init_logging():
    log_dir = os.path.join(get_script_directory(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(
        log_dir, f"pull-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    )
    logging.basicConfig(
        handlers=[
            logging.FileHandler(log_filename, "a", encoding="utf-8", errors="replace"),
            logging.StreamHandler(_safe_stdout()),
        ],
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )
