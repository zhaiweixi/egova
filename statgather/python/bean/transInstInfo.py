#coding:utf-8
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst
import copy as python_copy
from tools.utils import query_for_dict
import logging

class transInstInfoFactory(object):
    def __init__(self, stat_cur, biz_cur, rec_id):
        """
            采集单条案件信息，用于采集。
        """
        self.__recID = rec_id
        self.__isHisRec = self.__get_rec_his_flag(biz_cur = biz_cur, stat_cur = stat_cur) == 1
        self.__data = {}
        self.__data["rec_id"] = rec_id
        self.__data["act_def_id"] = self.__get_act_def_id(biz_cur = biz_cur, stat_cur = stat_cur)
        self.__data["pre_archive_counts"] = self.__get_pre_archive_counts(biz_cur = biz_cur, stat_cur = stat_cur)
        # self._data["wrong_pre_archive_counts"] = self.__get_wrong_pre_archive_counts(biz_cur = biz_cur, stat_cur = stat_cur)

    def __get_act_def_id(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.recInfo.transInstInfoFactory")
        """
        获取案件市结案审核前阶段标识
        """
        rec_id = self.__recID
        towftransinst = (schemaConst.dlhist_ + "to_his_wf_trans_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_trans_inst"
        sql = "select act_def_id from %(towftransinst)s where rec_id = %(rec_id)s and next_act_def_id = 313 "

        # 执行sql
        param = {"towftransinst": towftransinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def  __get_pre_archive_counts(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.recInfo.transInstInfoFactory")

        rec_id = self.__recID
        towftransinst = (schemaConst.dlhist_ + "to_his_wf_trans_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_trans_inst"
        sql = "select count(act_id) from %(towftransinst)s where rec_id = %(rec_id)s and act_def_id in (304,311) and next_act_def_id = 313 and item_type_id = 610"

        # 执行sql
        param = {"towftransinst": towftransinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    # def __get_wrong_pre_archive_counts(self, biz_cur, stat_cur):
    #     logger = logging.getLogger("main.bean.recInfo.transInstInfoFactory")
    #
    #     rec_id = self.__recID
    #     towftransinst = (schemaConst.dlhist_ + "to_his_wf_trans_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_trans_inst"
    #     sql = "select count(act_id) from %(towftransinst)s where rec_id = %(rec_id)s and act_def_id in (304,311) and next_act_def_id = 313 and item_type_id = 610"
    #
    #     # 执行sql
    #     param = {"towftransinst": towftransinst, "rec_id": rec_id}
    #     rec_info = query_for_dict(biz_cur, sql % param)
    #
    #     return rec_info

    def __get_rec_his_flag(self, biz_cur, stat_cur):
        rec_id = self.__recID
        sql = "select rec_id from %(toRec)s where rec_id = %(rec_id)s "
        param = {"toRec": schemaConst.dlmis_ + "to_rec", "rec_id": self.__recID}
        biz_cur.execute(sql % param)
        row = biz_cur.fetchone()
        if row:
            return 0
        else:
            sql = "select rec_id from %(toRec)s where rec_id = %(rec_id)s "
            param = {"toRec": schemaConst.dlhist_ + "to_his_rec", "rec_id": rec_id}
            biz_cur.execute(sql % param)
            row = biz_cur.fetchone()
            if row:
                return 1
            else:
                return -1

     # 对外暴露获取数据字典方法，使用deepcopy，复制__data对象及其子对象返回
    def get_data(self, key = None):
        if key:
            if (self.__data.has_key(key)):
                return python_copy.deepcopy(self.__data[key])
            else:
                return None
        else:
            return python_copy.deepcopy(self.__data)