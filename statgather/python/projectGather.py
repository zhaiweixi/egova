# coding: utf-8
import sys
sys.path.append("..")
from tools.utils import insert_one, insert_many, copy_dict2dict as copy
import logging
from bean.transInstInfo import transInstInfoFactory
from bean.actInstInfo import actInstInfoFactory
from bean.toWFItemInst import toWFItemInstFactory
"""
    zwx 2016-03-16 hangzhou project
    项目定制采集入口
"""
def gather_handler(biz_cur, stat_cur, recInfo, sysInfo):
     # to_stat_info
    pass
    # gather_stat_info(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo)

"""
    采集to_stat_info表个性化指标
"""
def gather_stat_info(stat_cur, biz_cur, recInfo, sysInfo):
    logger = logging.getLogger("main.projectGather")
    rec_id = recInfo.get_data("rec_id")
    actInstInfo = actInstInfoFactory(stat_cur, biz_cur, rec_id)
    toWFItemInst = toWFItemInstFactory(stat_cur, biz_cur, rec_id)
    rec_Info = recInfo.get_data("rec_info")
    act_property_id = rec_Info["act_property_id"]
    handle_unit = rec_Info["handle_unit"]
    handle_human = rec_Info["handle_human"]
    from maintable.statinfo import table_name as table_name
    if handle_human is not None:
        sqlEx = "update %(statInfo)s set handle_human = %(handle_human)s where rec_id = %(rec_id)s";
        param = {"to_stat_info": table_name, "handle_human":handle_human, "rec_id": rec_id}
        stat_cur.execute(sqlEx % param)
    pass_unit = rec_Info["pass_unit"]
    if pass_unit is not None:
        sqlEx = "update %(to_stat_info)s set pass_unit = %(pass_unit)s where rec_id = %(rec_id)s";
        param = {"to_stat_info": table_name, "pass_unit":pass_unit, "rec_id": rec_id}
        stat_cur.execute(sqlEx % param)
    pass_human = rec_Info["pass_human"]
    if pass_human is not None:
        sqlEx = "update %(to_stat_info)s set pass_human = %(pass_human)s where rec_id = %(rec_id)s";
        param = {"to_stat_info": table_name, "pass_human":pass_human, "rec_id": rec_id}
        stat_cur.execute(sqlEx % param)
    apply_type = rec_Info["apply_type"]
    if apply_type is not None:
        sqlEx = "update %(to_stat_info)s set apply_type = %(apply_type)s where rec_id = %(rec_id)s";
        param = {"to_stat_info": table_name, "apply_type":apply_type, "rec_id": rec_id}
        stat_cur.execute(sqlEx % param)
    is_phone_reply = rec_Info["is_phone_reply"]
    if is_phone_reply is not None:
        sqlEx = "update %(to_stat_info)s set is_phone_reply = %(is_phone_reply)s where rec_id = %(rec_id)s";
        param = {"to_stat_info": table_name, "is_phone_reply":is_phone_reply, "rec_id": rec_id}
        stat_cur.execute(sqlEx % param)
    is_reply_flag = rec_Info["is_reply_flag"]
    if is_reply_flag is not None:
        sqlEx = "update %(to_stat_info)s set is_reply_flag = %(is_reply_flag)s where rec_id = %(rec_id)s";
        param = {"to_stat_info": table_name, "is_reply_flag":is_reply_flag, "rec_id": rec_id}
        stat_cur.execute(sqlEx % param)
    appoint_flag = rec_Info["appoint_flag"]
    if appoint_flag is not None:
        sqlEx = "update %(to_stat_info)s set appoint_flag = %(appoint_flag)s where rec_id = %(rec_id)s";
        param = {"to_stat_info": table_name, "appoint_flag":appoint_flag, "rec_id": rec_id}
        stat_cur.execute(sqlEx % param)
    line_disruption = rec_Info["line_disruption"]
    if line_disruption is not None:
        sqlEx = "update %(to_stat_info)s set line_disruption = %(line_disruption)s where rec_id = %(rec_id)s";
        param = {"to_stat_info": table_name, "line_disruption":line_disruption, "rec_id": rec_id}
        stat_cur.execute(sqlEx % param)
    deal_unit_flag = rec_Info["deal_unit_flag"]
    if deal_unit_flag is not None:
        sqlEx = "update %(to_stat_info)s set deal_unit_flag = %(deal_unit_flag)s where rec_id = %(rec_id)s";
        param = {"to_stat_info": table_name, "deal_unit_flag":deal_unit_flag, "rec_id": rec_id}
        stat_cur.execute(sqlEx % param)
    pass_act_def = actInstInfo.get_data("pass_act_def")
    if pass_act_def is not None:
        try:
            sqlEx = "update %(to_stat_info)s set pass_act_def = '%(pass_act_def)s' where rec_id = %(rec_id)s";
            param = {"to_stat_info": table_name, "pass_act_def":pass_act_def["act_def_name"], "rec_id": rec_id}
            stat_cur.execute(sqlEx % param)
        except Exception, e:
            logger.error(u"案件阶段指标采集失败: %s " % str(e))
            print(sqlEx % param)
    count_650 = toWFItemInst.get_data("count_650")

    if count_650 > 0:
        deal_operator_id = 1
    else:
        deal_operator_id = 0

    sqlEx = "update %(to_stat_info)s set deal_operator_id = %(deal_operator_id)s where rec_id = %(rec_id)s";
    param = {"to_stat_info": table_name, "deal_operator_id":deal_operator_id, "rec_id": rec_id}
    stat_cur.execute(sqlEx % param)

    if act_property_id > 7:
        # 采集错误派遣数
        cur_act_info = actInstInfo.get_data("act_id_dispose")
        cur_act_def_id = actInstInfo.get_data("act_def_id")
        cur_act_def_name = actInstInfo.get_data("act_def_name")
        cur_role_part_id = actInstInfo.get_data("role_part_id")
        act_def_id_first = actInstInfo.get_data("act_def_id_first")
        role_part_id_first = actInstInfo.get_data("role_part_id_first")
        act_def_id_second = actInstInfo.get_data("act_def_id_second")
        role_part_id_second = actInstInfo.get_data("role_part_id_second")
        cur_unit_id = actInstInfo.get_data("cur_unit_id")
        cur_unit_id_first = actInstInfo.get_data("cur_unit_id_first")
        cur_unit_id_second = actInstInfo.get_data("cur_unit_id_second")
        if (cur_act_def_id == act_def_id_first and cur_role_part_id == role_part_id_first) \
            or (cur_act_def_id != act_def_id_first and cur_unit_id != cur_unit_id_first) \
            or (cur_act_def_id == act_def_id_second and cur_role_part_id == role_part_id_second) \
            or (cur_act_def_id != act_def_id_second and cur_unit_id != cur_unit_id_second):
            accur_dispatch_num = 1
            wrong_dispatch_num = 0
        else:
            accur_dispatch_num = 0
            wrong_dispatch_num = 1

        try:
            sql = "update %(statInfo)s set accur_dispatch_num = %(accur_dispatch_num)s ,wrong_dispatch_num = %(wrong_dispatch_num)s, " \
                  "cur_act_def_name = '%(cur_act_def_name)s' where rec_id = %(rec_id)s"
            param = {"statInfo": table_name, "accur_dispatch_num": accur_dispatch_num, "wrong_dispatch_num":wrong_dispatch_num, "cur_act_def_name":cur_act_def_name["act_def_name"], "rec_id": rec_id}
            stat_cur.execute(sql % param)
        except Exception, e:
            logger.error(u"特殊指标采集失败: %s " % str(e))
            print(sql % param)

    if act_property_id == 12:
        # 采集市直接结案数 区直接结案数
        transInstInfo = transInstInfoFactory(stat_cur, biz_cur, rec_id)
        act_def_id = transInstInfo.get_data("act_def_id");
        if act_def_id == 303:
            citydirect_archive_num = 1
        elif act_def_id == 304:
            districtdirect_archive_num = 1
        else:
            citydirect_archive_num = 0
            districtdirect_archive_num = 0
        sql = "update %(statInfo)s set citydirect_archive_num = %(cityarchivenum)s ,districtdirect_archive_num = %(districtdirectarchivenum)s where rec_id = %(rec_id)s"
        from maintable.statinfo import table_name as table_name
        param = {"statInfo": table_name, "cityarchivenum": citydirect_archive_num, "districtdirectarchivenum":districtdirect_archive_num, "rec_id": rec_id}
        stat_cur.execute(sql % param)

    if act_property_id > 12 and act_property_id in (13,14):
        archive_end_date = actInstInfo.get_data("archive_end_date");
        sql = "update %(statInfo)s set archive_end_time = %(archive_end_date)s where rec_id = %(rec_id)s"
        from maintable.statinfo import table_name as table_name
        param = {"statInfo": table_name, "archive_end_date": archive_end_date, "rec_id": rec_id}
        stat_cur.execute(sql % param)

    if act_property_id == 101:
        #采集超时倍数
        deal_unit_flag = rec_Info["deal_unit_flag"]
        if deal_unit_flag == 2:
            sqlUnit2 = "select bundle_used,deadline_limit from to_rec_time_bundle where rec_id = %(rec_id)s"
            param1 = {"rec_id": rec_id}
            overtime_col = stat_cur.execute(sqlUnit2 % param1)
            act_used = overtime_col["bundle_used"]
            act_deadline = overtime_col["deadline_limit"]
        else:
            act_used = cur_act_info["act_used"]
            act_deadline = cur_act_info["act_deadline"]

        if act_used > act_deadline:
            over_time_times = (act_used - act_deadline)/act_deadline
        else:
            over_time_times = 0
        sql = "update %(statInfo)s set over_time_times = %(over_time_times)s where rec_id = %(rec_id)s"
        from maintable.statinfo import table_name as table_name
        param = {"statInfo": table_name, "over_time_times": over_time_times, "rec_id": rec_id}
        stat_cur.execute(sql % param)