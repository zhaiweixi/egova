# coding: utf-8
"""
    zwx 2016-07-26
    单条采集测试
"""
import app
import logging.config
from bean.sysInfo import sysInfoFactory

def test_gather_handler(biz_cur, stat_cur, rec_id, sysInfo):
    app.gather_one_handler(biz_cur = biz_cur, stat_cur = stat_cur, rec_id = rec_id, sysInfo = sysInfo)

def test_one():
    try:
        import readline
    except:
        print u"readline模块加载失败"
    from tools.utils import get_bizdb_conn, get_statdb_conn
    biz_conn = get_bizdb_conn()
    stat_conn = get_statdb_conn()
    biz_cur = biz_conn.cursor()
    stat_cur = stat_conn.cursor()
    sysInfo = sysInfoFactory(stat_cur = stat_cur, biz_cur = biz_cur)
    print u"  单条案件采集测试:"
    print u"  退出请输入exit 或者 -1"
    while (True):
        print u"  请输入案件标识:"
        rec_id = raw_input()
        if rec_id == "exit" or rec_id == "-1":
            exit()
        else:
            test_gather_handler(biz_cur = biz_cur, stat_cur = stat_cur, rec_id = int(rec_id), sysInfo = sysInfo)
            stat_conn.commit()
            biz_conn.commit()
            print u"[rec_id = ", rec_id, u"]采集成功"
        print u"  请继续输入案件号:"

if __name__ == "__main__":
    logging.config.fileConfig("conf/test_log.conf")
    test_one()