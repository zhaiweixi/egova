# coding:utf-8
"""
    后台任务管理
"""
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append("..")
from threading import Thread
import logging
import logging.config


def start():
    logger = logging.getLogger("main")
    logger.info(u"python后台定时任务启动...")
    threads = []
    

    # 启动任务
    for thread in threads:
        thread.start()
    # 等待任务完成
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    logging.config.fileConfig("../conf/task_log.conf")
    start()