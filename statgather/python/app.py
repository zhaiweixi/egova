# coding:utf-8
"""
   zwx 2016-05-26
   统计案件采集应用
"""
# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
# zwx 2016-09-20 不设置编码为utf-8
from datetime import datetime, timedelta
import time
import settings
from bean.recInfo import recInfoFactory
from bean.sysInfo import sysInfoFactory
from tools.utils import get_bizdb_conn, get_statdb_conn
import constant.schemaConst as schemaConst
import logging
import logging.config
import traceback

"""
    采集处理方法
"""
def gather_one_handler(biz_cur, stat_cur, rec_id, sysInfo):
    recInfo = recInfoFactory(stat_cur, biz_cur, rec_id)
    if recInfo.get_data("rec_info"):
        # 主版本数据表采集
        import mainGather
        mainGather.gather_handler(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)
        # 项目扩展表数据采集
        import projectGather
        projectGather.gather_handler(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)
    else:
        # 删除案件
        from tools.statDataManager import delete_stat_rec_one
        delete_stat_rec_one(cur = stat_cur, rec_id = rec_id)

"""
    定时执行任务
"""
def timer(n):
    dtGatherStart = datetime.now()
    logger = logging.getLogger("main")
    logger.info("---------------------------------------------")
    logger.info(u"采集开始:")
    iRecCount = 0
    biz_conn = get_bizdb_conn()
    biz_cur = biz_conn.cursor()
    stat_conn = get_statdb_conn()
    stat_cur = stat_conn.cursor()
    biz_cur.execute("select rec_id from %s" % (schemaConst.dlmis_ + "to_stat_gather"))
    rec_list = biz_cur.fetchall()
    if biz_cur.rowcount > 0 :
        iRecCount = biz_cur.rowcount
        sysInfo = sysInfoFactory(biz_cur = biz_cur, stat_cur = stat_cur)
        count = 0
        for rec in rec_list:
            rec_id = rec[0]
            try:
                gather_one_handler(biz_cur = biz_cur, stat_cur = stat_cur, rec_id = rec[0], sysInfo = sysInfo)
                biz_cur.execute("delete from %s where rec_id = %s" % (schemaConst.dlmis_ + "to_stat_gather", rec[0]))

                stat_conn.commit()
                biz_conn.commit()

            except Exception, e:
                stat_conn.rollback() # 先回滚错误采集已更新部分
                logger.error("rec gather error:[rec_id=%s]: %s" % (rec_id, traceback.format_exc()))
                if (settings.dbTypeName == "oracle"):
                    stat_cur.execute("select %s from dual" % (schemaConst.umstat_ + "sr_gather_log.nextval"))
                    row = stat_cur.fetchone()
                    gather_id = row[0]
                    stat_cur.execute("delete from %s where rec_id = %s" % (schemaConst.umstat_ + "tr_gather_log", rec_id))
                    stat_cur.execute("insert into %s (gather_id, rec_id, gather_time, gather_desc) values(:1, :2, :3, :4)" % (schemaConst.umstat_ + "tr_gather_log"), (gather_id, rec_id, datetime.now(), str(e)))
                else:
                    stat_cur.execute("delete from tr_gather_log where rec_id = %s" % (rec_id))
                    stat_cur.execute("insert into tr_gather_log(rec_id, gather_time, gather_desc) values(%s, %s, %s)",(rec_id, datetime.now(), str(e)))
                stat_conn.commit()
            count += 1
            if count % 100 == 0:
                logger.info(u"已采集%s条, 剩余%s条" % (count, iRecCount - count))
    try:
        import afterGatherHandler as afterGatherHandler
        afterGatherHandler.execute(stat_cur = stat_cur, biz_cur = biz_cur)
        biz_conn.commit()
        stat_conn.commit()
    except Exception, e:
        logger.error("afterGatherHandler error: %s" % traceback.format_exc())
    biz_conn.close()
    stat_conn.close()
    dtGatherEnd = datetime.now()
    logger.info(u"采集完成:")
    logger.info(u"共采集 %s 条案件,耗时 %s " % (iRecCount, dtGatherEnd - dtGatherStart))
    logger.info(u"采集任务挂起，下一次采集时间为: %s" % (dtGatherEnd + timedelta(seconds = n)))
    time.sleep(n)

"""
    启动定时任务,在23:00-6:00期间不采集
"""
def start():
    while True:
        if datetime.now().strftime("%H") not in ("23", "01", "00", "02", "03", "04", "05"):
            timer(settings.gather_interval)
if __name__ == "__main__":
    logging.config.fileConfig("conf/main_log.conf")
    start()