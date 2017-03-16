#coding: utf-8
"""
    zwx 2016-05-26
    专业部门工作量采集 均从wf_act_inst中取
    被派遣数 回退数 延期数 缓办数(挂账数) 作废数
"""
import sys
sys.path.append("..")
from tools.utils import copy_dict2dict as copy, insert_many
import tools.systemUtils as systemUtils
from maintable.unitWorkloadEval import table_name, field
import tools.recutils as recutils
import logging

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
                # 其他
                else:
                    unit_workload_eval_dict = {}

            if unit_workload_eval_dict:
                copy(rec_info, unit_workload_eval_dict)
                unit_workload_eval_dict["execute_time"] = act_inst_dict["end_time"] if act_inst_dict["end_time"] else act_inst_dict["create_time"]
                unit_workload_eval_dict["action_start_time"] = act_inst_dict["create_time"]
                unit_workload_eval_dict["action_end_time"] = act_inst_dict["end_time"] if act_inst_dict["end_time"] else act_inst_dict["create_time"]

                dispose_act_def_id = act_inst_dict["act_def_id"]
                dispose_role_id = act_inst_dict["role_id"]
                # 部门岗位信息
                dispose_role = systemUtils.get_role_byID(biz_cur, dispose_role_id)
                dispose_role_name = dispose_role["role_name"]
                dispose_unit_id = dispose_role["unit_id"]
                # 部门信息
                dispose_unit = systemUtils.get_unit_byID(biz_cur, dispose_unit_id)    
                dispose_unit_name = dispose_unit["unit_name"]
                # 专业部门所属区域
                dispose_region_id = dispose_unit["region_id"]
                dispose_region_name = dispose_unit["region_name"]
                dispose_street_id = None
                dispose_street_name = None
                dispose_region = systemUtils.get_region_byID(biz_cur, dispose_region_id)
                if dispose_region and dispose_region["region_type"] == 3:
                    dispose_street_id = dispose_region["region_id"]
                    dispose_street_name = dispose_region["region_name"]
                    dispose_region_id = dispose_region["senior_id"]
                    temp_region = systemUtils.get_region_byID(biz_cur, dispose_region_id)
                    dispose_region_name = temp_region["region_name"]

                # 初始化一二级部门信息
                first_unit_id = None
                first_unit_name = None
                second_unit_id = None
                second_unit_name = None
                dispatch_actdef_ids = sysInfo.get_data("dispatch_actdef_ids") if sysInfo.get_data("dispatch_actdef_ids") else [0]
                if dispose_act_def_id in (184, 185):
                    # 区、区县二级部门处置
                    second_unit_id = dispose_unit_id
                    second_unit_name = dispose_unit_name
                    first_unit_id = dispose_unit["senior_id"]
                    first_unit_name = dispose_unit["senior_name"]
                elif dispose_act_def_id in (183,):
                    # 市二级部门处置
                    second_unit_id = dispose_unit_id
                    second_unit_name = dispose_unit_name
                    first_unit_id = dispose_unit["senior_id"]
                    first_unit_name = dispose_unit["senior_name"]
                elif dispose_act_def_id in (169, 173, 186):
                    # 区、区县、中心镇部门处置
                    first_unit_id = dispose_unit_id
                    first_unit_name = dispose_unit_name
                elif dispose_act_def_id in (160,):
                    # 市专业部门处置则需要判断是否由二级部门批转过来
                    dispatch_act = recutils.get_last_trans_act(act_inst_list, dispatch_actdef_ids, (610,))
                    dispatch_create_time = dispatch_act["create_time"]
                    dispose_create_time = act_inst_dict["create_time"]
                    second_dispose_act = recutils.get_between_last_trans_act(act_inst_list, (183,), dispatch_create_time, dispose_create_time, (610,))
                    first_unit_id = dispose_unit_id
                    first_unit_name = dispose_unit_name
                    if second_dispose_act:
                        second_role_id = second_dispose_act["role_id"]
                        # 二级部门处置岗位
                        second_role = systemUtils.get_role_byID(biz_cur, second_role_id)
                        second_unit_id = second_role["unit_id"]
                        second_unit_name = second_role["unit_name"]
                # 更新到stat_info_dict中        
                unit_workload_eval_dict["dispose_unit_id"] = second_unit_id if second_unit_id else first_unit_id
                unit_workload_eval_dict["dispose_unit_name"] = second_unit_name if second_unit_name else first_unit_name
                unit_workload_eval_dict["dispose_region_id"] = dispose_region_id
                unit_workload_eval_dict["dispose_region_name"] = dispose_region_name
                unit_workload_eval_dict["first_unit_id"] = first_unit_id
                unit_workload_eval_dict["first_unit_name"] = first_unit_name
                unit_workload_eval_dict["second_unit_id"] = second_unit_id
                unit_workload_eval_dict["second_unit_name"] = second_unit_name
                unit_workload_eval_dict["dispose_street_id"] = dispose_street_id
                unit_workload_eval_dict["dispose_street_name"] = dispose_street_name

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