#coding: utf-8
"""
    采集完成后，附加处理
    zwx 2016-06-06
"""
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst
from datetime import datetime
import time, calendar
from tools.utils import toDbDateStr, query_for_list, get_statdb_conn, get_bizdb_conn, insert_many


def execute(stat_cur, biz_cur):
    update_rec_unit_stat(stat_cur = stat_cur, biz_cur = biz_cur)

# 更新业务库的to_rec_unit_stat
def update_rec_unit_stat(stat_cur, biz_cur):
    yyyy = time.strftime("%Y")
    mm = time.strftime("%m")
    last_day = calendar.monthrange(int(yyyy), int(mm))
    beginDate = toDbDateStr(yyyy + "-" + mm + "-01 00:00:00")
    endDate = toDbDateStr(yyyy + "-" + mm + "-" + str(last_day[1]) + " 23:59:59")
    sql = """select %(yyyy)s as year, %(mm)s as month,first_unit_id as unit_id, count(1) as rec_count from %(tableName)s 
             where bundle_dispose_deadline between %(beginDate)s and %(endDate)s and first_unit_id is not null
             group by first_unit_id
          """
    param = {}
    param["tableName"] = schemaConst.umstat_ + "to_stat_info"
    param["beginDate"] = beginDate
    param["endDate"] = endDate
    param["yyyy"] = int(yyyy)
    param["mm"] = int(mm)
    rec_unit_list = query_for_list(stat_cur, sql % param)
    table_name = schemaConst.dlmis_ + "to_rec_unit_stat"
    biz_cur.execute("delete from %s " % (table_name, ))
    field_tuple = ("year", "month", "unit_id", "rec_count")
    sql = "delete from %s where year = %s and month = %s"
    biz_cur.execute(sql % (table_name, yyyy, mm))
    insert_many(cur = biz_cur, table_name = table_name, data_list = rec_unit_list, field_tuple = field_tuple)