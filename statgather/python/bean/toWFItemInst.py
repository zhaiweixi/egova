# coding:utf-8
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst
import copy as python_copy
from tools.utils import query_for_dict
import logging

class toWFItemInstFactory(object):
    def __init__(self, stat_cur, biz_cur, rec_id):
        """
            采集单条案件信息，用于采集。
        """
        self.__recID = rec_id
        self.__isHisRec = self.__get_rec_his_flag(biz_cur = biz_cur, stat_cur = stat_cur) == 1
        self.__data = {}
        self.__data["rec_id"] = rec_id
        self.__data["count_650"] = self.__get_count_650(biz_cur = biz_cur, stat_cur = stat_cur)

    def __get_count_650(self, biz_cur, stat_cur):

        rec_id = self.__recID
        towfiteminst = (schemaConst.dlhist_ + "to_his_wf_item_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_item_inst"
        sql = "select count(1) from %(towfiteminst)s where rec_id = %(rec_id)s and item_type_id = 650 "

        # 执行sql
        param = {"towfiteminst": towfiteminst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

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