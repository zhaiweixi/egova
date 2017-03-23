# coding: utf-8
"""
    zwx 2016-05-26
    专业部门工作量采集 均从wf_act_inst中取
    被派遣数 回退数 延期数 缓办数(挂账数) 作废数
"""
import sys
sys.path.append("..")
from tools.utils import copy_dict2dict as copy, insert_many
from maintable.unitWorkloadEval import table_name, field

def execute(stat_cur, biz_cur, recInfo, sysInfo):
    unit_workload_eval_list = []
    rec_id = recInfo.get_data("rec_id")
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    dispose_actdef_ids = sysInfo.get_data("dispose_actdef_ids") if sysInfo.get_data("dispose_actdef_ids") else [0]
    if act_inst_list:
        for act_inst_dict in act_inst_list:
            unit_workload_eval_dict = {}
            if act_inst_dict["act_def_id"] in dispose_actdef_ids:
                # 回退
                if act_inst_dict["item_type_id"] and act_inst_dict["item_type_id"] in (626, ):
                    unit_workload_eval_dict["back_num"] = 1
                    if act_inst_dict["end_time"] and act_inst_dict["deadline_time"] and act_inst_dict["end_time"] > act_inst_dict["deadline_time"]:
                        unit_workload_eval_dict["overtime_back_num"] = 1
                # 挂账
                elif act_inst_dict["item_type_id"] and act_inst_dict["item_type_id"] in (810, ):
                    unit_workload_eval_dict["hang_num"] = 1
                # 延期
                elif act_inst_dict["item_type_id"] and act_inst_dict["item_type_id"] in (606, ):
                    unit_workload_eval_dict["postpone_num"] = 1

            if unit_workload_eval_dict:
                copy(rec_info, unit_workload_eval_dict)
                unit_workload_eval_dict["execute_time"] = act_inst_dict["end_time"] if act_inst_dict["end_time"] else act_inst_dict["create_time"]
                unit_workload_eval_dict["action_start_time"] = act_inst_dict["create_time"]
                unit_workload_eval_dict["action_end_time"] = act_inst_dict["end_time"] if act_inst_dict["end_time"] else act_inst_dict["create_time"]

                unit_workload_eval_dict["dispose_unit_id"] = act_inst_dict["unit_id"]
                unit_workload_eval_dict["dispose_unit_name"] = act_inst_dict["unit_name"]
                if act_inst_dict["unit_id"] in sysInfo.get_data("unit"):
                    dispose_unit = sysInfo.get_data("unit")[act_inst_dict["unit_id"]]
                    if dispose_unit["region_id"] in sysInfo.get_data("region"):
                        unit_workload_eval_dict["dispose_region_id"] = dispose_unit["region_id"]
                        unit_workload_eval_dict["dispose_region_name"] = sysInfo.get_data("region")[dispose_unit["region_id"]]["region_name"]

                unit_workload_eval_list.append(unit_workload_eval_dict)
    # 入库
    if unit_workload_eval_list:
        i = 1
        for unit_workload_eval_dict in unit_workload_eval_list:
            unit_workload_eval_dict["unit_workload_eval_id"] = rec_id*100 + i
            i += 1
        # 入库前先删除
        param = {"table_name": table_name, "rec_id": rec_id}
        stat_cur.execute("delete from %(table_name)s where rec_id = %(rec_id)s" % param)
        insert_many(stat_cur, table_name, unit_workload_eval_list, field)