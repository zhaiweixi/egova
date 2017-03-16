#coding: utf-8
#监督员工作量表
"""
    zwx 2016-04-01 main
    监督员考核数据表
"""
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst

table_name = schemaConst.umstat_ + "to_patrol_eval"

field = (   # 主键 案件标识 任务号 上报时间 问题描述 问题来源标识 问题来源
            "patrol_eval_id", "rec_id", "task_num", "create_time", "event_desc", "event_src_id", "event_src_name", \
            # 案件类型标识 案件类型 问题类型标识 问题类型 大类标识 大类 小类标识 小类 问题类型编码 部件编码
            "rec_type_id", "rec_type_name", "event_type_id", "event_type_name", "main_type_id", "main_type_name", "sub_type_id", "sub_type_name", "event_type_code", "part_code", \
            # 地址描述 区域标识 区域 街道标识 街道 社区标识 社区 网格标识 网格 责任网格标识 责任网格 责任网格编码
            "address", "district_id", "district_name", "street_id", "street_name", "community_id", "community_name", "cell_id", "cell_name", "duty_grid_id", "duty_grid_name", "duty_grid_code", \
            # x坐标 y坐标 案件显示标识 案件活动属性 道路标识 道路 道路类型标识
            "coordinate_x", "coordinate_y", "display_style_id", "act_property_id", "road_id", "road_name", "road_type_id",\
            # 结案时间 作废时间
            "archive_time", "cancel_time", \
            # 人员标识 人员 所属区域标识 所属区域 工卡号 工作时间
            "human_id", "human_name", "human_region_id", "human_region_name", "card_id", "execute_time", \
            # 上报监督员标识 上报监督员
            "report_patrol_id", "report_patrol_name", \
            # 监督员上报数 监督员有效上报数
            "patrol_report_num", "valid_patrol_report_num", "invalid_patrol_report_num", \
            # 应核实数 核实数 按时核实数 超时核实数 待核实数 超时待核实数
            "need_verify_num", "verify_num", "intime_verify_num", "overtime_verify_num", "to_verify_num", "overtime_to_verify_num", \
            # 应核查数 核查数 按时核查数 超时核查数 待核查数 超时待核查数 无效核查数
            "need_check_num", "check_num", "intime_check_num", "overtime_check_num", "to_check_num", "overtime_to_check_num", "invalid_check_num", \
        )

extend_field = ()