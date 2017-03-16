#coding:utf-8
"""
    zwx 2016-04-01 main
    案件工具方法
    @ get_first_trans_act 获取指定节点集合的第一条指定流向活动
    @ get_last_trans_act 获取指定节点集合的最后一条指定流向活动
    @ get_last_act_inst 获取指定节点集合的第一条活动
    @ get_last_act_inst 获取指定节点集合的最后一条活动
    @ get_between_last_trans_act 获取指定节点集合在指定时间范围内的最后一条指定流向记录
    @ get_between_last_act_inst 获取指定节点集合在指定时间范围内的最后一条记录
    @ get_last_patrol_task 获取在指定时间之后的最后一条指定任务类型的监督员任务
    @ get_dispose_dict 获取处置
"""
from datetime import datetime

max_time = datetime.strptime("2100-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
min_time = datetime.strptime("2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

def get_first_trans_act(act_inst_list, act_def_ids, item_type_ids):
	# 获取指定节点集合的第一条指定流向活动
    # @param act_inst_list 活动实例列表
    # @param act_def_ids 指定节点集合
    # @param item_type_ids 指定流向类型集合
    # @return 一条活动实例
    maxtime = max_time
    first_act_inst = None
    for act_inst in act_inst_list:
        if act_inst["act_def_id"] in act_def_ids and act_inst["item_type_id"] in item_type_ids:
            if act_inst["create_time"] <= maxtime:
                first_act_inst = act_inst
                maxtime = act_inst["create_time"]
                continue
            else:
                continue
    return first_act_inst

def get_last_trans_act(act_inst_list, act_def_ids, item_type_ids):
	# 获取指定节点集合的最后一条指定流向活动
    # @param act_inst_list 活动实例列表
    # @param act_def_ids 指定节点集合
    # @param item_type_ids 指定流向类型集合
    # @return 一条活动实例
    mintime = min_time
    last_act_inst = None
    for act_inst in act_inst_list:
        if act_inst["act_def_id"] in act_def_ids and act_inst["item_type_id"] in item_type_ids:
            if act_inst["create_time"] >= mintime:
                last_act_inst = act_inst
                mintime = act_inst["create_time"]
                continue
            else:
                continue
    return last_act_inst

def get_last_act_inst(act_inst_list, act_def_ids):
	# 获取指定节点集合的第一条活动
    # @param act_inst_list 活动实例列表
    # @param act_def_ids 指定节点集合
    # @return 一条活动实例
    mintime = min_time
    last_act_inst = None
    for act_inst in act_inst_list:
        if act_inst["act_def_id"] in act_def_ids and act_inst["create_time"] >= mintime:
            last_act_inst = act_inst
            mintime = act_inst["create_time"]
            continue
        else:
            continue
    return last_act_inst

def get_between_last_trans_act(act_inst_list, act_def_ids, start_datetime, end_datetime, item_type_ids):
    # 获取指定节点集合的最后一条活动
    # @param act_inst_list 活动实例列表
    # @param act_def_ids 指定节点集合
    # @return 一条活动实例
    last_trans_act = None
    mintime = start_datetime
    for act_inst in act_inst_list:
        if act_inst["act_def_id"] in act_def_ids and act_inst["create_time"] >= mintime and \
            act_inst["create_time"] < end_datetime and act_inst["item_type_id"] in item_type_ids:
            last_trans_act = act_inst
            mintime = act_inst["create_time"]
            continue
        else:
            continue
    return last_trans_act

def get_between_last_act_inst(act_inst_list, act_def_ids, start_datetime, end_datetime):
    # 获取指定节点集合在指定时间范围内的最后一条指定流向记录
    # @param act_inst_list 活动实例列表
    # @param act_def_ids 指定节点集合
    # @param start_datetime 开始时间
    # @param end_datetime 结束时间
    # @return 一条活动实例
    last_act_inst = None
    mintime = start_datetime
    for act_inst in act_inst_list:
        if act_inst["act_def_id"] in act_def_ids and act_inst["create_time"] >= mintime and act_inst["create_time"] < end_datetime:
            last_act_inst = act_inst
            mintime = act_inst["create_time"]
            continue
        else:
            continue
    return last_act_inst

def get_last_patrol_task(patrol_task_list, start_datetime, task_type):
	# 获取在指定时间之后的最后一条指定任务类型的监督员任务
    # @param patrol_task_list 监督员任务列表
    # @param start_datetime 限定开始时间
    # @param task_type 任务类型 2:核实|3:核查
    # @return 一条监督员任务
    try:
        last_patrol_task = None
        mintime = start_datetime
        for patrol_task in patrol_task_list:
            if patrol_task["task_type"] == task_type and patrol_task["cancel_flag"] == 0 and patrol_task["create_time"] >= mintime:
                last_patrol_task = patrol_task
                mintime = patrol_task["create_time"]
                continue
            else:
                continue
        return last_patrol_task
    except:
        return None