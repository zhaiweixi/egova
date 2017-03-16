#coding: utf-8
"""
    zwx 2016-05-26
    统计数据管理
"""
from utils import get_statdb_conn
import sys
sys.path.append("..")
import settings
import constant.schemaConst as schemaConst

def delete_stat_rec_one(cur, rec_id):
    stat_rec_table_list = get_stat_rec_tables()
    for stat_rec_table in stat_rec_table_list:
        sql = "delete from %(table_name)s where rec_id = %(rec_id)s"
        param = {"table_name": stat_rec_table, "rec_id": rec_id}
        print sql % param
        cur.execute(sql % param)

def delete_stat_rec_all(cur):
    stat_rec_table_list = get_stat_rec_tables()
    for stat_rec_table in stat_rec_table_list:
        sql = "delete from %(table_name)s"
        param = {"table_name": stat_rec_table}
        print sql % param
        cur.execute(sql % param)

def get_stat_rec_tables():
    stat_rec_tables = []
    # 主版本
    stat_rec_tables.append(schemaConst.umstat_ + "to_stat_info")
    stat_rec_tables.append(schemaConst.umstat_ + "to_stat_main_info")
    stat_rec_tables.append(schemaConst.umstat_ + "to_stat_unit_eval")
    stat_rec_tables.append(schemaConst.umstat_ + "to_patrol_eval")
    stat_rec_tables.append(schemaConst.umstat_ + "to_dispatcher_eval")
    stat_rec_tables.append(schemaConst.umstat_ + "to_acceptor_eval")
    stat_rec_tables.append(schemaConst.umstat_ + "to_ganger_eval")
    stat_rec_tables.append(schemaConst.umstat_ + "to_unit_workload_eval")

    return stat_rec_tables

if __name__ == "__main__":
    try:
        import readline
    except:
        print u"自动补全模块readline加载失败"
    conn = get_statdb_conn()
    cur = conn.cursor()
    print u"帮助:"
    print u"删除所有案件命令: 0"
    print u"删除单条案件请直接输入案件号: 例如 10086"
    print u"退出: exit 或者 -1"
    print u"请输入命令:"
    while(True):
        commandName = raw_input()
        if commandName == "-1" or commandName == "exit":
            cur.close()
            conn.close()
            exit()
        elif commandName == "0":
            try:
                delete_stat_rec_all(cur)
                conn.commit()
                print u"删除所有案件成功"
            except Exception, e:
                conn.rollback()
                print u"删除所有案件失败:", str(e)
        else:
            try:
                delete_stat_rec_one(cur, commandName)
                conn.commit()
                print u"案件[rec_id = ", commandName, u"]删除成功"
            except Exception, e:
                conn.rollback()
                print u"案件[rec_id = ", commandName, u"]删除失败，原因:", str(e)

        print u"请输入命令:"
