#coding:utf-8
"""
    zwx 2016-04-01 main
    专业部门考核数据表
    数据来源于to_stat_info
"""
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst

table_name = schemaConst.umstat_ + "to_stat_unit_eval"

field = (   # 基本属性
            "rec_id", "task_num", "create_time", "event_desc", "address", "event_src_id", "event_src_name", \
            "rec_type_id", "rec_type_name", "event_type_id", "event_type_name", "main_type_id", "main_type_name", "sub_type_id", "sub_type_name", "event_type_code", \
            "district_id", "district_name", "street_id", "street_name", "community_id", "community_name", "cell_id", "cell_name", "duty_grid_id", "duty_grid_name", "duty_grid_code", \
            "coordinate_x", "coordinate_y", "road_id", "road_name", "archive_time", \
            "road_type_id", "road_type_name", \
            "act_property_id", "display_style_id",\
            # 处置区域标识 处置区域 处置部门标识 处置部门
            "dispose_region_id", "dispose_region_name", "dispose_unit_id", "dispose_unit_name", \
            # 一级部门标识 一级部门 二级部门标识 二级部门 三级部门标识 三级部门
            "first_unit_id", "first_unit_name", "second_unit_id", "second_unit_name", "third_unit_id", "third_unit_name", \
            # 处置截止时间 处置开始时间 处置结束时间 捆绑截止时间
            "dispose_deadline", "dispose_begin_time", "dispose_end_time", "bundle_dispose_deadline",\
            # 应处置数 处置数 按期处置数 超期处置数
            "need_dispose_num", "dispose_num", "intime_dispose_num", "overtime_dispose_num", \
            # 处置超时倍数 捆绑超时倍数 处置用时 捆绑处置用时 处置时限 捆绑处置时限 处置时限字符串
            "dispose_overtime_times", "bundle_dispose_overtime_times", "dispose_used", "bundle_dispose_used", "dispose_limit", "bundle_dispose_limit", "dispose_limit_str", \
            # 待处置数 按期待处置数 超期待处置数
            "to_dispose_num", "intime_to_dispose_num", "overtime_to_dispose_num", \
            # 返工数 返工次数 城区返工数 城区返工次数 挂账数(缓办数) 历史挂账数 延期数
            "rework_num", "multi_rework_num", "district_rework_num", "multi_district_rework_num", "hang_num", "his_hang_num", "postpone_num", \
            # 应结案数 结案数 按期结案数 超期结案数 按期未结案数 超期未结案数
            "need_archive_num", "archive_num", "intime_archive_num", "overtime_archive_num", "intime_to_archive_num", "overtime_to_archive_num", \
            # 处置意见 处置节点号
            "dispose_opinion", "dispose_act_def_id", \
        )