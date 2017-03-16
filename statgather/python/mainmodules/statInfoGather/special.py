#coding:utf-8
"""
    zwx 2016-06-23
    特殊指标采集
    延期数
    缓办数
    回退数
"""
import sys
sys.path.append("..")
sys.path.append("../")
import constant.schemaConst as schemaConst
import logging

def execute(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    # 采集延期
    __extendPostponeInfo(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)
    # 采集挂账
    __extendHangInfo(stat_cur = stat_cur, biz_cur = biz_cur, recInfo = recInfo, sysInfo = sysInfo, stat_info_dict = stat_info_dict)

# 延期采集
def __extendPostponeInfo(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    rec_id = recInfo.get_data("rec_id")
    sql = """
            select count(1) as postpone_num, sum(time_num) as postpone_hours 
            from %(postponeTable)s a, %(humanTable)s b 
            where a.rec_id = %(iRecID)s and b.human_id = a.human_id
              and (b.unit_id = %(firstUnitID)s or b.unit_id = %(secondUnitID)s)
          
          """
    param = {}
    param["postponeTable"] = schemaConst.dlmis_ + "to_wf_postpone_time"
    param["humanTable"] = schemaConst.dlsys_ + "tc_human"
    param["iRecID"] = rec_id
    if stat_info_dict.has_key("first_unit_id"):
        param["firstUnitID"] = stat_info_dict["first_unit_id"] if stat_info_dict["first_unit_id"] else -1
    else:
        param["firstUnitID"] = -1
    if stat_info_dict.has_key("second_unit_id"):
        param["secondUnitID"] = stat_info_dict["second_unit_id"] if stat_info_dict["second_unit_id"] else -1
    else:
        param["secondUnitID"] = -1
    biz_cur.execute(sql % param)
    if (biz_cur.rowcount > 0):
        row = biz_cur.fetchone()
        stat_info_dict["postpone_num"] = row[0]
        stat_info_dict["postpone_hours"] = row[1] if row[0] > 0 else 0

# 挂账信息
def __extendHangInfo(stat_cur, biz_cur, recInfo, sysInfo, stat_info_dict):
    logger = logging.getLogger("main.mainmodules.statInfoGather")
    rec_id = recInfo.get_data("rec_id")
    rec_info = recInfo.get_data("rec_info")
    act_inst_list = recInfo.get_data("act_inst_list")

    if rec_info.has_key("real_act_property_id") and rec_info["real_act_property_id"] == 103:
        stat_info_dict["hang_num"] = 1
    # 历史挂账数   
    try:
        isHisRec = recInfo.get_data("isHisRecFlag")
        sWfItemInstTable = schemaConst.dlhist_ + "to_his_wf_item_inst" if isHisRec else schemaConst.dlmis_ + "to_wf_item_inst"
        sql = "select count(1) from %(sWfItemInstTable)s where rec_id = %(recID)s and item_type_id = 810"
        param = {"sWfItemInstTable": sWfItemInstTable, "recID": rec_id}
        biz_cur.execute(sql % param)
        if (biz_cur.rowcount > 0):
            stat_info_dict["his_hang_num"] = 1
    except Exception, e:
        logger.error(u"挂账信息采集失败[rec_id = %s]: %s" % (rec_id, str(e)))