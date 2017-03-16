#coding:utf-8
import sys
sys.path.append("..")
sys.path.append("../")
import settings
import tools.recutils as recutils
from datetime import datetime
import tools.systemUtils as systemUtils
import logging
"""
    zwx 2016-03-16 main
    主版本采集to_stat_info受理阶段指标
    受理、核实
    2016-07-28 修改传参方式
"""
"""
    入口
"""
def execute(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    # 受理阶段批转
    gather_accept_trans(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
    # 受理阶段发核实
    gather_verify_task(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)

"""
    采集受理指标
"""
def gather_accept_trans(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    accept_actdef_ids = sysInfo.get_data("accept_actdef_ids") if sysInfo.get_data("accept_actdef_ids") else [0]
    accept_act_inst = None
    if rec_info["act_property_id"] > 2:
        stat_info_dict["operate_num"] = 1
        accept_act_inst = recutils.get_last_trans_act(act_inst_list, accept_actdef_ids, (610,))
        if accept_act_inst:
            stat_info_dict["operate_time"] = accept_act_inst["end_time"]
            if accept_act_inst["end_time"] and accept_act_inst["deadline_time"] and accept_act_inst["end_time"] > accept_act_inst["deadline_time"]:
                stat_info_dict["intime_operate_num"] = 0
            else:
                stat_info_dict["intime_operate_num"] = 1
    elif rec_info["act_property_id"] in (1, 2):
        stat_info_dict["to_operate_num"] = 1
        accept_act_inst = recutils.get_last_act_inst(act_inst_list, accept_actdef_ids)
        if stat_info_dict["event_src_id"] and stat_info_dict["event_src_id"] not in settings.patrol_report_src_tuple:
            stat_info_dict["need_send_verify_num"] = 1
    # 受理人相关
    if accept_act_inst:
        stat_info_dict["operate_human_id"] = accept_act_inst["human_id"]
        stat_info_dict["operate_human_name"] = accept_act_inst["human_name"]
        stat_info_dict["operate_role_id"] = accept_act_inst["role_id"]

"""
    采集核实指标
"""
def gather_verify_task(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    patrol_task_list = recInfo.get_data("patrol_task_list")
    create_time = stat_info_dict["create_time"] if stat_info_dict.has_key("create_time") else datetime.min
    verify_task = recutils.get_last_patrol_task(patrol_task_list, create_time, 2)
    if verify_task:
        stat_info_dict["need_send_verify_num"] = 1
        stat_info_dict["send_verify_num"] = 1
        stat_info_dict["send_verify_time"] = verify_task["create_time"]
        #发核实人
        send_verify_human_id = verify_task["human_id"]
        send_verify_human = systemUtils.get_human_byID(biz_cur, send_verify_human_id)
        if send_verify_human:
            stat_info_dict["send_verify_human_id"] = send_verify_human_id
            stat_info_dict["send_verify_human_name"] = send_verify_human["human_name"]
        stat_info_dict["need_verify_num"] = 1
        #核实监督员
        verify_patrol_card_id = verify_task["card_id"]
        verify_patrol = systemUtils.get_patrol_byCardID(biz_cur, verify_patrol_card_id)
        if verify_patrol:
            stat_info_dict["verify_patrol_id"] = verify_patrol["patrol_id"]
            stat_info_dict["verify_patrol_name"] = verify_patrol["patrol_name"]
        if verify_task["done_flag"] == 1:
            stat_info_dict["verify_num"] = 1
            stat_info_dict["verify_time"] = verify_task["done_time"]
            if verify_task["used_time"] and settings.VERIFY_LIMIT < verify_task["used_time"]:
                stat_info_dict["intime_verify_num"] = 0
            else:
                stat_info_dict["intime_verify_num"] = 1
