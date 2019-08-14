# coding: utf-8
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst
"""
    案件流转效率表
"""
table_name = schemaConst.umstat_ + "to_stat_flow_info"
field = (
    # 主键 案件标识 任务号 上报时间 问题描述 地址 act_property_id display_style_id x坐标 y坐标
    "flow_id", "rec_id", "task_num", "create_time", "event_desc", "address", "act_property_id", "display_style_id", "coordinate_x", "coordinate_y",
    # 问题来源ID 问题来源 问题类型ID 问题类型 大类ID 大类 小类ID 小类
    "event_src_id", "event_src_name", "event_type_id", "event_type_name", "main_type_id", "main_type_name", "sub_type_id", "sub_type_id",
    # 城区ID 城区 街道ID 街道 社区ID 社区
    "district_id", "district_name", "street_id", "street_name", "community_id", "community_name",
    # 活动标识 环节ID 环节 流转用时 是否超时 开始时间 结束时间 截止时间 考核标识
    "act_id", "cur_stage_id", "cur_stage_name", "flow_used", "overtime_flag", "start_time", "end_time", "deadline_time", "stat_flag",
    # 环节计数 收发核查用时 核查用时
    "flow_num", "rs_check_used", "check_used"
)