#coding: utf-8
"""
    zwx 2016-05-27
    增加采集特殊指标
    复杂的采集过程外挂脚本处理,例如处置阶段,简单阶段在此脚本中执行
"""
import sys
sys.path.append("..")
from tools.utils import insert_one, insert_many, copy_dict2dict as copy
import tools.recutils as recutils
import logging
import settings

def get_stat_info_dict(stat_cur, biz_cur, recInfo, sysInfo):
    logger = logging.getLogger("main.mainmodules.statInfoGather")
    rec_info = recInfo.get_data("rec_info")
    act_property_id = rec_info["act_property_id"] if rec_info["act_property_id"] else 0
    stat_info_dict = {}
    copy(rec_info, stat_info_dict)
    # 采集上报信息
    __extendReportInfo(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
    if act_property_id and act_property_id not in (102,):
        # 受理阶段
        import statInfoGather.accept as accept
        accept.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集立案阶段
        if act_property_id > 2:
            __extendInstInfo(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集派遣阶段
        if act_property_id > 4:
            __extendDispatchInfo(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集处置阶段指标
        if act_property_id > 6:
            import statInfoGather.dispose as dispose
            dispose.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集督查阶段指标
        if act_property_id > 8:
            __extendSuperviseInfo(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集核查阶段指标
        if act_property_id > 10: 
            import statInfoGather.check as check
            check.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集值班长结案阶段指标
        if act_property_id == 12 or act_property_id > 13: 
            __extendHumanArchive(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
        # 需采集办结阶段指标
        if act_property_id == 101:
            stat_info_dict["archive_num"] = 1
            stat_info_dict["intime_archive_num"] = stat_info_dict["intime_dispose_num"] if stat_info_dict.has_key("intime_dispose_num") else 1
            stat_info_dict["overtime_archive_num"] = stat_info_dict["overtime_dispose_num"] if stat_info_dict.has_key("overtime_dispose_num") else 0
    # 作废阶段       
    elif act_property_id == 102:
        __extendCancelInfo(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
    
    # 采集特殊指标 延期 挂账 回退
    try:
        import statInfoGather.special as special
        special.execute(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
    except Exception, e:
        logger.error(u"特殊指标采集失败: %s " % str(e))
    return stat_info_dict

# 采集上报阶段信息
def __extendReportInfo(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
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

# 立案阶段采集
def __extendInstInfo(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    inst_actdef_ids = sysInfo.get_data("inst_actdef_ids") if sysInfo.get_data("inst_actdef_ids") else [0]

    if rec_info["act_property_id"] > 4:
        stat_info_dict["inst_num"] = 1
        stat_info_dict["need_dispatch_num"] = 1
        inst_act_inst = recutils.get_last_trans_act(act_inst_list, inst_actdef_ids, (610,))
        if inst_act_inst:
            stat_info_dict["inst_time"] = inst_act_inst["end_time"]
            if inst_act_inst["end_time"] > inst_act_inst["deadline_time"]:
                stat_info_dict["intime_inst_num"] = 0
            else:
                stat_info_dict["intime_inst_num"] = 1
    elif rec_info["act_property_id"] in (3, 4):
        stat_info_dict["to_inst_num"] = 1
        inst_act_inst = recutils.get_last_act_inst(act_inst_list, inst_actdef_ids)
    # 立案人信息
    if inst_act_inst:
        stat_info_dict["inst_human_id"] = inst_act_inst["human_id"]
        stat_info_dict["inst_human_name"] = inst_act_inst["human_name"]
        stat_info_dict["inst_role_id"] = inst_act_inst["role_id"]

# 派遣阶段采集
def __extendDispatchInfo(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    dispatch_actdef_ids = sysInfo.get_data("dispatch_actdef_ids") if sysInfo.get_data("dispatch_actdef_ids") else [0]
    dispatch_act_inst = None
    if rec_info["act_property_id"] > 6:
        stat_info_dict["dispatch_num"] = 1
        stat_info_dict["need_dispose_num"] = 1
        dispatch_act_inst = recutils.get_last_trans_act(act_inst_list, dispatch_actdef_ids, (610,))
        if dispatch_act_inst:
            stat_info_dict["dispatch_time"] = dispatch_act_inst["end_time"]
            if dispatch_act_inst["end_time"] and dispatch_act_inst["end_time"] > dispatch_act_inst["deadline_time"]:
                stat_info_dict["intime_dispatch_num"] = 0
                stat_info_dict["overtime_dispatch_num"] = 1
            else:
                stat_info_dict["intime_dispatch_num"] = 1
                stat_info_dict["overtime_dispatch_num"] = 0
    elif rec_info["act_property_id"] in (5, 6):
        stat_info_dict["to_dispatch_num"] = 1
        dispatch_act_inst = recutils.get_last_act_inst(act_inst_list, dispatch_actdef_ids)
    if dispatch_act_inst:
        stat_info_dict["dispatch_human_id"] = dispatch_act_inst["human_id"]
        stat_info_dict["dispatch_human_name"] = dispatch_act_inst["human_name"]
        stat_info_dict["dispatch_role_id"] = dispatch_act_inst["role_id"]

# 督查阶段采集
def __extendSuperviseInfo(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    supervise_actdef_ids = sysInfo.get_data("supervise_actdef_ids") if sysInfo.get_data("supervise_actdef_ids") else [0]
    supervise_act_inst = None
    if rec_info["act_property_id"] > 10:
        stat_info_dict["supervise_num"] = 1
        supervise_act_inst = recutils.get_last_trans_act(act_inst_list, supervise_actdef_ids, (610,))
        if supervise_act_inst:
            if supervise_act_inst["end_time"] and supervise_act_inst["deadline_time"] and supervise_act_inst["end_time"] > supervise_act_inst["deadline_time"]:
                stat_info_dict["intime_supervise_num"] = 0
                stat_info_dict["supervise_time"] = supervise_act_inst["end_time"]
            else:
                stat_info_dict["intime_supervise_num"] = 1
            if supervise_act_inst["end_time"]:
                stat_info_dict["supervise_time"] = supervise_act_inst["end_time"]
        else:
            # 无督查动作则暂时把按时督查数置为1
            stat_info_dict["intime_supervise_num"] = 1
    elif rec_info["act_property_id"] in (9, 10):
        stat_info_dict["to_supervise_num"] = 1
        supervise_act_inst = recutils.get_last_act_inst(act_inst_list, supervise_actdef_ids)
    # 督查阶段信息
    if supervise_act_inst:
        stat_info_dict["supervise_human_id"] = supervise_act_inst["human_id"]
        stat_info_dict["supervise_human_name"] = supervise_act_inst["human_name"]
        stat_info_dict["supervise_role_id"] = supervise_act_inst["role_id"]

# 值班长结案阶段
def __extendHumanArchive(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    stat_info_dict["need_human_archive_num"] = 1
    archive_actdef_ids = sysInfo.get_data("archive_actdef_ids") if sysInfo.get_data("archive_actdef_ids") else [0]
    human_archive_act_inst = None
    if rec_info["act_property_id"] == 101:
        human_archive_act_inst = recutils.get_last_trans_act(act_inst_list, archive_actdef_ids, (800,))
        if human_archive_act_inst:
            stat_info_dict["human_archive_num"] = 1
            if rec_info["archive_time"] and human_archive_act_inst["deadline_time"] and rec_info["archive_time"] > human_archive_act_inst["deadline_time"]:
                stat_info_dict["intime_human_archive_num"] = 0
            else:
                stat_info_dict["intime_human_archive_num"] = 1
    elif rec_info["act_property_id"] in (12, 14):
        human_archive_act_inst = recutils.get_last_act_inst(act_inst_list, archive_actdef_ids)
        stat_info_dict["to_human_archive_num"] = 1
        
    if human_archive_act_inst:
        stat_info_dict["archive_human_id"] = human_archive_act_inst["human_id"]
        stat_info_dict["archive_human_name"] = human_archive_act_inst["human_name"]
        stat_info_dict["archive_role_id"] = human_archive_act_inst["role_id"]

# 作废阶段时采集
def __extendCancelInfo(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    accept_actdef_ids = sysInfo.get_data("accept_actdef_ids") if sysInfo.get_data("accept_actdef_ids") else [0]
    inst_actdef_ids = sysInfo.get_data("inst_actdef_ids") if sysInfo.get_data("inst_actdef_ids") else [0]
    cancel_act_inst = recutils.get_last_trans_act(act_inst_list, accept_actdef_ids+inst_actdef_ids, (814,))
    if cancel_act_inst:
        if cancel_act_inst["act_def_id"] in accept_actdef_ids:
            # 不予受理数
            stat_info_dict["not_operate_num"] = 1
            stat_info_dict["operate_human_id"] = cancel_act_inst["human_id"]
            stat_info_dict["operate_human_name"] = cancel_act_inst["human_name"]
            stat_info_dict["operate_role_id"] = cancel_act_inst["role_id"]
        elif cancel_act_inst["act_def_id"] in inst_actdef_ids:
            # 不予立案数
            stat_info_dict["not_inst_num"] = 1
            stat_info_dict["inst_human_id"] = cancel_act_inst["human_id"]
            stat_info_dict["inst_human_name"] = cancel_act_inst["human_name"]
            stat_info_dict["inst_role_id"] = cancel_act_inst["role_id"]
    else:
        dispatch_actdef_ids = sysInfo.get_data("dispatch_actdef_ids") if sysInfo.get_data("dispatch_actdef_ids") else [0]
        cancel_act_inst = recutils.get_last_trans_act(act_inst_list, dispatch_actdef_ids, (814,))
        if cancel_act_inst:
            stat_info_dict["cancel_num"] = 1
            stat_info_dict["cancel_human_id"] = cancel_act_inst["human_id"]
            stat_info_dict["cancel_human_name"] = cancel_act_inst["human_name"]
            stat_info_dict["cancel_role_id"] = cancel_act_inst["role_id"]