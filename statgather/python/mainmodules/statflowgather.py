# coding: utf-8

import sys
sys.path.append("..")
import logging
import traceback
from maintable import statflowinfo
from tools.utils import insert_many
from tools.timing import get_minutes
import constant.sysConst as sysconst

def execute(biz_cur, stat_cur, recinfo, sysinfo):
    stat_flow_info_list = []
    logger = logging.getLogger("")
    rec_info = recinfo.get_data("rec_info")
    rec_id = rec_info["rec_id"]
    act_inst_list = recinfo.get_data("act_inst_list")
    patrol_task_list = recinfo.get_data("patrol_task_list")
    flow_act_inst_list = filter(lambda x: x["item_type_id"] in (610, 620, 626, 800), act_inst_list)
    accept_actdef_ids = sysinfo.get_data("accept_actdef_ids")
    inst_actdef_ids = sysinfo.get_data("inst_actdef_ids")
    dispatch_actdef_ids = sysinfo.get_data("dispatch_actdef_ids")
    dispose_actdef_ids = sysinfo.get_data("dispose_actdef_ids")
    supervise_actdef_ids = sysinfo.get_data("supervise_actdef_ids")
    check_actdef_ids = sysinfo.get_data("check_actdef_ids")
    archive_actdef_ids = sysinfo.get_data("archive_actdef_ids")
    if flow_act_inst_list:
        flow_act_inst_list.sort(key=lambda x: x["create_time"])
        for flow_act_inst_dict in flow_act_inst_list:
            stat_flow_info_dict = {}
            stat_flow_info_dict.update(rec_info)
            if flow_act_inst_dict["act_def_id"] in (accept_actdef_ids + inst_actdef_ids):
                stat_flow_info_dict["cur_stage_id"] = 2
                stat_flow_info_dict["cur_stage_name"] = u"立案环节"
                # 专业部门为空
                if rec_info["act_property_id"] < 7:
                    stat_flow_info_dict["stat_flag"] = 0
            elif flow_act_inst_dict["act_def_id"] in dispatch_actdef_ids:
                stat_flow_info_dict["cur_stage_id"] = 3
                stat_flow_info_dict["cur_stage_name"] = u"派遣环节"
            elif flow_act_inst_dict["act_def_id"] in dispose_actdef_ids:
                stat_flow_info_dict["cur_stage_id"] = 4
                stat_flow_info_dict["cur_stage_name"] = u"处置环节"
            elif flow_act_inst_dict["act_def_id"] in supervise_actdef_ids:
                stat_flow_info_dict["cur_stage_id"] = 5
                stat_flow_info_dict["cur_stage_name"] = u"督查环节"
            elif flow_act_inst_dict["act_def_id"] in check_actdef_ids:
                stat_flow_info_dict["cur_stage_id"] = 6
                stat_flow_info_dict["cur_stage_name"] = u"核查环节"
                # 核查环节对核查任务有特殊处理
                stat_flow_info_dict["act_id"] = flow_act_inst_dict["act_id"]
                stat_flow_info_dict["start_time"] = flow_act_inst_dict["start_time"]
                stat_flow_info_dict["end_time"] = flow_act_inst_dict["end_time"]
                stat_flow_info_dict["deadline_time"] = flow_act_inst_dict["deadline_time"]
                stat_flow_info_dict["rs_check_used"] = flow_act_inst_dict["act_used"]
                # 环节用时也采集
                stat_flow_info_dict["flow_used"] = flow_act_inst_dict["act_used"]
                stat_flow_info_dict["overtime_flag"] = 0
                if flow_act_inst_dict["act_used"] and flow_act_inst_dict["act_limit"] and flow_act_inst_dict["act_used"] > flow_act_inst_dict["act_limit"]:
                    stat_flow_info_dict["overtime_flag"] = 1

                check_patrol_task_list = filter(lambda x: x["task_type"] == 3 and flow_act_inst_dict["create_time"] < x["create_time"] < flow_act_inst_dict["end_time"] and x["done_flag"] == 1 and x["cancel_flag"] == 0, patrol_task_list)
                if check_patrol_task_list:
                    check_patrol_task_list.sort(key=lambda x: x["patrol_task_id"])
                    for check_patrol_task_dict in check_patrol_task_list:
                        temp_stat_flow_info_dict = {}
                        temp_stat_flow_info_dict.update(rec_info)
                        temp_stat_flow_info_dict["cur_stage_id"] = 6
                        temp_stat_flow_info_dict["cur_stage_name"] = u"核查环节"
                        temp_stat_flow_info_dict["flow_num"] = 0
                        temp_stat_flow_info_dict["act_id"] = check_patrol_task_dict["patrol_task_id"]
                        temp_stat_flow_info_dict["start_time"] = check_patrol_task_dict["create_time"]
                        temp_stat_flow_info_dict["end_time"] = check_patrol_task_dict["done_time"]
                        check_used = get_minutes(sysinfo.get_data("timing_dict"), sysconst.default_sys_time_id, check_patrol_task_dict["create_time"], check_patrol_task_dict["done_time"])
                        temp_stat_flow_info_dict["check_used"] = check_used
                        temp_stat_flow_info_dict["overtime_flag"] = 0
                        if rec_info["district_id"] == 14:
                            if check_used > sysconst.cixi_check_limit:
                                temp_stat_flow_info_dict["overtime_flag"] = 1
                        else:
                            if check_used > sysconst.check_limit:
                                temp_stat_flow_info_dict["overtime_flag"] = 1
                        stat_flow_info_list.append(temp_stat_flow_info_dict)

                stat_flow_info_list.append(stat_flow_info_dict)
                continue
            elif flow_act_inst_dict["act_def_id"] in archive_actdef_ids:
                stat_flow_info_dict["cur_stage_id"] = 7
                stat_flow_info_dict["cur_stage_name"] = u"结案环节"
            else:
                continue

            if flow_act_inst_dict["act_def_id"] not in check_actdef_ids:
                stat_flow_info_dict["act_id"] = flow_act_inst_dict["act_id"]
                stat_flow_info_dict["start_time"] = flow_act_inst_dict["start_time"]
                stat_flow_info_dict["end_time"] = flow_act_inst_dict["end_time"]
                stat_flow_info_dict["deadline_time"] = flow_act_inst_dict["deadline_time"]
                stat_flow_info_dict["flow_used"] = flow_act_inst_dict["act_used"]
                stat_flow_info_dict["overtime_flag"] = 0
                if flow_act_inst_dict["act_used"] and flow_act_inst_dict["act_limit"] and flow_act_inst_dict["act_used"] > flow_act_inst_dict["act_limit"]:
                    stat_flow_info_dict["overtime_flag"] = 1

            stat_flow_info_list.append(stat_flow_info_dict)

    sql = "delete from %(table_name)s where rec_id = %(rec_id)s"
    param = {"table_name": statflowinfo.table_name, "rec_id": rec_id}
    try:
        stat_cur.execute(sql % param)
        if stat_flow_info_list:
            i = 1
            for stat_flow_info_dict in stat_flow_info_list:
                stat_flow_info_dict["flow_id"] = rec_id * 1000 + i
                i += 1
        insert_many(cur=stat_cur, table_name=statflowinfo.table_name, field_tuple=statflowinfo.field, data_list=stat_flow_info_list)
    except:
        logger.error(u"to_stat_flow_info采集失败:%s" % traceback.format_exc())
