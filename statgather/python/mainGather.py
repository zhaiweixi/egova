#coding:utf-8

from tools.utils import insert_one, insert_many, copy_dict2dict as copy
import constant.schemaConst as schemaConst
import logging

"""
    zwx 2016-03-16 main
    主版本采集
"""
"""
    入口
"""
def gather_handler(stat_cur, biz_cur, recInfo, sysInfo):
    # 参数说明
    # stat_cur 统计库游标
    # biz_cur 业务库游标
    # recInfo 案件信息
    # sysInfo 系统信息

    # to_stat_info
    gather_stat_info(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)
    # to_patrol_eval
    gather_patrol_eval(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)
    # to_acceptor_eval
    gather_accept_eval(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)
    # to_dispatch_eval
    gather_dispatch_eval(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)
    # to_unit_workload_eval
    gather_unit_workload_eval(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)
    
"""
    采集to_stat_info表
"""
def gather_stat_info(stat_cur, biz_cur, recInfo, sysInfo):
    rec_id = recInfo.get_data("rec_id")
    import mainmodules.statInfoGatherHandler as statInfoGatherHandler
    stat_info_dict = statInfoGatherHandler.get_stat_info_dict(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)
    if stat_info_dict:
        # 插入to_stat_info
        from datetime import datetime
        stat_info_dict["last_update_time"] = datetime.now()
        from maintable.statinfo import field as table_field, table_name as table_name
        sql = "delete from %(statInfo)s where rec_id = %(rec_id)s"
        param = {"statInfo": table_name, "rec_id": rec_id}
        stat_cur.execute(sql % param)
        insert_one(stat_cur, table_name, stat_info_dict, table_field)
        # 插入子表
        insert_stat_main_info(stat_cur, stat_info_dict)
        insert_stat_unit_eval(stat_cur, stat_info_dict)

# 插入子表to_stat_main_info
def insert_stat_main_info(stat_cur, stat_info_dict):
    logger = logging.getLogger("main.mainGather")
    try:
        from maintable.statMainInfo import field as table_field, table_name as table_name
        rec_id = stat_info_dict["rec_id"]
        sql = "delete from %(statMainInfo)s where rec_id = %(rec_id)s "
        param = {"statMainInfo": table_name, "rec_id": rec_id}
        stat_cur.execute(sql % param)
        insert_one(stat_cur, table_name, stat_info_dict, table_field)
    except Exception, e:
        logger.error("insert into to_stat_main_info error: %s" % str(e))

# 插入子表to_stat_unit_eval
def insert_stat_unit_eval(stat_cur, stat_info_dict):
    logger = logging.getLogger("main.mainGather")
    if stat_info_dict.has_key("bundle_dispose_deadline") and stat_info_dict["bundle_dispose_deadline"]:
        try:
            from maintable.statUnitEval import field as table_field, table_name as table_name
            rec_id = stat_info_dict["rec_id"]
            sql = "delete from %(statUnitEval)s where rec_id = %(rec_id)s "
            param = {"statUnitEval": table_name, "rec_id": rec_id}
            stat_cur.execute(sql % param)
            insert_one(stat_cur, table_name, stat_info_dict, table_field)
        except Exception, e:
            logger.error("insert into to_stat_unit_eval error: %s" % str(e))

# 监督员工作量采集
def gather_patrol_eval(stat_cur, biz_cur, recInfo, sysInfo):
    import mainmodules.patrolEvalGather as patrolEvalGather
    patrolEvalGather.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)

# 受理员工作量采集
def gather_accept_eval(stat_cur, biz_cur, recInfo, sysInfo):
    import mainmodules.acceptEvalGather as acceptEvalGather
    acceptEvalGather.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)

# 派遣员工作量采集
def gather_dispatch_eval(stat_cur, biz_cur, recInfo, sysInfo):
    import mainmodules.dispatchEvalGather as dispatchEvalGather
    dispatchEvalGather.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)

# 专业部门工作量采集
def gather_unit_workload_eval(stat_cur, biz_cur, recInfo, sysInfo):
    import mainmodules.unitWorkloadEvalGather as unitWorkloadEvalGather
    unitWorkloadEvalGather.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)