# coding: utf-8
"""
    人员工作量(全部)数据采集
    zwx 2016-08-01
    to_human_workload_all 采集
"""
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst
import logging

def execute(stat_cur, biz_cur, recInfo, sysInfo):
    logger = logging.getLogger("main.mainmodules.humanWorkloadAllGather")
    rec_id = recInfo.get_data("rec_id")
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    human_workload_list = []
    for act_inst in act_inst_list:
        __appendHumanWorkload(rec_info = rec_info, act_inst = act_inst, human_workload_list = human_workload_list)

    # 先删除案件信息
    try:
        disposeInfo = {}
        stat_cur.execute("select dispose_region_id,dispose_region_name from %s where rec_id = %s" % (schemaConst.umstat_ + "to_stat_info", rec_id))
        if (stat_cur.rowcount > 0):
            row = stat_cur.fetchone()
            disposeInfo["dispose_region_id"] = row[0]
            disposeInfo["dispose_region_name"] = row[1]
        else:
            disposeInfo["dispose_region_id"] = None
            disposeInfo["dispose_region_name"] = None
        from maintable.humanWorkloadAll import table_name, field
        stat_cur.execute("delete from %s where rec_id = %s" % (table_name, rec_id))
        if human_workload_list:
            count = 0
            for human_workload_dict in human_workload_list:
                count = count + 1
                human_workload_dict["workload_id"] = rec_id * 100 + count
                human_workload_dict["dispose_region_id"] = disposeInfo["dispose_region_id"]
                human_workload_dict["dispose_region_name"] = disposeInfo["dispose_region_name"]
            from tools.utils import insert_many
            insert_many(stat_cur, table_name, human_workload_list, field)

    except Exception, e:
        logger.error(u"人员工作量(全部)数据采集失败[rec_id = %s]: %s" % (rec_id, str(e)))


def __appendHumanWorkload(rec_info, act_inst, human_workload_list):
    # 606 延期
    # 610 批转
    # 626 回退
    # 800 存档
    # 810 挂账
    # 814 作废
    from tools.utils import copy_dict2dict
    human_workload_dict = {}
    if act_inst["item_type_id"] and act_inst["item_type_id"] in (610, 626, 800, 814, 606, 810):
        copy_dict2dict(rec_info, human_workload_dict)
        human_workload_dict["item_type_id"] = act_inst["item_type_id"]
        human_workload_dict["act_def_id"] = act_inst["act_def_id"]
        human_workload_dict["human_id"] = act_inst["human_id"]
        human_workload_dict["human_name"] = act_inst["human_name"]
        human_workload_dict["role_id"] = act_inst["role_id"]
        human_workload_dict["role_name"] = act_inst["role_name"]
        human_workload_dict["unit_id"] = act_inst["unit_id"]
        human_workload_dict["unit_name"] = act_inst["unit_name"]
        human_workload_dict["action_start_time"] = act_inst["create_time"]
        human_workload_dict["action_end_time"] = act_inst["end_time"]
        human_workload_dict["execute_time"] = act_inst["end_time"] if act_inst["end_time"] else act_inst["create_time"]
        human_workload_dict["next_act_def_id"] = act_inst["next_act_def_id"]
        if act_inst["end_time"] and act_inst["deadline_time"] and act_inst["end_time"] > act_inst["deadline_time"]:
            human_workload_dict["intime_flag"] = 0
        else:
            human_workload_dict["intime_flag"] = 1

        if act_inst["item_type_id"] == 610:
            human_workload_dict["trans_num"] = 1
        elif act_inst["item_type_id"] == 626:
            human_workload_dict["back_num"] = 1
        elif act_inst["item_type_id"] == 800:
            human_workload_dict["archive_num"] = 1
            # 结案时间特殊处理
            human_workload_dict["action_end_time"] = rec_info["archive_time"]
            human_workload_dict["execute_time"] = rec_info["archive_time"]
            if rec_info["archive_time"] and act_inst["deadline_time"] and rec_info["archive_time"] > act_inst["deadline_time"]:
                human_workload_dict["intime_flag"] = 0
            else:
                human_workload_dict["intime_flag"] = 1
                
        elif act_inst["item_type_id"] == 814:
            human_workload_dict["cancel_num"] = 1
        elif act_inst["item_type_id"] == 606:
            human_workload_dict["postpone_num"] = 1
        elif act_inst["item_type_id"] == 810:
            human_workload_dict["hang_num"] = 1

    if human_workload_dict:
        human_workload_list.append(human_workload_dict)
