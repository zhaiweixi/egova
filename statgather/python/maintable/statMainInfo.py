#coding: utf-8

"""
    zwx 2016-04-01 main
    案件主要信息数据表
"""
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst

table_name = schemaConst.umstat_ + "to_stat_main_info"

field = (   # 案件标识 任务号 上报时间
            "rec_id", "task_num", "create_time", \
            # 问题描述 问题来源标识 问题来源 案件类型标识 案件类型
            "event_desc", "event_src_id", "event_src_name", "rec_type_id", "rec_type_name", \
            # 问题类型标识 问题类型 大类标识 大类 小类标识 小类
            "event_type_id", "event_type_name", "main_type_id", "main_type_name", "sub_type_id", "sub_type_name", \
            # 问题类型编码 部件编码
            "event_type_code", "part_code", \
            # 地址 城区标识 城区 街道标识 街道 社区标识 社区
            "address", "district_id", "district_name", "street_id", "street_name", "community_id", "community_name", \
            # 道路标识 道路 道路类型标识 道路类型
            "road_id", "road_name", "road_type_id", "road_type_name", \
            # 单元网格标识 单元网格 责任网格标识 责任网格 责任网格编码
            "cell_id", "cell_name", "duty_grid_id", "duty_grid_name", "duty_grid_code", \
            # x坐标 y坐标 案件显示标识 案件活动属性
            "coordinate_x", "coordinate_y", "display_style_id", "act_property_id", \
            # 结案时间 作废时间 问题状态标识 问题状态
            "archive_time", "cancel_time", "event_state_id", "event_state_name", \
            # 上报数 受理数 核实数 立案数 派遣数 处置数 督查数 核查数 结案数 作废数
            "report_num", "operate_num", "verify_num", "inst_num", "dispatch_num", "dispose_num", "supervise_num", "check_num", "archive_num", "cancel_num", \
            # 处置区域标识 处置区域 处置部门标识 处置部门
            "dispose_region_id", "dispose_region_name", "dispose_unit_id", "dispose_unit_name"
        )