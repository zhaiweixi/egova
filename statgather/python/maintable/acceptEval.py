#coding: utf-8
"""
    zwx 2016-04-01 main
    受理员考核数据表
"""
#增加人员所属街道
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst

table_name = schemaConst.umstat_ + "to_acceptor_eval"

field = (   # 主键 案件标识 任务号 上报时间 问题描述 问题来源标识 问题来源
            "acceptor_eval_id", "rec_id", "task_num", "create_time", "event_desc", "event_src_id", "event_src_name", \
            # 案件类型标识 案件类型 问题类型标识 问题类型 大类标识 大类 小类标识 小类 问题类型编码 部件编码
            "rec_type_id", "rec_type_name", "event_type_id", "event_type_name", "main_type_id", "main_type_name", "sub_type_id", "sub_type_name", "event_type_code", "part_code", \
            # 地址描述 区域标识 区域 街道标识 街道 社区标识 社区 网格标识 网格 责任网格标识 责任网格 责任网格编码
            "address", "district_id", "district_name", "street_id", "street_name", "community_id", "community_name", "cell_id", "cell_name", "duty_grid_id", "duty_grid_name", "duty_grid_code", \
            # x坐标 y坐标 案件显示标识 案件活动属性 道路标识 道路 道路类型标识
            "coordinate_x", "coordinate_y", "display_style_id", "act_property_id", "road_id", "road_name", "road_type_id",\
            # 结案时间 作废时间
            "archive_time", "cancel_time", \
            # 人员标识 人员 岗位标识 工作时间 活动开始时间 活动结束时间 
            "human_id", "human_name", "role_id", "execute_time", "action_start_time", "action_end_time", \
            # 受理数 按时受理数 不受理数 待受理数 准确受理数
            "operate_num", "intime_operate_num", "not_operate_num", "to_operate_num", "accur_operate_num",\
            # 应发核实数 发核实数 按时发核实数
            "need_send_verify_num", "send_verify_num", "intime_send_verify_num", \
            # 应发核查数 发核查数 按时发核查数
            "need_send_check_num", "send_check_num", "intime_send_check_num", \
            # 核查批转数 按时核查批转数
            "check_trans_num", "intime_check_trans_num", \
            # 自处置办结数 自处置待审核数 自处置作废数 
            "patrol_deal_archive_num", "patrol_deal_to_check_num", "patrol_deal_cancel_num", 
        )

extend_field = ()