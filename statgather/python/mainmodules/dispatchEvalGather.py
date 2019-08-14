# coding: utf-8
import sys
sys.path.append("..")
from tools.utils import copy_dict2dict as copy, insert_many
from datetime import datetime
from tools.systemUtils import get_human_byID, get_region_byID
import logging
"""
    zwx 2016-04-13 main
    派遣员工作量采集
    应派遣数 派遣数 按时派遣数 超时派遣数 超时未派遣数
    应督查数 督查数 按时督查数 超时督查数 超时未督查数
"""

def execute(stat_cur, biz_cur, recInfo, sysInfo):
    logger = logging.getLogger("main.mainmodules.dispatchEvalGather")
    dispatch_eval_list = []
    rec_info = recInfo.get_data("rec_info")
    rec_id = recInfo.get_data("rec_id")
    act_inst_list = recInfo.get_data("act_inst_list")
    dispatch_actdef_ids = sysInfo.get_data("dispatch_actdef_ids") if sysInfo.get_data("dispatch_actdef_ids") else [0]
    supervise_actdef_ids = sysInfo.get_data("supervise_actdef_ids") if sysInfo.get_data("supervise_actdef_ids") else [0]
    for act_inst in act_inst_list:
        dispatch_eval_dict = {}
        try:
            # 派遣节点
            if act_inst["act_def_id"] in dispatch_actdef_ids and act_inst["item_type_id"] in (610,):
                # 派遣批转
                copy(rec_info, dispatch_eval_dict)
                dispatch_eval_dict["execute_time"] = act_inst["end_time"]
                dispatch_eval_dict["dispatch_num"] = 1
                dispatch_eval_dict["need_dispatch_num"] = 1
                # 结束时间 > 截止时间，则记为超期派遣数
                if act_inst["end_time"] and act_inst["deadline_time"] and act_inst["end_time"] > act_inst["deadline_time"]:
                    dispatch_eval_dict["overtime_dispatch_num"] = 1
                else:
                    dispatch_eval_dict["intime_dispatch_num"] = 1
            # 督查节点
            elif act_inst["act_def_id"] in supervise_actdef_ids and act_inst["item_type_id"] in (610,):
                # 督查批转
                copy(rec_info, dispatch_eval_dict)
                dispatch_eval_dict["execute_time"] = act_inst["end_time"]
                dispatch_eval_dict["need_dc_num"] = 1
                dispatch_eval_dict["dc_num"] = 1
                # 按时超时督查数采集
                if act_inst["end_time"] and act_inst["end_time"] > act_inst["deadline_time"]:
                    dispatch_eval_dict["overtime_dc_num"] = 1
                else:
                    dispatch_eval_dict["intime_dc_num"] = 1
            if dispatch_eval_dict and act_inst["human_id"] in sysInfo.get_data("human"):
                dispatch_eval_dict["action_start_time"] = act_inst["create_time"]
                dispatch_eval_dict["action_end_time"] = act_inst["end_time"]
                dispatch_human = sysInfo.get_data("human")[act_inst["human_id"]]
                dispatch_eval_dict["human_id"] = act_inst["human_id"]
                dispatch_eval_dict["human_name"] = dispatch_human["human_name"]
                dispatch_eval_dict["role_id"] = act_inst["role_id"]
                if dispatch_human["region_id"] in sysInfo.get_data("region"):
                    dispatch_eval_dict["human_region_id"] = dispatch_human["region_id"]
                    dispatch_eval_dict["human_region_name"] = sysInfo.get_data("region")[dispatch_human["region_id"]]["region_name"]
        except Exception, e:
            dispatch_eval_dict = {}
            logger.error(u"派遣员工作量采集失败[rec_id = %s]: %s" % (rec_id, str(e)))

        # 工作量字典非空则插入List
        if dispatch_eval_dict:
            dispatch_eval_list.append(dispatch_eval_dict)
    # 待派遣
    try:
        dispatch_eval_dict = {}
        now = datetime.now()
        # 待派遣
        if len(act_inst_list) > 0:
            act_inst = act_inst_list[len(act_inst_list) - 1]
            if act_inst["act_def_id"] in dispatch_actdef_ids and not act_inst_list[len(act_inst_list) - 1]["item_type_id"] and not act_inst_list[len(act_inst_list) - 1]["end_time"]:
                copy(rec_info, dispatch_eval_dict)
                dispatch_eval_dict["need_dispatch_num"] = 1
                dispatch_eval_dict["to_dispatch_num"] = 1
                if act_inst["deadline_time"] and now > act_inst["deadline_time"]:
                    dispatch_eval_dict["overtime_to_dispatch_num"] = 1
            elif act_inst["act_def_id"] in supervise_actdef_ids and not act_inst_list[len(act_inst_list) - 1]["item_type_id"] and not act_inst_list[len(act_inst_list) - 1]["end_time"]:
                copy(rec_info, dispatch_eval_dict)
                dispatch_eval_dict["need_dc_num"] = 1
                dispatch_eval_dict["to_dc_num"] = 1
                if act_inst["deadline_time"] and now > act_inst["deadline_time"]:
                    dispatch_eval_dict["overtime_to_dc_num"] = 1
            if dispatch_eval_dict and act_inst_list["human_id"] in sysInfo.get_data("human"):
                dispatch_eval_dict["execute_time"] = act_inst["create_time"]
                dispatch_eval_dict["action_start_time"] = act_inst["create_time"]
                dispatch_eval_dict["action_end_time"] = act_inst["create_time"]
                dispatch_human = sysInfo.get_data("human")[act_inst["human_id"]]
                dispatch_eval_dict["human_id"] = act_inst["human_id"]
                dispatch_eval_dict["human_name"] = dispatch_human["human_name"]
                dispatch_eval_dict["role_id"] = act_inst["role_id"]
                if dispatch_human["region_id"] in sysInfo.get_data("region"):
                    dispatch_eval_dict["human_region_id"] = dispatch_human["region_id"]
                    dispatch_eval_dict["human_region_name"] = sysInfo.get_data("region")[dispatch_human["region_id"]][
                        "region_name"]
                dispatch_eval_list.append(dispatch_eval_dict)

    except Exception, e:
        logger.error(u"待派遣工作量采集失败[rec_id = %s]: %s" % (rec_id, str(e)))

    # 入库
    if dispatch_eval_list:
        # 主键策略
        i = 1
        for dispatch_eval_dict in dispatch_eval_list:
            dispatch_eval_dict["dispatcher_eval_id"] = rec_id*100 + i
            i += 1
        from maintable.dispatchEval import table_name, field
        sql = "delete from %(tableName)s where rec_id = %(rec_id)s"
        param = {"tableName": table_name, "rec_id": rec_id}
        stat_cur.execute(sql % param)
        insert_many(stat_cur, table_name, dispatch_eval_list, field)

