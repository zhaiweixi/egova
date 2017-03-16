# coding: utf-8
import sys
sys.path.append("..")
import settings
import tools.systemUtils as systemUtils
import tools.timing as timing
from tools.utils import insert_many, copy_dict2dict as copy
import logging
"""
    zwx 2016-03-16 main
    to_acceptor_eval
    受理员工作量采集
    受理 不受理 核查批转 办结 发核实 发核查

"""
def execute(stat_cur, biz_cur, recInfo, sysInfo):
    accept_eval_list = []
    __appendAcceptTrans(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, accept_eval_list = accept_eval_list)
    __appendVerifyOrCheckTask(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, accept_eval_list = accept_eval_list)
    # 主键策略
    i = 1
    rec_id = recInfo.get_data("rec_id")
    for accept_eval_dict in accept_eval_list:
        accept_eval_dict["acceptor_eval_id"] = rec_id*100 + i
        i += 1
    
    from maintable.acceptEval import field, table_name
    sql = "delete from %(table_name)s where rec_id = %(rec_id)s"
    param = {"table_name": table_name, "rec_id": rec_id}
    stat_cur.execute(sql % param)
    if accept_eval_list:
        insert_many(stat_cur, table_name, accept_eval_list, field)

# 受理 核查批转
def __appendAcceptTrans(stat_cur, biz_cur, recInfo, sysInfo, accept_eval_list):
    logger = logging.getLogger("main.mainmodules.acceptEvalGather")
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    patrol_task_list = recInfo.get_data("patrol_task_list")
    accept_actdef_ids = sysInfo.get_data("accept_actdef_ids") if sysInfo.get_data("accept_actdef_ids") else [0]
    check_actdef_ids = sysInfo.get_data("check_actdef_ids") if sysInfo.get_data("check_actdef_ids") else [0]
    for act_inst in act_inst_list:
        accept_eval_dict = {}
        if act_inst["act_def_id"] in accept_actdef_ids:
            try:
                copy(rec_info, accept_eval_dict)
                accept_eval_dict["human_id"] = act_inst["human_id"]
                accept_eval_dict["human_name"] = act_inst["human_name"]
                accept_eval_dict["role_id"] = act_inst["role_id"]
                if act_inst["end_time"]:
                    accept_eval_dict["execute_time"] = act_inst["end_time"]
                    accept_eval_dict["action_start_time"] = act_inst["create_time"]
                    accept_eval_dict["action_end_time"] = act_inst["end_time"]
                else:
                    accept_eval_dict["execute_time"] = act_inst["create_time"]
                    accept_eval_dict["action_start_time"] = act_inst["create_time"]
                    accept_eval_dict["action_end_time"] = act_inst["end_time"]
                # 批转
                if act_inst["item_type_id"] and act_inst["item_type_id"] == 610:
                    
                    accept_eval_dict["operate_num"] = 1
                    if act_inst["end_time"] and act_inst["deadline_time"] and act_inst["end_time"] > act_inst["deadline_time"]:
                        accept_eval_dict["intime_operate_num"] = 0
                    else:
                        accept_eval_dict["intime_operate_num"] = 1
                # 作废
                elif act_inst["item_type_id"] and act_inst["item_type_id"] == 814:
                    accept_eval_dict["not_operate_num"] = 1
                # 无动作
                elif not act_inst["item_type_id"]:
                    accept_eval_dict["to_operate_num"] = 1
                # 其他活动暂时不算工作量
                else:
                    accept_eval_dict = {}
            except Exception, e:
                logger.error(u"受理工作量采集失败[rec_id = %s]: %s" % (rec_info["rec_id"], str(e)))
                accept_eval_dict = {}
        elif act_inst["act_def_id"] in check_actdef_ids:
            try:
                copy(rec_info, accept_eval_dict)
                accept_eval_dict["human_id"] = act_inst["human_id"]
                accept_eval_dict["human_name"] = act_inst["human_name"]
                accept_eval_dict["role_id"] = act_inst["role_id"]
                if act_inst["end_time"]:
                    accept_eval_dict["execute_time"] = act_inst["end_time"]
                    accept_eval_dict["action_start_time"] = act_inst["create_time"]
                    accept_eval_dict["action_end_time"] = act_inst["end_time"]
                else:
                    accept_eval_dict["execute_time"] = act_inst["create_time"]
                    accept_eval_dict["action_start_time"] = act_inst["create_time"]
                    accept_eval_dict["action_end_time"] = act_inst["end_time"]

                # 批转
                if act_inst["item_type_id"] and act_inst["item_type_id"] == 610:
                    accept_eval_dict["check_trans_num"] = 1
                    if act_inst["end_time"] and act_inst["deadline_time"] and act_inst["end_time"] > act_inst["deadline_time"]:
                        accept_eval_dict["intime_check_trans_num"] = 0
                    else:
                        accept_eval_dict["intime_check_trans_num"] = 1
                # 办结
                elif act_inst["item_type_id"] and act_inst["item_type_id"] == 800:
                    accept_eval_dict["archive_num"] = 1
                    # 结案时间应特殊处理，因为to_wf_act_inst表中结案动作没有存end_time
                    accept_eval_dict["execute_time"] = rec_info["archive_time"]
                    accept_eval_dict["action_start_time"] = act_inst["create_time"]
                    accept_eval_dict["action_end_time"] = rec_info["archive_time"]
                # 其他动作不算工作量
                else:
                    accept_eval_dict = {}
            except Exception, e:
                logger.error(u"核查批转工作量采集失败[rec_id = %s]: %s" % (rec_info["rec_id"], str(e)))
                accept_eval_dict = {}
        # 加入工作量List中
        if accept_eval_dict:
            accept_eval_list.append(accept_eval_dict)
"""
    采集发核实阶段的信息
"""
def __appendVerifyOrCheckTask(stat_cur, biz_cur, recInfo, sysInfo, accept_eval_list):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    patrol_task_list = recInfo.get_data("patrol_task_list")
    timing_dict = sysInfo.get_data("timing_dict") if sysInfo.get_data("timing_dict") else {}
    accept_actdef_ids = sysInfo.get_data("accept_actdef_ids") if sysInfo.get_data("accept_actdef_ids") else [0]
    check_actdef_ids = sysInfo.get_data("check_actdef_ids") if sysInfo.get_data("check_actdef_ids") else [0]
    for act_inst in act_inst_list:
        # 受理阶段的发核实
        if act_inst["act_def_id"] in accept_actdef_ids:
            # 如果当前阶段有结束时间
            if act_inst["end_time"]:
                for patrol_task in patrol_task_list:
                    accept_eval_dict = {}
                    if patrol_task["task_type"] == 2 and patrol_task["create_time"] and patrol_task["create_time"] > act_inst["create_time"] and patrol_task["create_time"] < act_inst["end_time"]:
                        copy(rec_info, accept_eval_dict)
                        accept_eval_dict["need_send_verify_num"] = 1
                        accept_eval_dict["send_verify_num"] = 1
                        accept_eval_dict["human_id"] = patrol_task["human_id"]
                        accept_eval_dict["execute_time"] = patrol_task["create_time"]
                        accept_eval_dict["human_id"] = patrol_task["human_id"]
                        human = systemUtils.get_human_byID(biz_cur, patrol_task["human_id"])
                        accept_eval_dict["human_name"] = human["human_name"]
                        accept_eval_dict["human_region_id"] = human["region_id"]
                        accept_eval_dict["human_region_name"] = human["region_name"]
                        minutes = timing.get_minutes(timing_dict, settings.default_time_sys_id, act_inst["create_time"], patrol_task["create_time"])
                        if minutes <= settings.SEND_VERIFY_LIMIT:
                            accept_eval_dict["intime_send_verify_num"] = 1
                    # 字典表非空则加入到工作量List中
                    if accept_eval_dict:
                        accept_eval_list.append(accept_eval_dict)
            elif act_inst["human_id"] > 0 and act_inst["start_time"]:
                for patrol_task in patrol_task_list:
                    accept_eval_dict = {}
                    if patrol_task["task_type"] == 2 and patrol_task["create_time"] > act_inst["start_time"]:
                        copy(rec_info, accept_eval_dict)
                        accept_eval_dict["need_send_verify_num"] = 1
                        accept_eval_dict["send_verify_num"] = 1
                        accept_eval_dict["human_id"] = patrol_task["human_id"]
                        accept_eval_dict["execute_time"] = patrol_task["create_time"]
                        accept_eval_dict["human_id"] = patrol_task["human_id"]
                        human = systemUtils.get_human_byID(biz_cur, patrol_task["human_id"])
                        accept_eval_dict["human_name"] = human["human_name"]
                        accept_eval_dict["human_region_id"] = human["region_id"]
                        accept_eval_dict["human_region_name"] = human["region_name"]
                        minutes = timing.get_minutes(timing_dict, settings.default_time_sys_id, act_inst["create_time"], patrol_task["create_time"])
                        if minutes <= settings.SEND_VERIFY_LIMIT:
                            accept_eval_dict["intime_send_verify_num"] = 1
                    
                    # 字典表非空则加入到工作量List中
                    if accept_eval_dict:
                        accept_eval_list.append(accept_eval_dict)
        # 核查阶段发核查
        elif act_inst["act_def_id"] in check_actdef_ids:
            # 如果当前阶段有结束时间
            if act_inst["end_time"]:
                for patrol_task in patrol_task_list:
                    accept_eval_dict = {}
                    if patrol_task["task_type"] == 3 and patrol_task["create_time"] and patrol_task["create_time"] > act_inst["create_time"] and patrol_task["create_time"] < act_inst["end_time"]:
                        copy(rec_info, accept_eval_dict)
                        accept_eval_dict["need_send_check_num"] = 1
                        accept_eval_dict["send_check_num"] = 1
                        accept_eval_dict["human_id"] = patrol_task["human_id"]
                        accept_eval_dict["execute_time"] = patrol_task["create_time"]
                        accept_eval_dict["human_id"] = patrol_task["human_id"]
                        human = systemUtils.get_human_byID(biz_cur, patrol_task["human_id"])
                        accept_eval_dict["human_name"] = human["human_name"]
                        accept_eval_dict["human_region_id"] = human["region_id"]
                        accept_eval_dict["human_region_name"] = human["region_name"]
                        minutes = timing.get_minutes(timing_dict, settings.default_time_sys_id, act_inst["create_time"], patrol_task["create_time"])
                        if minutes <= settings.SEND_VERIFY_LIMIT:
                            accept_eval_dict["intime_send_check_num"] = 1
                    # 字典表非空则加入到工作量List中
                    if accept_eval_dict:
                        accept_eval_list.append(accept_eval_dict)
            elif act_inst["human_id"] > 0 and act_inst["start_time"]:
                for patrol_task in patrol_task_list:
                    accept_eval_dict = {}
                    if patrol_task["task_type"] == 2 and patrol_task["create_time"] > act_inst["start_time"]:
                        copy(rec_info, accept_eval_dict)
                        accept_eval_dict["need_send_check_num"] = 1
                        accept_eval_dict["send_check_num"] = 1
                        accept_eval_dict["human_id"] = patrol_task["human_id"]
                        accept_eval_dict["execute_time"] = patrol_task["create_time"]
                        accept_eval_dict["human_id"] = patrol_task["human_id"]
                        human = systemUtils.get_human_byID(biz_cur, patrol_task["human_id"])
                        accept_eval_dict["human_name"] = human["human_name"]
                        accept_eval_dict["human_region_id"] = human["region_id"]
                        accept_eval_dict["human_region_name"] = human["region_name"]
                        minutes = timing.get_minutes(timing_dict, settings.default_time_sys_id, act_inst["create_time"], patrol_task["create_time"])
                        if minutes <= settings.SEND_CHECK_LIMIT:
                            accept_eval_dict["intime_send_check_num"] = 1
                    
                    # 字典表非空则加入到工作量List中
                    if accept_eval_dict:
                        accept_eval_list.append(accept_eval_dict)