#coding:utf-8
import sys
sys.path.append("..")
sys.path.append("../")
import settings
import tools.recutils as recutils
import tools.systemUtils as systemUtils
"""
    zwx 2016-03-16 main
    采集处置阶段指标
    处置、结案
"""
"""
    入口
"""
def execute(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    # 核查阶段批转 办结活动
    __extendCheckTrans(stat_cur = stat_cur, biz_cur = biz_cur, stat_info_dict = stat_info_dict, recInfo = recInfo, sysInfo = sysInfo)
    # 发核查 核查反馈
    __extendCheckTask(stat_cur = stat_cur, biz_cur = biz_cur, stat_info_dict = stat_info_dict, recInfo = recInfo, sysInfo = sysInfo)

"""
    核查批转(结案)
"""
def __extendCheckTrans(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    check_actdef_ids = sysInfo.get_data("check_actdef_ids") if sysInfo.get_data("check_actdef_ids") else [0]
    check_act_inst = None
    if rec_info["act_property_id"] > 13 and not rec_info["act_property_id"] in (12,):
        check_act_inst = recutils.get_last_trans_act(act_inst_list, check_actdef_ids, (610, 800))
        if check_act_inst:
            if check_act_inst["item_type_id"] == 610:
                # 核查批转
                stat_info_dict["check_trans_num"] = 1
                stat_info_dict["check_trans_time"] = check_act_inst["end_time"]
                stat_info_dict["check_trans_human_id"] = check_act_inst["human_id"]
                stat_info_dict["check_trans_human_name"] = check_act_inst["human_name"]
                stat_info_dict["check_trans_role_id"] = check_act_inst["role_id"]
                if check_act_inst["end_time"] and check_act_inst["deadline_time"] and check_act_inst["end_time"] > check_act_inst["deadline_time"]:
                    stat_info_dict["intime_check_trans_num"] = 0
                else:
                    stat_info_dict["intime_check_trans_num"] = 1
            elif check_act_inst["item_type_id"] == 800:
                # 结案
                stat_info_dict["need_human_archive_num"] = 1
                stat_info_dict["human_archive_num"] = 1
                stat_info_dict["archive_human_id"] = check_act_inst["human_id"]
                stat_info_dict["archive_human_name"] = check_act_inst["human_name"]
                stat_info_dict["archive_role_id"] = check_act_inst["role_id"]
                if check_act_inst["deadline_time"] and rec_info["archive_time"] and rec_info["archive_time"] > check_act_inst["deadline_time"]:
                    stat_info_dict["intime_human_archive_num"] = 0
                else:
                    stat_info_dict["intime_human_archive_num"] = 1
    elif rec_info["act_property_id"] in (11, 13):
        stat_info_dict["need_send_check_num"] = 1
"""
    发核查 反馈核查
"""
def __extendCheckTask(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    from datetime import datetime
    dispose_end_time = stat_info_dict["dispose_end_time"] if stat_info_dict.has_key("dispose_end_time") else datetime.min
    patrol_task_list = recInfo.get_data("patrol_task_list")
    check_patrol_task = recutils.get_last_patrol_task(patrol_task_list, dispose_end_time, 3)
    if check_patrol_task:
        stat_info_dict["send_check_num"] = 1
        send_check_human_id = check_patrol_task["human_id"]
        # 发核查人信息
        send_check_human = systemUtils.get_human_byID(biz_cur, send_check_human_id)
        if send_check_human:
            stat_info_dict["send_check_human_id"] = send_check_human_id
            stat_info_dict["send_check_human_name"] = send_check_human["human_name"]
        stat_info_dict["need_check_num"] = 1
        card_id = check_patrol_task["card_id"]
        check_patrol = systemUtils.get_patrol_byCardID(biz_cur, card_id)
        if check_patrol:
            stat_info_dict["check_patrol_id"] = check_patrol["patrol_id"]
            stat_info_dict["check_patrol_name"] = check_patrol["patrol_name"]
        if check_patrol_task["done_flag"] == 1:
            stat_info_dict["check_num"] = 1
            patrol_check_used = check_patrol_task["used_time"]
            if settings.CHECK_LIMIT < patrol_check_used:
                stat_info_dict["overtime_check_num"] = 1
                stat_info_dict["intime_check_num"] = 0
            else:
                stat_info_dict["overtime_check_num"] = 0
                stat_info_dict["intime_check_num"] = 1
