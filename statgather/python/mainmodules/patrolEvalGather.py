#coding: utf-8
import sys
sys.path.append("..")
import tools.systemUtils as systemUtils
import settings
import tools.recutils as recutils
from tools.utils import copy_dict2dict as copy, insert_many
import logging
"""
    zwx 2016-03-16 main
    监督员工作量采集入口
"""
def execute(stat_cur, biz_cur, recInfo, sysInfo):
    patrol_eval_list = []
    __appendReport(biz_cur = biz_cur, patrol_eval_list = patrol_eval_list, recInfo = recInfo, sysInfo = sysInfo)
    __appendVerify(biz_cur = biz_cur, patrol_eval_list = patrol_eval_list, recInfo = recInfo, sysInfo = sysInfo)
    __appendCheck(biz_cur = biz_cur, patrol_eval_list = patrol_eval_list, recInfo = recInfo, sysInfo = sysInfo)

    # 主键策略
    rec_id = recInfo.get_data("rec_id")
    i = 1
    for patrol_eval_dict in patrol_eval_list:
        patrol_eval_dict["patrol_eval_id"] = rec_id*100 + i
        # 权重只对应上报记录
        if not patrol_eval_dict.has_key("patrol_report_num") or patrol_eval_dict["patrol_report_num"] != 1:
            patrol_eval_dict["weights"] = 0
        i += 1
    
    # 入库
    from maintable.patrolEval import field, table_name
    sql = "delete from %(tableName)s where rec_id = %(rec_id)s "
    param = {"tableName": table_name, "rec_id": rec_id}
    stat_cur.execute(sql % param)
    insert_many(stat_cur, table_name, patrol_eval_list, field)

"""
    监督员上报工作量
"""
def __appendReport(biz_cur, recInfo, sysInfo, patrol_eval_list):
    rec_info = recInfo.get_data("rec_info")
    patrol_eval_dict = {}
    if rec_info["event_src_id"] in settings.patrol_report_src_tuple:
        copy(rec_info, patrol_eval_dict)
        patrol_eval_dict["patrol_report_num"] = 1
        report_patrol_id = rec_info["patrol_id"]
        patrol_eval_dict["human_id"] = report_patrol_id
        patrol_eval_dict["human_name"] = rec_info["patrol_name"]
        report_patrol = systemUtils.get_patrol_byID(biz_cur, report_patrol_id)
        if report_patrol:
            patrol_eval_dict["card_id"] = report_patrol["card_id"]
            patrol_eval_dict["human_region_id"] = report_patrol["region_id"]
            patrol_eval_dict["human_region_name"] = report_patrol["region_name"]
            patrol_eval_dict["human_unit_id"] = report_patrol["unit_id"]
            patrol_eval_dict["human_unit_name"] = report_patrol["unit_name"]
        patrol_eval_dict["report_patrol_id"] = rec_info["patrol_id"]
        patrol_eval_dict["report_patrol_name"] = rec_info["patrol_name"]
        patrol_eval_dict["execute_time"] = rec_info["create_time"]

    # 工作量字典非空则插入List 
    if patrol_eval_dict:
        patrol_eval_list.append(patrol_eval_dict)

"""
    监督员核实工作量
"""
def __appendVerify(biz_cur, recInfo, sysInfo, patrol_eval_list):
    logger = logging.getLogger("main.mainmodules.patrolEvalGather")
    patrol_task_list = recInfo.get_data("patrol_task_list")
    rec_id = recInfo.get_data("rec_id")
    rec_info = recInfo.get_data("rec_info")
    if patrol_task_list:
        for patrol_task_dict in patrol_task_list:
            patrol_eval_dict = {}
            if patrol_task_dict["task_type"] != 2:
                continue
            try:
                copy(rec_info, patrol_eval_dict)
                patrol_eval_dict["need_verify_num"] = 1
                verify_card_id = patrol_task_dict["card_id"]
                verify_patrol = systemUtils.get_patrol_byCardID(biz_cur, verify_card_id)
                patrol_eval_dict["card_id"] = verify_card_id
                if verify_patrol:
                    patrol_eval_dict["human_id"] = verify_patrol["patrol_id"]
                    patrol_eval_dict["human_name"] = verify_patrol["patrol_name"]
                if patrol_task_dict["done_flag"] == 1:
                    patrol_eval_dict["verify_num"] = 1
                    patrol_eval_dict["execute_time"] = patrol_task_dict["done_time"]
                    if patrol_task_dict["used_time"] and patrol_task_dict["used_time"] > settings.VERIFY_LIMIT:
                        patrol_eval_dict["intime_verify_num"] = 0
                    else:
                        patrol_eval_dict["intime_verify_num"] = 1
                else:
                    patrol_eval_dict["to_verify_num"] = 1
                    patrol_eval_dict["execute_time"] = patrol_task_dict["create_time"]

                # 项目定制
                if rec_info["event_src_id"] in settings.patrol_report_src_tuple:
                    patrol_eval_dict["report_patrol_id"] = rec_info["patrol_id"]
                    patrol_eval_dict["report_patrol_name"] = rec_info["patrol_name"]

            except Exception, e:
                logger.error(u"监督员核实工作量采集失败[rec_id = %s]: %s" % (rec_id, str(e)))
                patrol_eval_dict = {}
            # 工作量字典非空则插入List
            if patrol_eval_dict:
                patrol_eval_list.append(patrol_eval_dict)
"""
    监督员核查工作量
"""
def __appendCheck(biz_cur, recInfo, sysInfo, patrol_eval_list):
    logger = logging.getLogger("main.mainmodules.patrolEvalGather")
    patrol_task_list = recInfo.get_data("patrol_task_list")
    act_inst_list = recInfo.get_data("act_inst_list")
    rec_id = recInfo.get_data("rec_id")
    rec_info = recInfo.get_data("rec_info")
    if patrol_task_list:
        for patrol_task_dict in patrol_task_list:
            patrol_eval_dict = {}
            if patrol_task_dict["task_type"] != 3:
                continue
            try:
                copy(rec_info, patrol_eval_dict)
                card_id = patrol_task_dict["card_id"]
                check_patrol = systemUtils.get_patrol_byCardID(biz_cur, card_id)
                patrol_eval_dict["card_id"] = card_id
                patrol_eval_dict["need_check_num"] = 1
                if check_patrol:
                    patrol_eval_dict["human_id"] = check_patrol["patrol_id"]
                    patrol_eval_dict["human_name"] = check_patrol["patrol_name"]
                    patrol_eval_dict["human_region_id"] = check_patrol["region_id"]
                    patrol_eval_dict["human_region_name"] = check_patrol["region_name"]
                    patrol_eval_dict["human_unit_id"] = check_patrol["unit_id"]
                    patrol_eval_dict["human_unit_name"] = check_patrol["unit_name"]
                if patrol_task_dict["done_flag"] == 1:
                    patrol_eval_dict["check_num"] = 1
                    patrol_eval_dict["execute_time"] = patrol_task_dict["done_time"]
                    check_used = patrol_task_dict["used_time"]
                    patrol_eval_dict["invalid_check_num"] = get_invalid_check_num(patrol_task_dict, act_inst_list, patrol_task_list, sysInfo)
                else:
                    patrol_eval_dict["to_check_num"] = 1
                    patrol_eval_dict["execute_time"] = patrol_task_dict["create_time"]

                #项目定制
                if rec_info["event_src_id"] in settings.patrol_report_src_tuple:
                    patrol_eval_dict["report_patrol_id"] = rec_info["patrol_id"]
                    patrol_eval_dict["report_patrol_name"] = rec_info["patrol_name"]
            except Exception, e:
                logger.error(u"核查工作量采集失败[rec_id = %s]: %s" % (rec_id, str(e)))
                patrol_eval_dict = {}
            # 工作量字典非空则插入List 
            if patrol_eval_dict:
                patrol_eval_list.append(patrol_eval_dict)

"""
  获取核查无效数
  每个核查阶段，只有最后一次核查算有效
"""
def get_invalid_check_num(patrol_task_dict, act_inst_list, patrol_task_list, sysInfo):
    from datetime import datetime
    
    check_actdef_ids = sysInfo.get_data("check_actdef_ids") if sysInfo.get_data("check_actdef_ids") else [0]
    result = 0
    task_done_time = patrol_task_dict["done_time"]
    check_start_time = datetime.min
    check_act_inst = recutils.get_between_last_act_inst(act_inst_list, check_actdef_ids, check_start_time, task_done_time)
    if check_act_inst:
        if check_act_inst["end_time"]:
            check_act_end_time = check_act_inst["end_time"]
        else:
            check_act_end_time = datetime.now()

        for patrol_task_one in patrol_task_list:
            done_time = patrol_task_one["done_time"]
            if patrol_task_one["task_type"] == 3 and done_time and done_time > task_done_time and done_time < check_act_end_time:
                result = 1
                break
            else:
                continue
    return result