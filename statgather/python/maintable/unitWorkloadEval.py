#coding: utf-8
"""
    zwx 2016-04-01 main
    专业部门工作量表
"""
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst

table_name = schemaConst.umstat_ + "to_unit_workload_eval"

field = (   # 主键
            "unit_workload_eval_id", \
            # 案件基本信息
            "rec_id", "task_num", "create_time", "event_desc", "address", "event_src_id", "event_src_name", \
            "rec_type_id", "rec_type_name", "event_type_id", "event_type_name", "main_type_id", "main_type_name", "sub_type_id", "sub_type_name", "event_type_code", "part_code", \
            "district_id", "district_name", "street_id", "street_name", "community_id", "community_name", "cell_id", "cell_name", "duty_grid_id", "duty_grid_name", "duty_grid_code", \
            "coordinate_x", "coordinate_y", "display_style_id", "act_property_id", "road_id", "road_name", \
            # 统计标识 
            "stat_flag", "road_type_id", "road_type_name", \
            # 时间指标
            "execute_time", "action_start_time", "action_end_time", \
            # 指标
            "dispatch_num", "back_num", "overtime_back_num", "postpone_num", "hang_num", "cancel_num", \
            # 处置区域标识 处置区域
            "dispose_region_id", "dispose_region_name", "dispose_unit_id", "dispose_unit_name", "first_unit_id", "first_unit_name", "second_unit_id", "second_unit_name"
        )