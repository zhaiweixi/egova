# coding:utf-8
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst
"""
    案件统计表
    zwx 2016-04-22 main
"""
table_name = schemaConst.umstat_ + "to_stat_info"

field = (# 案件标识 任务号 上报时间 问题描述 地址 问题来源标识 问题来源
         "rec_id", "task_num", "create_time", "event_desc", "address", "event_src_id", "event_src_name",
         # 案件类型标识 案件类型 问题类型标识 问题类型 大类标识 大类 小类标识 小类 问题类型编码 部件编码
         "rec_type_id", "rec_type_name", "event_type_id", "event_type_name", "main_type_id", "main_type_name", "sub_type_id", "sub_type_name", "event_type_code", "part_code", 
         # 区域标识 区域 街道标识 街道 社区标识 社区 网格标识 网格 责任网格标识 责任网格 责任网格编码
         "district_id", "district_name", "street_id", "street_name", "community_id", "community_name", "cell_id", "cell_name", "duty_grid_id", "duty_grid_name", "duty_grid_code", 
         # x坐标 y坐标 案件显示标识 案件活动属性
         "coordinate_x", "coordinate_y", "display_style_id", "act_property_id", 
         # 道路标识 道路名称 道路类型标识 道路类型
         "road_id", "road_name", "road_type_id", "road_type_name"
         # 问题状态标识 问题状态 问题级别标识 问题级别 问题等级标识 问题等级
         "event_state_id", "event_state_name", "event_level_id", "event_level_name", "event_grade_id", "event_grade_name", 
         # 上报阶段
         "report_num", "valid_report_num", "patrol_report_num", "valid_patrol_report_num", "report_patrol_id", "report_patrol_name", "public_report_num", "valid_public_report_num", 
         # 受理阶段
         "operate_num", "operate_human_id", "operate_human_name", "operate_role_id", "operate_time", "intime_operate_num", "not_operate_num", 
         # 发核实
         "need_send_verify_num", "send_verify_num", "send_verify_human_id", "send_verify_human_name", "send_verify_time", "intime_send_verify_num",
         # 监督员核实
         "need_verify_num", "verify_num", "verify_patrol_id", "verify_patrol_name", "verify_time", "intime_verify_num", 
         # 立案阶段
         "inst_num", "inst_human_id", "inst_human_name", "inst_role_id", "inst_time", "intime_inst_num", "not_inst_num", 
         # 派遣阶段
         "need_dispatch_num", "dispatch_num", "dispatch_human_id", "dispatch_human_name", "dispatch_role_id", "dispatch_time", "intime_dispatch_num", "to_dispatch_num", 
         "need_second_dispatch_num", "second_dispatch_num", "second_dispatch_human_id", "second_dispatch_human_name", "second_dispatch_role_id", "second_dispatch_time", "intime_second_dispatch_num",
         # 处置阶段
         "need_dispose_num", "dispose_num", "intime_dispose_num", "overtime_dispose_num", "to_dispose_num", "intime_to_dispose_num", "overtime_to_dispose_num", 
         # 特殊指标，返工数、返工次数、城区返工数、城区返工次数、挂账数、历史挂账数、推诿数
         "rework_num", "multi_rework_num", "district_rework_num", "multi_district_rework_num", "hang_num", "his_hang_num", "postpone_num", "shuffle_num",
         "need_archive_num", "archive_num", "intime_archive_num", "overtime_archive_num", "to_archive_num", "intime_to_archive_num", "overtime_to_archive_num", 
         "dispose_unit_id", "dispose_unit_name", "dispose_region_id", "dispose_region_name", "first_unit_id", "first_unit_name", "second_unit_id", "second_unit_name", "third_unit_id", "third_unit_name",
         "dispose_begin_time", "dispose_end_time", "dispose_deadline", "bundle_dispose_deadline", "dispose_used", "bundle_dispose_used", "dispose_limit", "bundle_dispose_limit", 
         # 特殊指标，超时处置倍数、捆绑超时处置倍数
         "dispose_overtime_times", "bundle_dispose_overtime_times", 
         # 督查阶段
         "need_supervise_num", "supervise_num", "supervise_human_id", "supervise_human_name", "supervise_role_id", "intime_supervise_num", 
         # 核查阶段
         # 应发核查数 发核查数 发核查人标识 发核查人 发核查岗位标识 发核查时间 按时发核查数
         "need_send_check_num", "send_check_num", "send_check_human_id", "send_check_human_name", "send_check_time", "intime_send_check_num",
         # 应核查数 核查数 核查监督员标识 核查监督员 核查时间 按时核查数
         "need_check_num", "check_num", "check_patrol_id", "check_patrol_name", "check_time", "intime_check_num", 
         # 核查批转数 核查批转人标识 核查批转人 核查批转岗位标识 核查批转时间
         "check_trans_num", "check_trans_human_id", "check_trans_human_name", "check_trans_role_id", "check_trans_time", 
         # 结案阶段
         # 人员应结案数 人员结案数 结案人标识 结案人 结案岗位标识 结案人按时结案数
         "need_human_archive_num", "human_archive_num", "archive_human_id", "archive_human_name", "archive_role_id", "intime_human_archive_num",
         # 结案时间
         "archive_time", 
         # 其他指标
         # 典型案件标识 周期类型 统计标识
         # 立案条件标识 立案条件 结案条件标识 结案条件
         "classic_flag", "period_type", "stat_flag", 
         # 业务标识 业务名称
         "biz_id", "biz_name", 
         # 立案条件标识 立案条件 结案条件标识 结案条件
         "new_inst_cond_id", "new_inst_cond_name", "archive_cond_id", "archive_cond_name", 
         # 最后更新时间
         "last_update_time",
         # 宁波城管指标
         "handle_human", "handle_unit", "pass_unit", "pass_human", "apply_type", "is_phone_reply", "is_reply_flag", "appoint_flag", "line_disruption",
         "deal_unit_flag", "deal_operator_id", "")

extend_field = ()