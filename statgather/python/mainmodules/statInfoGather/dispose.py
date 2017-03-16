#coding:utf-8
import sys
sys.path.append("..")
sys.path.append("../")
import tools.recutils as recutils
from datetime import datetime
import tools.systemUtils as systemUtils
"""
    zwx 2016-03-16 main
    采集处置阶段指标
    处置、结案
    处置之后则算应结案数,超期未处置也算应结案数
"""
"""
    入口
"""
def execute(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    dispose_actdef_ids = sysInfo.get_data("dispose_actdef_ids") if sysInfo.get_data("dispose_actdef_ids") else [0]
    dispose_act_inst = None
    if rec_info["act_property_id"] > 8:
        stat_info_dict["need_supervise_num"] = 1
        stat_info_dict["need_archive_num"] = 1
        dispose_act_inst = recutils.get_last_trans_act(act_inst_list, dispose_actdef_ids, (610,))
        if dispose_act_inst and dispose_act_inst["end_time"]:
            stat_info_dict["dispose_num"] = 1
            if dispose_act_inst["end_time"] > dispose_act_inst["bundle_deadline"]:
                stat_info_dict["intime_dispose_num"] = 0
                stat_info_dict["overtime_dispose_num"] = 1
                stat_info_dict["intime_to_archive_num"] = 0
                stat_info_dict["overtime_to_archive_num"] = 1
            else:
                stat_info_dict["intime_dispose_num"] = 1
                stat_info_dict["overtime_dispose_num"] = 0
                stat_info_dict["intime_to_archive_num"] = 1
                stat_info_dict["overtime_to_archive_num"] = 0
    elif rec_info["act_property_id"] in (7, 8):
        stat_info_dict["to_dispose_num"] = 1
        dispose_act_inst = recutils.get_last_act_inst(act_inst_list, dispose_actdef_ids)
        if datetime.now() > dispose_act_inst["bundle_deadline"]:
            stat_info_dict["intime_to_dispose_num"] = 0
            stat_info_dict["overtime_to_dispose_num"] = 1
            stat_info_dict["need_archive_num"] = 1
            stat_info_dict["overtime_to_archive_num"] = 1
            stat_info_dict["intime_to_archive_num"] = 0
        else:
            stat_info_dict["intime_to_dispose_num"] = 1
            stat_info_dict["overtime_to_dispose_num"] = 0
    elif rec_info["act_property_id"] == 103: # 挂账，不计入处置指标，查找处置活动
        dispose_act_inst = recutils.get_last_trans_act(act_inst_list, dispose_actdef_ids, (810,))
    
    # 处置信息
    if dispose_act_inst:
        print "11"
        stat_info_dict["dispose_end_time"] = dispose_act_inst["end_time"] if stat_info_dict.has_key("dispose_num") and stat_info_dict["dispose_num"] == 1 else None
        stat_info_dict["dispose_deadline"] = dispose_act_inst["deadline_time"]
        stat_info_dict["dispose_begin_time"] = dispose_act_inst["create_time"]
        stat_info_dict["bundle_dispose_deadline"] = dispose_act_inst["bundle_deadline"]
        # 处置用时 捆绑用时 处置时限 捆绑时限
        stat_info_dict["dispose_used"] = dispose_act_inst["act_used"]
        stat_info_dict["bundle_dispose_used"] = dispose_act_inst["bundle_used"]
        stat_info_dict["dispose_limit"] = dispose_act_inst["act_limit"]
        stat_info_dict["bundle_dispose_limit"] = dispose_act_inst["bundle_limit"]

        dispose_role_id = dispose_act_inst["role_id"]
        stat_info_dict["dispose_act_def_id"] = dispose_act_inst["act_def_id"]
        stat_info_dict["dispose_unit_id"] = dispose_act_inst["unit_id"]
        stat_info_dict["dispose_unit_name"] = dispose_act_inst["unit_name"]
        dispose_unit = systemUtils.get_unit_byID(biz_cur, dispose_act_inst["unit_id"])
        if dispose_unit:
            stat_info_dict["dispose_region_id"] = dispose_unit["region_id"]
            stat_info_dict["dispose_region_name"] = dispose_unit["region_name"]
        # 更新专业部门信息，杭州项目定制
        # __extendDisposeInfo(biz_cur = biz_cur, stat_info_dict = stat_info_dict, act_inst_list = act_inst_list, dispose_act_inst = dispose_act_inst, sysInfo = sysInfo)
        # 采集返工数
        __reworkHandler(recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict, dispose_act_inst = dispose_act_inst)

"""
    专业部门信息
"""
def __extendDisposeInfo(biz_cur, stat_info_dict, act_inst_list, dispose_act_inst, sysInfo):
    """获取专业部门信息"""    
    dispose_act_def_id = dispose_act_inst["act_def_id"]
    dispose_role_id = dispose_act_inst["role_id"]
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

    # 初始化一二级部门信息
    first_unit_id = None
    first_unit_name = None
    second_unit_id = None
    second_unit_name = None
    
    # 更新到stat_info_dict中        
    stat_info_dict["dispose_unit_id"] = second_unit_id if second_unit_id else first_unit_id
    stat_info_dict["dispose_unit_name"] = second_unit_name if second_unit_name else first_unit_name
    stat_info_dict["dispose_region_id"] = dispose_region_id
    stat_info_dict["dispose_region_name"] = dispose_region_name
    stat_info_dict["first_unit_id"] = first_unit_id
    stat_info_dict["first_unit_name"] = first_unit_name
    stat_info_dict["second_unit_id"] = second_unit_id
    stat_info_dict["second_unit_name"] = second_unit_name

"""
    返工采集
"""
def __reworkHandler(recInfo, sysInfo, stat_info_dict, dispose_act_inst):
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")
    act_property_id = rec_info["act_property_id"]
    dispose_actdef_ids = sysInfo.get_data("dispose_actdef_ids") if sysInfo.get_data("dispose_actdef_ids") else [0]
    dispatch_actdef_ids = sysInfo.get_data("dispatch_actdef_ids") if sysInfo.get_data("dispatch_actdef_ids") else [0]
    check_actdef_ids = sysInfo.get_data("check_actdef_ids") if sysInfo.get_data("check_actdef_ids") else [0]
    # 说明：
    # 经过核查且再次派遣到相同部门的为返工，记次数
    # 只计算一级处置节点返工次数
    multiReworkNum = 0
    first_dispose_unit_id = None
    firstDisposeCreateTime_list = []
    # 先找到最终处置部门的一级部门,到达时间存放到列表中
    for act_inst_dict in act_inst_list:
        if act_inst_dict["act_def_id"] in dispose_actdef_ids and act_inst_dict["create_time"] <= dispose_act_inst["create_time"]:
            first_dispose_unit_id = act_inst_dict["unit_id"]
            firstDisposeCreateTime_list.append(act_inst_dict["create_time"])
    if not first_dispose_unit_id:
        first_dispose_unit_id = dispose_act_inst["unit_id"]
    # 循环判断是否经过派遣-处置-核查
    dispatchFlag = 0
    disposeFlag = 0
    checkFlag = 0
    for act_inst_dict in act_inst_list:
        if act_inst_dict["act_def_id"] in dispatch_actdef_ids:
            dispatchFlag = 1
            disposeFlag = 0

        if act_inst_dict["act_def_id"] in dispose_actdef_ids:
            if act_inst_dict["unit_id"] == first_dispose_unit_id:
                disposeFlag = 1
                if checkFlag == 1:
                    multiReworkNum += 1
                    checkFlag = 0
                    dispatchFlag = 0
                    disposeFlag = 0

        if act_inst_dict["act_def_id"] in check_actdef_ids:
            checkFlag = 1
    
    if multiReworkNum > 0:
        stat_info_dict["multi_rework_num"] = multiReworkNum
        stat_info_dict["rework_num"] = 1
