import logging
import os
import sys
import time

LOG_FORMAT = "%(asctime)s %(levelname)s %(processName)s-%(threadName)s-%(thread)d %(filename)s:%(lineno)d %(funcName)-10s : %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S "


def init_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    logging.basicConfig(
        handlers=[
            logging.FileHandler(
                "logs/pull-{}.log".format(int(time.time())), "a", encoding="utf-8"
            ),
            logging.StreamHandler(sys.stdout),
        ],
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )
