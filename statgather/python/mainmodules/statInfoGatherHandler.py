# coding: utf-8
"""
    zwx 2016-05-27
    增加采集特殊指标
    复杂的采集过程外挂脚本处理,例如处置阶段,简单阶段在此脚本中执行
    zwx 2017-03-21
    宁波城管修改 采集逻辑全部写在这个脚本中，不再调用外挂脚本
"""
import sys
sys.path.append("..")
from tools.utils import copy_dict2dict as copy, get_db_now
import tools.recutils as recutils
import logging
import settings
from tools.timing import get_minutes
import constant.sysConst as sysConst

def get_stat_info_dict(stat_cur, biz_cur, recInfo, sysInfo):
    logger = logging.getLogger("main.mainmodules.statInfoGather")
    rec_info = recInfo.get_data("rec_info")
    act_property_id = rec_info["act_property_id"] if rec_info["act_property_id"] else 0
    stat_info_dict = {}
    copy(rec_info, stat_info_dict)
    # 采集上报信息
    __extend_report_info(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
    if act_property_id and act_property_id not in (102,):
        # 受理阶段
        # import statInfoGather.accept as accept
        # accept.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        __extend_accept_info(recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集立案阶段
        if act_property_id > 2:
            __extend_inst_info(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集派遣阶段
        if act_property_id > 4:
            __extend_dispatch_info(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集处置阶段指标
        if act_property_id > 6:
            # import statInfoGather.dispose as dispose
            # dispose.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
            __extend_dispose_info(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集督查阶段指标
        if act_property_id > 8:
            __extend_supervise_info(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集核查阶段指标
        if act_property_id > 10: 
            # import statInfoGather.check as check
            # check.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
            __extend_check_info(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集值班长结案阶段指标
        if act_property_id == 12 or act_property_id > 13: 
            __extend_human_archive(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集办结阶段指标
        if act_property_id == 101:
            stat_info_dict["archive_num"] = 1
            stat_info_dict["intime_archive_num"] = stat_info_dict["intime_dispose_num"] if "intime_dispose_num" in stat_info_dict else 1
            stat_info_dict["overtime_archive_num"] = stat_info_dict["overtime_dispose_num"] if "overtime_dispose_num" in stat_info_dict else 0
    # 作废阶段       
    elif act_property_id == 102:
        __extend_cancel_info(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
    
    # 采集特殊指标 延期 挂账 回退
    try:
        # import statInfoGather.special as special
        # special.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        __extend_special_info(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
    except Exception, e:
        logger.error(u"特殊指标采集失败: %s " % str(e))
    return stat_info_dict

# 采集上报阶段信息
def __extend_report_info(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    # 采集案件指标
    stat_info_dict["report_num"] = 1
    rec_info = recInfo.get_data("rec_info")
    # 监督员上报数
    if rec_info["event_src_id"] in settings.patrol_report_src_tuple:
        stat_info_dict["patrol_report_num"] = 1
        stat_info_dict["public_report_num"] = 0
        stat_info_dict["report_patrol_id"] = rec_info["patrol_id"]
        stat_info_dict["report_patrol_name"] = rec_info["patrol_name"]
    else:
        stat_info_dict["patrol_report_num"] = 0
        stat_info_dict["public_report_num"] = 1
        stat_info_dict["need_send_verify_num"] = 1
    # 有效上报数
    if rec_info["act_property_id"] and rec_info["act_property_id"] > 4 and rec_info["act_property_id"] != 102:
        stat_info_dict["valid_report_num"] = 1
        stat_info_dict["valid_patrol_report_num"] = stat_info_dict["patrol_report_num"]
        stat_info_dict["valid_public_report_num"] = stat_info_dict["public_report_num"]

def __extend_accept_info(recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    accept_actdef_ids = sysInfo.get_data("accept_actdef_ids") if sysInfo.get_data("accept_actdef_ids") else [0]
    if rec_info["act_property_id"] > 2:
        stat_info_dict["operate_num"] = 1
        accept_act_inst_list = filter(lambda x: x["act_def_id"] in accept_actdef_ids and x["item_type_id"] in (610, ), act_inst_list)
        if accept_act_inst_list:
            accept_act_inst_list.sort(key=lambda x: x["create_time"])
            stat_info_dict["operate_time"] = accept_act_inst_list[-1]["end_time"]
            if accept_act_inst_list[-1]["end_time"] and accept_act_inst_list[-1]["deadline_time"] and accept_act_inst_list[-1]["end_time"] > accept_act_inst_list[-1]["deadline_time"]:
                stat_info_dict["intime_operate_num"] = 0
            else:
                stat_info_dict["intime_operate_num"] = 1
            stat_info_dict["operate_human_id"] = accept_act_inst_list[-1]["human_id"]
            stat_info_dict["operate_human_name"] = accept_act_inst_list[-1]["human_name"]
            stat_info_dict["operate_role_id"] = accept_act_inst_list[-1]["role_id"]
    elif rec_info["act_property_id"] in (1, 2):
        stat_info_dict["to_operate_num"] = 1
        accept_act_inst_list = filter(lambda x: x["act_def_id"] in accept_actdef_ids, act_inst_list)
        if accept_act_inst_list:
            accept_act_inst_list.sort(key=lambda x: x["create_time"])
            stat_info_dict["operate_human_id"] = accept_act_inst_list[-1]["human_id"]
            stat_info_dict["operate_human_name"] = accept_act_inst_list[-1]["human_name"]
            stat_info_dict["operate_role_id"] = accept_act_inst_list[-1]["role_id"]
        # accept_act_inst = recutils.get_last_act_inst(act_inst_list, accept_actdef_ids)
        if stat_info_dict["event_src_id"] and stat_info_dict["event_src_id"] not in settings.patrol_report_src_tuple:
            stat_info_dict["need_send_verify_num"] = 1
    # 受理人相关
    # if accept_act_inst:
    #     stat_info_dict["operate_human_id"] = accept_act_inst["human_id"]
    #     stat_info_dict["operate_human_name"] = accept_act_inst["human_name"]
    #     stat_info_dict["operate_role_id"] = accept_act_inst["role_id"]

    patrol_task_list = filter(lambda x: x["task_type"] == 2, recInfo.get_data("patrol_task_list"))

    if patrol_task_list:
        patrol_task_list.sort(key=lambda x: x["create_time"])
        stat_info_dict["need_send_verify_num"] = 1
        stat_info_dict["send_verify_num"] = 1
        stat_info_dict["send_verify_time"] = patrol_task_list[-1]["create_time"]
        # 发核实人
        send_verify_human_id = patrol_task_list[-1]["human_id"]
        if send_verify_human_id in sysInfo.get_data("human"):
            stat_info_dict["send_verify_human_id"] = send_verify_human_id
            stat_info_dict["send_verify_human_name"] = sysInfo.get_data("human")[send_verify_human_id]["human_name"]
        stat_info_dict["need_verify_num"] = 1
        # 核实监督员
        verify_patrol_card_id = patrol_task_list[-1]["card_id"]
        if verify_patrol_card_id in sysInfo.get_data("patrol_card"):
            stat_info_dict["verify_patrol_id"] = sysInfo.get_data("patrol_card")[verify_patrol_card_id]["patrol_id"]
            stat_info_dict["verify_patrol_name"] = sysInfo.get_data("patrol_card")[verify_patrol_card_id]["patrol_name"]
        # if verify_patrol:
        #     stat_info_dict["verify_patrol_id"] = verify_patrol["patrol_id"]
        #     stat_info_dict["verify_patrol_name"] = verify_patrol["patrol_name"]
        if patrol_task_list[-1]["done_flag"] == 1 and patrol_task_list[-1]["done_time"]:
            stat_info_dict["verify_num"] = 1
            stat_info_dict["intime_verify_num"] = 1
            stat_info_dict["verify_time"] = patrol_task_list[-1]["done_time"]
            verify_used = get_minutes(sysInfo.get_data("timing_dict"), sysConst.default_sys_time_id, patrol_task_list[-1]["create_time"], patrol_task_list[-1]["done_time"])
            if verify_used > sysConst.verify_limit:
                stat_info_dict["intime_verify_num"] = 0
            # else:
            #     stat_info_dict["intime_verify_num"] = 1

# 立案阶段采集
def __extend_inst_info(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    inst_actdef_ids = sysInfo.get_data("inst_actdef_ids") if sysInfo.get_data("inst_actdef_ids") else [0]
    if rec_info["act_property_id"] > 4:
        inst_act_inst_list = filter(lambda x: x["act_def_id"] in inst_actdef_ids and x["item_type_id"] in (610,), act_inst_list)
        stat_info_dict["inst_num"] = 1
        stat_info_dict["intime_inst_num"] = 1
        stat_info_dict["need_dispatch_num"] = 1
        # inst_act_inst = recutils.get_last_trans_act(act_inst_list, inst_actdef_ids, (610,))
        if inst_act_inst_list:
            inst_act_inst_list.sort(key=lambda x: x["create_time"])
            stat_info_dict["inst_time"] = inst_act_inst_list[-1]["end_time"]
            if inst_act_inst_list[-1]["end_time"] and inst_act_inst_list[-1]["deadline_time"] and inst_act_inst_list[-1]["end_time"] > inst_act_inst_list[-1]["deadline_time"]:
                stat_info_dict["intime_inst_num"] = 0
            # else:
            #     stat_info_dict["intime_inst_num"] = 1
            stat_info_dict["inst_human_id"] = inst_act_inst_list[-1]["human_id"]
            stat_info_dict["inst_human_name"] = inst_act_inst_list[-1]["human_name"]
            stat_info_dict["inst_role_id"] = inst_act_inst_list[-1]["role_id"]

    elif rec_info["act_property_id"] in (3, 4):
        stat_info_dict["to_inst_num"] = 1
        inst_act_inst_list = filter(lambda x: x["act_def_id"] in inst_actdef_ids and x["item_type_id"] in (610,),
                                    act_inst_list)
        if inst_act_inst_list:
            inst_act_inst_list.sort(key=lambda x: x["create_time"])
            stat_info_dict["inst_human_id"] = inst_act_inst_list[-1]["human_id"]
            stat_info_dict["inst_human_name"] = inst_act_inst_list[-1]["human_name"]
            stat_info_dict["inst_role_id"] = inst_act_inst_list[-1]["role_id"]
        # inst_act_inst = recutils.get_last_act_inst(act_inst_list, inst_actdef_ids)
    # 立案人信息
    # if inst_act_inst:
    #     stat_info_dict["inst_human_id"] = inst_act_inst["human_id"]
    #     stat_info_dict["inst_human_name"] = inst_act_inst["human_name"]
    #     stat_info_dict["inst_role_id"] = inst_act_inst["role_id"]

# 派遣阶段采集
def __extend_dispatch_info(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    dispatch_actdef_ids = sysInfo.get_data("dispatch_actdef_ids") if sysInfo.get_data("dispatch_actdef_ids") else [0]
    # dispatch_act_inst = None
    if rec_info["act_property_id"] > 6:
        stat_info_dict["dispatch_num"] = 1
        stat_info_dict["intime_dispatch_num"] = 1
        stat_info_dict["need_dispose_num"] = 1
        dispatch_act_inst_list = filter(lambda x: x["act_def_id"] in dispatch_actdef_ids and x["item_type_id"] in (610,), act_inst_list)
        # dispatch_act_inst = recutils.get_last_trans_act(act_inst_list, dispatch_actdef_ids, (610,))
        if dispatch_act_inst_list:
            dispatch_act_inst_list.sort(key=lambda x: x["create_time"])
            stat_info_dict["dispatch_time"] = dispatch_act_inst_list[-1]["end_time"]
            if dispatch_act_inst_list[-1]["end_time"] and dispatch_act_inst_list[-1]["end_time"] > dispatch_act_inst_list[-1]["deadline_time"]:
                stat_info_dict["intime_dispatch_num"] = 0
            #     stat_info_dict["overtime_dispatch_num"] = 1
            # else:
            #     stat_info_dict["intime_dispatch_num"] = 1
            #     stat_info_dict["overtime_dispatch_num"] = 0
            stat_info_dict["dispatch_human_id"] = dispatch_act_inst_list[-1]["human_id"]
            stat_info_dict["dispatch_human_name"] = dispatch_act_inst_list[-1]["human_name"]
            stat_info_dict["dispatch_role_id"] = dispatch_act_inst_list[-1]["role_id"]
        stat_info_dict["overtime_dispatch_num"] = stat_info_dict["dispatch_num"] - stat_info_dict["intime_dispatch_num"]
    elif rec_info["act_property_id"] in (5, 6):
        stat_info_dict["to_dispatch_num"] = 1
        dispatch_act_inst_list = filter(lambda x: x["act_def_id"] in dispatch_actdef_ids, act_inst_list)
        if dispatch_act_inst_list:
            dispatch_act_inst_list.sort(key=lambda x: x["create_time"])
            stat_info_dict["dispatch_human_id"] = dispatch_act_inst_list[-1]["human_id"]
            stat_info_dict["dispatch_human_name"] = dispatch_act_inst_list[-1]["human_name"]
            stat_info_dict["dispatch_role_id"] = dispatch_act_inst_list[-1]["role_id"]

# 处置阶段信息采集
# 计算处置活动时排除执法通、处置通2个节点
def __extend_dispose_info(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    dispose_actdef_ids = sysInfo.get_data("dispose_actdef_ids") if sysInfo.get_data("dispose_actdef_ids") else [0]
    last_dispose_act_inst_dict = {}
    if rec_info["act_property_id"] > 8:
        stat_info_dict["need_supervise_num"] = 1
        stat_info_dict["need_archive_num"] = 1
        stat_info_dict["dispose_num"] = 1
        stat_info_dict["intime_dispose_num"] = 1
        stat_info_dict["intime_to_archive_num"] = 1
        dispose_act_inst_list = filter(lambda x: x["act_def_id"] in dispose_actdef_ids and x["act_def_id"] not in sysConst.special_dispose_actdef_ids and x["item_type_id"] in (610,), act_inst_list)
        if dispose_act_inst_list:
            dispose_act_inst_list.sort(key=lambda x: x["create_time"])
            last_dispose_act_inst_dict = dispose_act_inst_list[-1]
            if dispose_act_inst_list[-1]["end_time"] and dispose_act_inst_list[-1]["bundle_deadline"] and dispose_act_inst_list[-1]["end_time"] > dispose_act_inst_list[-1]["bundle_deadline"]:
                stat_info_dict["intime_dispose_num"] = 0
                stat_info_dict["intime_to_archive_num"] = 0
        stat_info_dict["overtime_dispose_num"] = stat_info_dict["dispose_num"] - stat_info_dict["intime_dispose_num"]
        stat_info_dict["overtime_to_archive_num"] = stat_info_dict["dispose_num"] - stat_info_dict["intime_to_archive_num"]
    elif rec_info["act_property_id"] in (7, 8):
        stat_info_dict["to_dispose_num"] = 1
        stat_info_dict["intime_to_dispose_num"] = 1
        dispose_act_inst_list = filter(lambda x: x["act_def_id"] in dispose_actdef_ids and x["act_def_id"] not in sysConst.special_dispose_actdef_ids, act_inst_list)
        if dispose_act_inst_list:
            dispose_act_inst_list.sort(key=lambda x: x["create_time"])
            last_dispose_act_inst_dict = dispose_act_inst_list[-1]
            if dispose_act_inst_list[-1]["bundle_deadline"] and get_db_now(biz_cur) > dispose_act_inst_list[-1]["bundle_deadline"]:
                stat_info_dict["intime_to_dispose_num"] = 0
                stat_info_dict["need_archive_num"] = 1
                stat_info_dict["overtime_to_archive_num"] = 1
                stat_info_dict["intime_to_archive_num"] = 0
        stat_info_dict["overtime_to_dispose_num"] = stat_info_dict["to_dispose_num"] - stat_info_dict["intime_to_dispose_num"]

    if last_dispose_act_inst_dict:
        stat_info_dict["dispose_end_time"] = last_dispose_act_inst_dict["end_time"] if "dispose_num" in stat_info_dict and stat_info_dict["dispose_num"] else None
        stat_info_dict["dispose_deadline"] = last_dispose_act_inst_dict["deadline_time"]
        stat_info_dict["dispose_begin_time"] = last_dispose_act_inst_dict["create_time"]
        stat_info_dict["bundle_dispose_deadline"] = last_dispose_act_inst_dict["bundle_deadline"]
        # 处置用时 捆绑用时 处置时限 捆绑时限
        stat_info_dict["dispose_used"] = last_dispose_act_inst_dict["act_used"]
        stat_info_dict["bundle_dispose_used"] = last_dispose_act_inst_dict["bundle_used"]
        stat_info_dict["dispose_limit"] = last_dispose_act_inst_dict["act_limit"]
        stat_info_dict["bundle_dispose_limit"] = last_dispose_act_inst_dict["bundle_limit"]

        stat_info_dict["dispose_act_def_id"] = last_dispose_act_inst_dict["act_def_id"]
        stat_info_dict["dispose_unit_id"] = last_dispose_act_inst_dict["unit_id"]
        stat_info_dict["dispose_unit_name"] = last_dispose_act_inst_dict["unit_name"]

        real_dispose_act_inst_list = filter(lambda x: x["act_def_id"] == last_dispose_act_inst_dict["act_def_id"] and x["unit_id"] == last_dispose_act_inst_dict["unit_id"], act_inst_list)
        multi_rework_num = 0
        if real_dispose_act_inst_list and len(real_dispose_act_inst_list) > 1:
            check_actdef_ids = sysInfo.get_data("check_actdef_ids") if sysInfo.get_data("check_actdef_ids") else [-1]
            dispatch_actdef_ids = sysInfo.get_data("dispatch_actdef_ids") if sysInfo.get_data("dispatch_actdef_ids") else [-1]
            real_dispose_act_inst_list.sort(key=lambda x: x["create_time"])
            last_create_time = real_dispose_act_inst_list[0]["create_time"]
            for dispose_act_inst_dict in real_dispose_act_inst_list:
                check_act_inst_list = filter(lambda x: last_create_time < x["create_time"] < dispose_act_inst_dict["create_time"] and x["act_def_id"] in check_actdef_ids and x["item_type_id"] in (610,), act_inst_list)
                dispatch_act_inst_list = filter(lambda x: last_create_time < x["create_time"] < dispose_act_inst_dict["create_time"] and x["act_def_id"] in dispatch_actdef_ids and x["item_type_id"] in (610,), act_inst_list)
                if check_act_inst_list and dispatch_act_inst_list:
                    multi_rework_num += 1
        stat_info_dict["multi_rework_num"] = multi_rework_num
        stat_info_dict["rework_num"] = 1 if multi_rework_num else 0

        stat_info_dict["first_unit_id"] = last_dispose_act_inst_dict["unit_id"]
        stat_info_dict["first_unit_name"] = last_dispose_act_inst_dict["unit_name"]
        if last_dispose_act_inst_dict["unit_id"] in sysInfo.get_data("unit"):
            dispose_region_id = sysInfo.get_data("unit")[last_dispose_act_inst_dict["unit_id"]]["region_id"]
            if dispose_region_id in sysInfo.get_data("region"):
                stat_info_dict["dispose_region_id"] = sysInfo.get_data("region")[dispose_region_id]["region_id"]
                stat_info_dict["dispose_region_name"] = sysInfo.get_data("region")[dispose_region_id]["region_name"]
        # 宁波城管二级部门处理
        if last_dispose_act_inst_dict["act_def_id"] in (324,) and last_dispose_act_inst_dict["unit_id"] in sysInfo.get_data("unit"):
            first_unit_id = sysInfo.get_data("unit")[last_dispose_act_inst_dict["unit_id"]]["senior_id"]
            if first_unit_id in sysInfo.get_data("unit"):
                stat_info_dict["second_unit_id"] = last_dispose_act_inst_dict["unit_id"]
                stat_info_dict["second_unit_name"] = last_dispose_act_inst_dict["unit_name"]
                stat_info_dict["first_unit_id"] = first_unit_id
                stat_info_dict["first_unit_name"] = sysInfo.get_data("unit")[first_unit_id]["unit_name"]

# 督查阶段采集
def __extend_supervise_info(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    supervise_actdef_ids = sysInfo.get_data("supervise_actdef_ids") if sysInfo.get_data("supervise_actdef_ids") else [0]
    last_supervise_act_inst_dict = {}
    if rec_info["act_property_id"] > 10:
        stat_info_dict["supervise_num"] = 1
        stat_info_dict["intime_supervise_num"] = 1
        supervise_act_inst_list = filter(lambda x: x["act_def_id"] in supervise_actdef_ids and x["item_type_id"] in (610,), act_inst_list)
        if supervise_act_inst_list:
            supervise_act_inst_list.sort(key=lambda x: x["create_time"])
            last_supervise_act_inst_dict = supervise_act_inst_list[-1]
            if last_supervise_act_inst_dict["end_time"] and last_supervise_act_inst_dict["bundle_deadline"] and last_supervise_act_inst_dict["end_time"] > last_supervise_act_inst_dict["bundle_deadline"]:
                stat_info_dict["intime_supervise_num"] = 0
    elif rec_info["act_property_id"] in (9, 10):
        stat_info_dict["to_supervise_num"] = 1
        supervise_act_inst_list = filter(lambda x: x["act_def_id"] in supervise_actdef_ids, act_inst_list)
        if supervise_act_inst_list:
            supervise_act_inst_list.sort(key=lambda x: x["create_time"])
            last_supervise_act_inst_dict = supervise_act_inst_list[-1]
    # 督查阶段信息
    if last_supervise_act_inst_dict:
        stat_info_dict["supervise_human_id"] = last_supervise_act_inst_dict["human_id"]
        stat_info_dict["supervise_human_name"] = last_supervise_act_inst_dict["human_name"]
        stat_info_dict["supervise_role_id"] = last_supervise_act_inst_dict["role_id"]

def __extend_check_info(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    patrol_task_list = recInfo.get_data("patrol_task_list")
    check_actdef_ids = sysInfo.get_data("check_actdef_ids") if sysInfo.get_data("check_actdef_ids") else [0]
    if rec_info["act_property_id"] > 13 or rec_info["act_property_id"] in (12,):
        stat_info_dict["need_send_check_num"] = 1
        stat_info_dict["check_num"] = 1
        stat_info_dict["check_trans_num"] = 1
        check_act_inst_list = filter(lambda x: x["act_def_id"] in check_actdef_ids and x["item_type_id"] in (610,), act_inst_list)
        if check_act_inst_list:
            check_act_inst_list.sort(key=lambda x: x["create_time"])
            last_check_act_inst_dict = check_act_inst_list[-1]
            stat_info_dict["check_trans_human_id"] = last_check_act_inst_dict["human_id"]
            stat_info_dict["check_trans_human_name"] = last_check_act_inst_dict["human_name"]
            stat_info_dict["check_trans_role_id"] = last_check_act_inst_dict["role_id"]

    if patrol_task_list:
        check_patrol_task_list = filter(lambda x: x["task_type"] == 3, patrol_task_list)
        if "dispose_end_time" in stat_info_dict and stat_info_dict["dispose_end_time"]:
            check_patrol_task_list = filter(lambda x: x["task_type"] == 3 and x["create_time"] >= stat_info_dict["dispose_end_time"], patrol_task_list)
            if rec_info["act_property_id"] > 13 or rec_info["act_property_id"] in (12,):
                check_patrol_task_list = filter(lambda x: x["done_flag"] == 1 and x["task_type"] == 3, patrol_task_list)
        if check_patrol_task_list:
            stat_info_dict["send_check_num"] = 1
            check_patrol_task_list.sort(key=lambda x: x["create_time"])
            check_patrol_task_dict = check_patrol_task_list[-1]
            stat_info_dict["send_check_time"] = check_patrol_task_dict["create_time"]
            if check_patrol_task_dict["human_id"] in sysInfo.get_data("human"):
                send_check_human = sysInfo.get_data("human")[check_patrol_task_dict["human_id"]]
                stat_info_dict["send_check_human_id"] = send_check_human["human_id"]
                stat_info_dict["send_check_human_name"] = send_check_human["human_name"]
            if check_patrol_task_dict["done_flag"] == 1:
                stat_info_dict["check_num"] = 1
                stat_info_dict["intime_check_num"] = 1
                stat_info_dict["check_time"] = check_patrol_task_dict["done_time"]
                check_used = get_minutes(sysInfo.get_data("timing_dict"), sysConst.default_sys_time_id, check_patrol_task_dict["create_time"], check_patrol_task_dict["done_time"])
                if rec_info["district_id"] == 14 and check_used > sysConst.cixi_check_limit or check_used > sysConst.check_limit:
                    stat_info_dict["intime_check_num"] = 0
                stat_info_dict["overtime_check_num"] = stat_info_dict["check_num"] - stat_info_dict["intime_check_num"]
                if check_patrol_task_dict["card_id"] in sysInfo.get_data("patrol_card"):
                    check_patrol = sysInfo.get_data("patrol_card")[check_patrol_task_dict["card_id"]]
                    stat_info_dict["check_patrol_id"] = check_patrol["patrol_id"]
                    stat_info_dict["check_patrol_name"] = check_patrol["patrol_name"]

# 值班长结案阶段
def __extend_human_archive(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    stat_info_dict["need_human_archive_num"] = 1
    archive_actdef_ids = sysInfo.get_data("archive_actdef_ids") if sysInfo.get_data("archive_actdef_ids") else [0]
    last_archive_inst_dict = {}
    if rec_info["act_property_id"] == 101:
        stat_info_dict["human_archive_num"] = 1
        stat_info_dict["intime_human_archive_num"] = 1
        archive_inst_list = filter(lambda x: x["act_def_id"] in archive_actdef_ids and x["item_type_id"] == 800, act_inst_list)
        if archive_inst_list:
            archive_inst_list.sort(key=lambda x: x["create_time"])
            last_archive_inst_dict = archive_inst_list[-1]
            if rec_info["archive_time"] and last_archive_inst_dict["deadline_time"] and rec_info["archive_time"] > last_archive_inst_dict["deadline_time"]:
                stat_info_dict["intime_human_archive_num"] = 0

    elif rec_info["act_property_id"] in (12, 14):
        stat_info_dict["to_human_archive_num"] = 1
        archive_inst_list = filter(lambda x: x["act_def_id"] in archive_actdef_ids, act_inst_list)
        if archive_inst_list:
            archive_inst_list.sort(key=lambda x: x["create_time"])
            last_archive_inst_dict = archive_inst_list[-1]

    if last_archive_inst_dict:
        stat_info_dict["archive_human_id"] = last_archive_inst_dict["human_id"]
        stat_info_dict["archive_human_name"] = last_archive_inst_dict["human_name"]
        stat_info_dict["archive_role_id"] = last_archive_inst_dict["role_id"]

# 作废阶段时采集
def __extend_cancel_info(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    accept_actdef_ids = sysInfo.get_data("accept_actdef_ids") if sysInfo.get_data("accept_actdef_ids") else [0]
    inst_actdef_ids = sysInfo.get_data("inst_actdef_ids") if sysInfo.get_data("inst_actdef_ids") else [0]
    # cancel_act_inst = recutils.get_last_trans_act(act_inst_list, accept_actdef_ids+inst_actdef_ids, (814,))
    cancel_act_inst_list = filter(lambda x: x["item_type_id"] == 814, act_inst_list)
    if cancel_act_inst_list:
        cancel_act_inst_list.sort(key=lambda x: x["create_time"])
        if cancel_act_inst_list[-1]["act_def_id"] in accept_actdef_ids:
            # 不予受理数
            stat_info_dict["not_operate_num"] = 1
            stat_info_dict["operate_human_id"] = cancel_act_inst_list[-1]["human_id"]
            stat_info_dict["operate_human_name"] = cancel_act_inst_list[-1]["human_name"]
            stat_info_dict["operate_role_id"] = cancel_act_inst_list[-1]["role_id"]
        elif cancel_act_inst_list[-1]["act_def_id"] in inst_actdef_ids:
            # 不予立案数
            stat_info_dict["not_inst_num"] = 1
            stat_info_dict["inst_human_id"] = cancel_act_inst_list[-1]["human_id"]
            stat_info_dict["inst_human_name"] = cancel_act_inst_list[-1]["human_name"]
            stat_info_dict["inst_role_id"] = cancel_act_inst_list[-1]["role_id"]
        else:
            stat_info_dict["cancel_num"] = 1
            stat_info_dict["cancel_human_id"] = cancel_act_inst_list[-1]["human_id"]
            stat_info_dict["cancel_human_name"] = cancel_act_inst_list[-1]["human_name"]
            stat_info_dict["cancel_role_id"] = cancel_act_inst_list[-1]["role_id"]
    # else:
    #     dispatch_actdef_ids = sysInfo.get_data("dispatch_actdef_ids") if sysInfo.get_data("dispatch_actdef_ids") else [0]
    #     cancel_act_inst = recutils.get_last_trans_act(act_inst_list, dispatch_actdef_ids, (814,))
    #     if cancel_act_inst:
    #         stat_info_dict["cancel_num"] = 1
    #         stat_info_dict["cancel_human_id"] = cancel_act_inst["human_id"]
    #         stat_info_dict["cancel_human_name"] = cancel_act_inst["human_name"]
    #         stat_info_dict["cancel_role_id"] = cancel_act_inst["role_id"]

def __extend_special_info(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    wf_postpone_time_list = recInfo.get_data("wf_postpone_time_list")
    wf_item_inst_list = recInfo.get_data("wf_item_inst_list")
    # 延期采集
    dispose_unit_id_set = []
    if "second_unit_id" in stat_info_dict and stat_info_dict["second_unit_id"]:
        dispose_unit_id_set.append(stat_info_dict["second_unit_id"])
    if "first_unit_id" in stat_info_dict and stat_info_dict["first_unit_id"]:
        dispose_unit_id_set.append(stat_info_dict["first_unit_id"])
    dispose_act_id_set = [x["act_id"] for x in act_inst_list if x["unit_id"] in dispose_unit_id_set]
    if wf_postpone_time_list:
        real_postpone_time_list = filter(lambda x: x["act_id"] in dispose_act_id_set, wf_postpone_time_list)
        if real_postpone_time_list:
            stat_info_dict["multi_postpone_num"] = len(real_postpone_time_list)
            stat_info_dict["postpone_num"] = 1
            stat_info_dict["postpone_hours"] = sum([x["time_num"] for x in real_postpone_time_list])

    # 挂账(缓办)采集
    if "real_act_property_id" in rec_info and rec_info["real_act_property_id"] == 103:
        stat_info_dict["hang_num"] = 1
    hang_item_inst_list = filter(lambda x: x["item_type_id"] == 810, wf_item_inst_list)
    if hang_item_inst_list:
        stat_info_dict["his_hang_num"] = 1
        stat_info_dict["multi_hang_num"] = len(hang_item_inst_list)