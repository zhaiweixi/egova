#coding: utf-8
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst
import copy as python_copy
from tools.utils import query_for_dict
import logging

class actInstInfoFactory(object):
    def __init__(self, stat_cur, biz_cur, rec_id):
        """
            采集单条案件信息，用于采集。
        """
        self.__recID = rec_id
        self.__isHisRec = self.__get_rec_his_flag(biz_cur = biz_cur, stat_cur = stat_cur) == 1
        self.__data = {}
        self.__data["rec_id"] = rec_id
        self.__data["act_id_dispose"] = self.__get_act_id_dispose(biz_cur = biz_cur, stat_cur = stat_cur)
        self.__data["act_def_id"] = self.__get_act_def_id(biz_cur = biz_cur, stat_cur = stat_cur)
        self.__data["act_def_name"] = self.__get_act_def_name(biz_cur = biz_cur, stat_cur = stat_cur)
        self.__data["role_part_id"] = self.__get_role_part_id(biz_cur = biz_cur, stat_cur = stat_cur)
        role_part_id = self.__data["role_part_id"]
        self.__data["act_def_id_first"] = self.__get_act_def_id_first(biz_cur = biz_cur, stat_cur = stat_cur)
        self.__data["role_part_id_first"] = self.__get_role_part_id_first(biz_cur = biz_cur, stat_cur = stat_cur)
        role_part_id_first = self.__data["role_part_id_first"]
        self.__data["act_def_id_second"] = self.__get_act_def_id_second(biz_cur = biz_cur, stat_cur = stat_cur)
        self.__data["role_part_id_second"] = self.__get_role_part_id_second(biz_cur = biz_cur, stat_cur = stat_cur)
        role_part_id_second = self.__data["role_part_id_second"]
        self.__data["cur_unit_id"] = self.__get_cur_unit_id(biz_cur = biz_cur, role_part_id = role_part_id)
        self.__data["cur_unit_id_first"] = self.__get_cur_unit_id_first(biz_cur = biz_cur, role_part_id_first = role_part_id_first)
        self.__data["cur_unit_id_second"] = self.__get_cur_unit_id_second(biz_cur = biz_cur, role_part_id_second = role_part_id_second)
        self.__data["max_act_id"] = self.__get_max_act_id(biz_cur = biz_cur, stat_cur = stat_cur)
        max_act_id = self.__data["max_act_id"]
        self.__data["archive_end_date"] = self.__get_archive_end_date(biz_cur = biz_cur, max_act_id = max_act_id)
        self.__data["pass_act_def"] = self.__get_pass_act_def(biz_cur = biz_cur, stat_cur = stat_cur)

        #采集预结案差错次数
        self.__data["wrong_pre_archive_counts"] = self.__get_wrong_pre_archive_counts(biz_cur = biz_cur, stat_cur = stat_cur)

    def __get_act_id_dispose(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.actInstInfo.actInstInfoFactory")
        """
        获取派遣到专业部门阶段的标识
        """
        rec_id = self.__recID
        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select act_id, act_def_id, act_def_name, role_id, act_deadline, act_used from " \
              "(select act_id, act_def_id, act_def_name, role_id, act_deadline, act_used from %(towfactinst)s a where rec_id = %(rec_id)s and act_state_id <> 29800 " \
              "and act_def_id in (select act_def_id from tc_wf_act_def where proc_def_ver = 0 and act_property_id in (7,8,9)) and act_def_id not in (320,321) and not exists " \
              "(select * from to_wf_trans_inst where act_id = a.act_id and item_type_id = 626) order by create_time desc) b limit 1"

        # 执行sql
        param = {"towfactinst": towfactinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_act_def_id(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.actInstInfo.actInstInfoFactory")
        """
        获取派遣到专业部门阶段的标识
        """
        rec_id = self.__recID
        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select act_def_id from (select act_def_id from %(towfactinst)s a where rec_id = %(rec_id)s and act_state_id <> 29800 " \
              "and act_def_id in (select act_def_id from tc_wf_act_def where proc_def_ver = 0 and act_property_id in (7,8,9)) and act_def_id not in (320,321) and not exists " \
              "(select * from to_wf_trans_inst where act_id = a.act_id and item_type_id = 626) order by create_time desc) b limit 1"

        # 执行sql
        param = {"towfactinst": towfactinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_act_def_name(self,biz_cur,stat_cur):
        logger = logging.getLogger("main.bean.actInstInfo.actInstInfoFactory")

        rec_id = self.__recID
        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select act_def_name from (select act_def_name from %(towfactinst)s a where rec_id = %(rec_id)s and act_state_id <> 29800 " \
              "and act_def_id in (select act_def_id from tc_wf_act_def where proc_def_ver = 0 and act_property_id in (7,8,9)) and act_def_id not in (320,321) and not exists " \
              "(select * from to_wf_trans_inst where act_id = a.act_id and item_type_id = 626) order by create_time desc) b limit 1"

        # 执行sql
        param = {"towfactinst": towfactinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_role_part_id(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.actInstInfo.actInstInfoFactory")
        """
        获取派遣到专业部门阶段岗位标识
        """
        rec_id = self.__recID
        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select role_id from (select role_id from %(towfactinst)s a where rec_id = %(rec_id)s and act_state_id <> 29800 " \
              "and act_def_id in (select act_def_id from tc_wf_act_def where proc_def_ver = 0 and act_property_id in (7,8,9)) and act_def_id not in (320,321) and not exists " \
              "(select * from to_wf_trans_inst where act_id = a.act_id and item_type_id = 626) order by create_time desc) b limit 1"
        # 执行sql
        param = {"towfactinst": towfactinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_act_def_id_first(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.actInstInfo.actInstInfoFactory")
        """
        获取第一次派遣到专业部门阶段的标识
        """
        rec_id = self.__recID
        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select act_def_id from (select act_def_id from %(towfactinst)s a where rec_id = %(rec_id)s and act_state_id <> 29800 " \
              "and act_def_id in (select act_def_id from tc_wf_act_def where proc_def_ver = 0 and act_property_id in (7,8,9)) and act_def_id not in (320,321) and not exists " \
              "(select * from to_wf_trans_inst where act_id = a.act_id and item_type_id = 626) order by create_time asc) b limit 1"
        # 执行sql
        param = {"towfactinst": towfactinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_role_part_id_first(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.actInstInfo.actInstInfoFactory")
        """
        获取第一次派遣到专业部门阶段的标识
        """
        rec_id = self.__recID
        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select role_id from (select role_id from %(towfactinst)s a where rec_id = %(rec_id)s and act_state_id <> 29800 " \
              "and act_def_id in (select act_def_id from tc_wf_act_def where proc_def_ver = 0 and act_property_id in (7,8,9)) and act_def_id not in (320,321) and not exists " \
              "(select * from to_wf_trans_inst where act_id = a.act_id and item_type_id = 626) order by create_time asc) b limit 1"

        # 执行sql
        param = {"towfactinst": towfactinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_act_def_id_second(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.actInstInfo.actInstInfoFactory")
        """
        获取第二次派遣到专业部门阶段的标识
        """
        rec_id = self.__recID
        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select act_def_id from (select act_def_id from %(towfactinst)s a where rec_id = %(rec_id)s and act_state_id <> 29800 " \
              "and act_def_id in (select act_def_id from tc_wf_act_def where proc_def_ver = 0 and act_property_id in (7,8,9)) and act_def_id not in (320,321) and not exists " \
              "(select * from to_wf_trans_inst where act_id = a.act_id and item_type_id = 626) order by create_time asc) b limit 2"
        # 执行sql
        param = {"towfactinst": towfactinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_role_part_id_second(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.actInstInfo.actInstInfoFactory")
        """
        获取第二次派遣到专业部门阶段的标识
        """
        rec_id = self.__recID
        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select role_id from (select role_id from %(towfactinst)s a where rec_id = %(rec_id)s and act_state_id <> 29800 " \
              "and act_def_id in (select act_def_id from tc_wf_act_def where proc_def_ver = 0 and act_property_id in (7,8,9)) and act_def_id not in (320,321) and not exists " \
              "(select * from to_wf_trans_inst where act_id = a.act_id and item_type_id = 626) order by create_time asc) b limit 2"
        # 执行sql
        param = {"towfactinst": towfactinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_cur_unit_id(self, biz_cur, role_part_id):
        logger = logging.getLogger("main.bean.actInstInfo.actInstInfoFactory")
        """
        获取最终派遣到的专业部门标识
        """
        tcrole = "tc_role"
        sql = "select unit_id from %(tcrole)s where role_id = %(role_part_id)s"

        # 执行sql
        param = {"tcrole": tcrole, "role_part_id": role_part_id['role_id']}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_cur_unit_id_first(self, biz_cur, role_part_id_first):
        logger = logging.getLogger("main.bean.actInstInfo.actInstInfoFactory")
        """
        获取第一次派遣到专业部门标识
        """
        tcrole = "tc_role"
        sql = "select unit_id from %(tcrole)s where role_id = %(role_part_id_first)s"

        # 执行sql
        param = {"tcrole": tcrole, "role_part_id_first": role_part_id_first['role_id']}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_cur_unit_id_second(self, biz_cur, role_part_id_second):
        logger = logging.getLogger("main.bean.actInstInfo.actInstInfoFactory")
        """
        获取第二次派遣到专业部门标识
        """
        tcrole = "tc_role"
        sql = "select unit_id from %(tcrole)s where role_id = %(role_part_id_second)s"

        # 执行sql
        param = {"tcrole": tcrole, "role_part_id_second": role_part_id_second['role_id']}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_pass_act_def(self, biz_cur, stat_cur):
        rec_id = self.__recID
        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select group_concat(act_def_name) as act_def_name from %(towftransinst)s where rec_id = %(rec_id)s"
        # 执行sql
        param = {"towftransinst": towfactinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    #采集错误预结案数
    def __get_wrong_pre_archive_counts(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.recInfo.actInstInfoFactory")

        rec_id = self.__recID
        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select count(act_id) from %(towftransinst)s where rec_id = %(rec_id)s and act_def_id in (304,311) and next_act_def_id = 313 and item_type_id = 610"
        #这里要用游标实现
        # 执行sql
        param = {"towftransinst": towfactinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_max_act_id(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.recInfo.actInstInfoFactory")

        rec_id = self.__recID
        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select max(act_id) as act_id from %(towftransinst)s where rec_id = %(rec_id)s and act_def_id in (select act_def_id from tc_wf_act_def where act_property_id = 12 and proc_def_ver = 0)"
        param = {"towftransinst": towfactinst, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)

        return rec_info

    def __get_archive_end_date(self, biz_cur, max_act_id):
        logger = logging.getLogger("main.bean.recInfo.actInstInfoFactory")

        towfactinst = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        sql = "select end_time from %(towftransinst)s where act_id = %(act_id)s"
        param = {"towftransinst": towfactinst, "act_id": max_act_id["act_id"]}
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