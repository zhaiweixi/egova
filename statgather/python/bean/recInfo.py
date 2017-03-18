# coding:utf-8
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst
from tools.utils import query_for_list, query_for_dict, copy_dict2dict as copy
import logging

class recInfoFactory(object):
    def __init__(self, stat_cur, biz_cur, rec_id):
        """
            采集单条案件信息，用于采集。
        """
        self.__recID = rec_id
        self.__isHisRec = self.__get_rec_his_flag(biz_cur = biz_cur, stat_cur = stat_cur) == 1
        self.__data = {}
        self.__data["rec_id"] = rec_id
        # since 2.0
        self.__init_rec_wf_info(biz_cur=biz_cur, stat_cur=stat_cur)
        self.__data["rec_info"] = self.__get_rec_info(biz_cur = biz_cur, stat_cur = stat_cur)
        self.__data["act_inst_list"] = self.__get_wf_act_inst_info(biz_cur = biz_cur, stat_cur = stat_cur)
        self.__data["patrol_task_list"] = self.__get_patrol_task_info(biz_cur = biz_cur, stat_cur = stat_cur)
        self.__data["act_ard_list"] = self.__get_act_ard_info(biz_cur = biz_cur, stat_cur = stat_cur)
        self.__data["isHisRecFlag"] = self.__isHisRec

    def __get_rec_info(self, biz_cur, stat_cur):
        logger = logging.getLogger("main.bean.recInfo.recInfoFactory")
        """
        获取案件信息：
        案件标识、任务号、上报时间、业务标识、业务名称、问题来源标识、问题来源、地址描述、问题描述
        案件类型标识、案件类型、问题类型标识、问题类型、大类标识、大类、小类标识、小类、问题类型编码、部件编码
        区域标识、区域、街道标识、街道、社区标识、社区、单元网格标识、单元网格、责任网格标识、责任网格
        X坐标、Y坐标、活动属性标识、案件显示标识、
        监督员自处置标识、监督员标识、监督员
        结案时间、作废时间、
        立案条件、结案条件、
        问题标记、结案类型
        道路名称 道路标识 道路类型标识 道路类型
        立案建议 修正意见
        区域类型标识
        """
        rec_id = self.__recID
        toRec = (schemaConst.dlhist_ + "to_his_rec") if self.__isHisRec else schemaConst.dlmis_ + "to_rec"
        sql = """select rec_id, task_num, create_time, biz_id, biz_name, event_src_id, event_src_name, address, event_desc,
                        rec_type_id, rec_type_name, event_type_id, event_type_name, main_type_id, main_type_name, sub_type_id, sub_type_name, event_type_code, part_code,
                        district_id, district_name, street_id, street_name, community_id, community_name, cell_id, cell_name, duty_grid_id, duty_grid_name,
                        coordinate_x, coordinate_y, act_property_id, display_style_id,
                        patrol_deal_flag, patrol_id, patrol_name,
                        archive_time, cancel_time,
                        new_inst_cond_id, new_inst_cond_name, archive_cond_id, archive_cond as archive_cond_name,
                        event_marks, archive_type_id,
                        road_name, road_id, road_type_id, road_type_name,
                        new_inst_advise, revise_opinion,
                        area_type_id,check_msg_state_id, handle_unit, handle_human, pass_unit, pass_human,
                        apply_type, is_phone_reply, is_reply_flag, appoint_flag, line_disruption, deal_unit_flag
                   from %(toRec)s where rec_id = %(rec_id)s """

        # 执行sql
        param = {"toRec": toRec, "rec_id": rec_id}
        rec_info = query_for_dict(biz_cur, sql % param)
        return rec_info

    def __extend_rec_info(self, biz_cur, stat_cur):
        # 扩展非to_rec表案件基本信息
        logger = logging.getLogger("main.bean.recInfo.recInfoFactory")
        rec_info = self.__data["rec_info"]
        rec_id = self.__recID
        # 责任网格编码
        try:
            if rec_info and rec_info["duty_grid_id"]:
                tcDutyGrid = schemaConst.dlsys_ + "tc_duty_grid"
                sql = "select duty_grid_code from %(tcDutyGrid)s where duty_grid_id = %(dutyGridID)s"
                param = {"tcDutyGrid": tcDutyGrid, "dutyGridID": rec_info["duty_grid_id"]}
                biz_cur.execute(sql % param)
                if biz_cur.rowcount > 0:
                    row = biz_cur.fetchone()
                    rec_info["duty_grid_code"] = row[0]
        except Exception, e:
            logger.error("duty_grid_code init error [rec_id = %s]: %s" % (rec_id, str(e)))

        # 结案类型
        try:
            if rec_info and rec_info["archive_type_id"]:
                from constant.sysConst import archive_type_dict
                if archive_type_dict.has_key(rec_info["archive_type_id"]):
                    rec_info["archive_type_name"] = archive_type_dict[rec_info["archive_type_id"]]
        except Exception, e:
            logger.error("archive_type_name init error [rec_id = %s]: %s" % (rec_id, str(e)))
        # 采集案件最后活动标识last_act_id
        try:
            if self.__data["wf_act_inst_list"]:
                self.__data["wf_act_inst_list"].sort(key=lambda x: x["act_id"])
                rec_info["last_act_id"] = self.__data["wf_act_inst_list"][-1]["act_id"]
        except:
            logger.error("last_act_id init error [rec_id = %s]: %s" % (rec_id, str(e)))
        # 采集结案意见
        try:
            if rec_info["act_property_id"] and rec_info["act_property_id"] in (101,):
                # wfItemInst = (schemaConst.dlhist_ + "to_his_wf_item_inst") if self.__isHisRec else (
                #     schemaConst.dlmis_ + "to_wf_item_inst")
                # sql = "select item_content from %(wfItemInst)s where rec_id = %(rec_id)s and item_type_id in (800)"
                # param = {"wfItemInst": wfItemInst, "rec_id": rec_id}
                # biz_cur.execute(sql % param)
                # if biz_cur.rowcount > 0:
                #     row = biz_cur.fetchone()
                #     rec_info["archive_opinion"] = row[0]
                archive_item_inst_list = filter(lambda x: x["item_type_id"] == 800, self.__data["wf_item_inst_list"])
                if archive_item_inst_list:
                    rec_info["archive_opinion"] = archive_item_inst_list[-1]["item_content"]
        except Exception, e:
            logger.error("archive_opinion init error [rec_id = %s]: %s" % (rec_id, str(e)))
        # 案件上报时段 结案时段
        try:
            if rec_info["create_time"]:
                rec_info["create_time_hours"] = rec_info["create_time"].strftime("%H")
            if rec_info["archive_time"]:
                rec_info["archive_time_hours"] = rec_info["archive_time"].strftime("%H")
        except Exception, e:
            logger.error("create_time_hours || archive_time_hours init error [rec_id = %s]: %s" % (rec_id, str(e)))

        # 采集问题状态
        """
            1 待受理: 处于采集公司节点
            2 立案未移交: 处于受理节点
            3 立案派遣: 处于值班长、派遣员节点
            4 处理中: 在专业部门阶段
            5 核查结案: 处于受理员发核查 值班长结案节点
            6 结案: 办结
            7 作废: 作废
            8 缓办: 挂账
            9 督查: 督查阶段
        """
        try:
            if rec_info["act_property_id"]:
                iActPropertyID = rec_info["act_property_id"]
                if iActPropertyID in (102,):
                    rec_info["event_state_id"] = 7
                    rec_info["event_state_name"] = u"作废"
                elif iActPropertyID in (101,):
                    rec_info["event_state_id"] = 6
                    rec_info["event_state_name"] = u"结案"
                elif iActPropertyID in (103,):
                    rec_info["event_state_id"] = 8
                    rec_info["event_state_name"] = u"缓办"
                elif iActPropertyID in (3, 4, 5, 6):
                    rec_info["event_state_id"] = 3
                    rec_info["event_state_name"] = u"立案派遣"
                elif iActPropertyID in (7, 8):
                    rec_info["event_state_id"] = 4
                    rec_info["event_state_name"] = u"处理中"
                elif iActPropertyID in (11, 12, 13, 14):
                    rec_info["event_state_id"] = 5
                    rec_info["event_state_name"] = u"核查结案"
                elif iActPropertyID in (9, 10):
                    rec_info["event_state_id"] = 9
                    rec_info["event_state_name"] = u"督查"
                elif iActPropertyID in (1, 2):
                    rec_info["event_state_id"] = 1
                    rec_info["event_state_name"] = u"待受理"
                    # recAct = schemaConst.dlmis_ + "to_rec_act"
                    # sql = "select act_def_id from %(recAct)s where rec_id = %(rec_id)s"
                    # param = {"recAct": recAct, "rec_id": rec_id}
                    # biz_cur.execute(sql % param)
                    # if biz_cur.rowcount > 0:
                    #     row = biz_cur.fetchone()
                    #     iCurActDefID = row[0]
                    #     if iCurActDefID in (216,):
                    #         rec_info["event_state_id"] = 1
                    #         rec_info["event_state_name"] = u"待受理"
                    #     else:
                    #         rec_info["event_state_id"] = 2
                    #         rec_info["event_state_name"] = u"立案未移交"
                    # else:
                    #     rec_info["event_state_id"] = 2
                    #     rec_info["event_state_name"] = u"立案未移交"

        except Exception, e:
            logger.error("event_state init error [rec_id = %s]: %s" % (rec_id, str(e)))

        # 处理挂账案件的案件活动属性
        try:
            if rec_info["act_property_id"] == 103:
                hang_trans_inst_list = filter(lambda x: x["item_type_id"] == 810, self.__data["wf_trans_inst_list"])
                if hang_trans_inst_list:
                    hang_trans_inst_list.sort(lambda x: x["trans_id"])
                    act_def_id = hang_trans_inst_list[-1]["act_def_id"]
                    sql = "select act_property_id from tc_wf_act_def where act_def_id = %s"
                    biz_cur.execute(sql % act_def_id)
                    if biz_cur.rowcount:
                        rec_info["act_property_id"] = biz_cur.fetchone()[0]
                        rec_info["real_act_property_id"] == 103
                # sql = """
                #                         select a.act_property_id from tc_wf_act_def a, to_wf_item_inst b
                #                           where a.act_def_name = b.act_def_name and b.item_type_id = 810
                #                             and b.rec_id = %s
                #                           order by b.action_time desc
                #                       """
                # biz_cur.execute(sql % rec_id)
                # if (biz_cur.rowcount > 0):
                #     row = biz_cur.fetchone()
                #     rec_info["act_property_id"] = row[0]
                #     rec_info["real_act_property_id"] = 103
        except Exception, e:
            logger.error("rec hang act_property_id init error[rec_id = %s]: %s" % (rec_id, str(e)))

    def __init_rec_wf_info(self, biz_cur, stat_cur):
        # init workflow info, include tables:
        # to_wf_act_inst, to_wf_trans_inst, to_wf_item_inst, to_rec_time_bundle, to_wf_act_ard
        #
        sql = "select * from %(wf_act_inst)s where rec_id = %(rec_id)s"
        param = {
            "wf_act_inst": schemaConst.dlhist_ + "to_his_wf_act_inst" if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst",
            "rec_id": self.__recID
        }
        self.__data["wf_act_inst_list"] = query_for_list(biz_cur, sql % param)
        sql = "select * from %(wf_trans_inst)s where rec_id = %(rec_id)s"
        param = {
            "wf_trans_inst": schemaConst.dlhist_ + "to_his_wf_trans_inst" if self.__isHisRec else schemaConst.dlmis_ + "to_wf_trans_inst",
            "rec_id": self.__recID
        }
        self.__data["wf_trans_inst_list"] = query_for_list(biz_cur, sql % param)
        sql = "select * from %(wf_item_inst)s where rec_id = %(rec_id)s"
        param = {
            "wf_item_inst": schemaConst.dlhist_ + "to_his_wf_item_inst" if self.__isHisRec else schemaConst.dlmis_ + "to_wf_item_inst",
            "rec_id": self.__recID
        }
        self.__data["wf_item_inst_list"] = query_for_list(biz_cur, sql % param)
        sql = "select * from %(rec_time_bundle)s where rec_id = %(rec_id)s"
        param = {
            "rec_time_bundle": schemaConst.dlhist_ + "to_his_rec_time_bundle" if self.__isHisRec else schemaConst.dlmis_ + "to_rec_time_bundle",
            "rec_id": self.__recID
        }
        self.__data["rec_time_bundle_list"] = query_for_list(biz_cur, sql % param)
        sql = "select * from %(wf_act_ard)s where rec_id = %(rec_id)s"
        param = {
            "wf_act_ard": schemaConst.dlhist_ + "to_his_wf_act_ard" if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_ard",
            "rec_id": self.__recID
        }
        self.__data["wf_act_ard_list"] = query_for_list(biz_cur, sql % param)
        sql = "select * from %(rec_act)s where rec_id = %(rec_id)s"
        param = {
            "rec_act": schemaConst.dlmis_ + "to_rec_act",
            "rec_id": self.__recID
        }
        self.__data["rec_act_list"] = query_for_list(biz_cur, sql % param)

    def __get_wf_act_inst_info(self, biz_cur, stat_cur):
        # 案件批转实例信息
        # @return wf_act_inst_list

        """
        活动标识、节点标识、节点、部门标识、部门、岗位标识、岗位、人员标识、人员
        达到时间、开始时间、截止时间、结束时间、活动用时、活动用时(字符)、批转意见、活动时限
        活动类型、下一节点标识、下一岗位标识、下一人员标识、下一活动标识、
        绑定截止时间、绑定用时、绑定用时(字符)、绑定时限

        说明：排除案件活动实例表中的act_state_id = 0(发核查、发核实)的活动， 排除协办活动
        """
        logger = logging.getLogger("main.bean.recInfo.recInfoFactory")

        wf_trans_act_list = []
        wf_act_inst_list = self.__data["wf_act_inst_list"] if self.__data["wf_act_inst_list"] else []
        wf_trans_inst_list = self.__data["wf_trans_inst_list"] if self.__data["wf_trans_inst_list"] else []
        wf_item_inst_list = self.__data["wf_item_inst_list"] if self.__data["wf_item_inst_list"] else []
        wf_act_ard_list = self.__data["wf_act_ard_list"] if self.__data["wf_act_ard_list"] else []
        rec_time_bundle_list = self.__data["rec_time_bundle_list"] if self.__data["rec_time_bundle_list"] else []
        wf_act_inst_list.sort(key=lambda x: x["act_id"])
        for wf_act_inst_dict in wf_act_inst_list:
            act_id = wf_act_inst_dict["act_id"]
            wf_trans_act_dict = {
                "act_id": wf_act_inst_dict["act_id"],
                "act_def_id": wf_act_inst_dict["act_def_id"],
                "act_def_name": wf_act_inst_dict["act_def_name"],
                "unit_id": wf_act_inst_dict["unit_id"],
                "unit_name": wf_act_inst_dict["unit_name"],
                "role_id": wf_act_inst_dict["role_id"],
                "role_name": wf_act_inst_dict["role_name"],
                "human_id": wf_act_inst_dict["human_id"],
                "human_name": wf_act_inst_dict["humanname"],
                "create_time": wf_act_inst_dict["create_time"],
                "start_time": wf_act_inst_dict["start_time"],
                "deadline_time": wf_act_inst_dict["deadline_time"],
                "end_time": wf_act_inst_dict["end_time"],
                "act_used": wf_act_inst_dict["act_used"],
                "act_used_char": wf_act_inst_dict["act_used_char"],
                "trans_opinipn": wf_act_inst_dict["trans_opinion"],
                "act_limit": wf_act_inst_dict["act_deadline"],
                # 流向信息
                "next_role_id": None,
                "item_type_id": None,
                "next_act_def_id": None,
                "next_act_id": None,
                # 捆绑计时信息
                "bundle_used": wf_act_inst_dict["act_used"],
                "bundle_used_char": wf_act_inst_dict["act_used_char"],
                "bundle_limit": wf_act_inst_dict["act_deadline"],
                "bundle_deadline": wf_act_inst_dict["deadline_time"],
            }
            temp_trans_inst_list = filter(lambda x: x["act_id"] == act_id, wf_trans_inst_list)
            if temp_trans_inst_list:
                temp_trans_inst_list.sort(key=lambda x: x["trans_id"])
                wf_trans_inst_dict = temp_trans_inst_list[-1]
                wf_trans_act_dict["next_role_id"] = wf_trans_inst_dict["next_role_id"]
                wf_trans_act_dict["item_type_id"] = wf_trans_inst_dict["item_type_id"]
                wf_trans_act_dict["next_act_def_id"] = wf_trans_inst_dict["next_act_def_id"]
                wf_trans_act_dict["next_act_id"] = wf_trans_inst_dict["next_act_id"]

            temp_rec_time_bundle_list = filter(lambda x: x["act_id"] == act_id, rec_time_bundle_list)
            if temp_rec_time_bundle_list:
                temp_rec_time_bundle_list.sort(key=lambda x: x["refresh_time"])
                rec_time_bundle_dict = temp_rec_time_bundle_list[-1]
                wf_trans_act_dict["bundle_used"] = rec_time_bundle_dict["bundle_used"]
                wf_trans_act_dict["bundle_used_char"] = rec_time_bundle_dict["bundle_used_char"]
                wf_trans_act_dict["bundle_limit"] = rec_time_bundle_dict["bundle_limit"]
                wf_trans_act_dict["bundle_deadline"] = rec_time_bundle_dict["bundle_deadline"]

            wf_trans_act_list.append(wf_trans_act_dict)

        return wf_trans_act_list

        # rec_id = self.__recID
        # wfParam = {}
        # wfParam["rec_id"] = rec_id
        # wfParam["wfActInst"] = (schemaConst.dlhist_ + "to_his_wf_act_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_inst"
        # wfParam["wfTransInst"] = (schemaConst.dlhist_ + "to_his_wf_trans_inst") if self.__isHisRec else schemaConst.dlmis_ + "to_wf_trans_inst"
        # # wfParam["recTimeBundle"] = (schemaConst.dlhist_ + "to_his_rec_time_bundle") if self.__isHisRec else schemaConst.dlmis_ + "to_rec_time_bundle"
        # wfParam["recTimeBundle"] = schemaConst.dlmis_ + "to_rec_time_bundle"
        #
        # # 案件活动实例
        # act_inst_sql = """select act_id, act_def_id, act_def_name, unit_id, unit_name, role_id, role_name, human_id, human_name,
        #                          create_time, start_time, deadline_time, end_time, act_used, act_used_char, trans_opinion,
        #                          act_deadline as act_limit
        #                     from %(wfActInst)s
        #                     where rec_id = %(rec_id)s and act_state_id > 0 and pri_sub_type_id in (0, 1)
        #                     order by create_time, act_id
        #                """
        # # 案件活动流向实例
        # trans_inst_sql = """select act_id, act_def_id, item_type_id, next_act_def_id, next_role_id, next_human_id, next_act_id
        #                       from %(wfTransInst)s where rec_id = %(rec_id)s order by trans_id
        #                  """
        # # 案件绑定计时活动实例
        # bundle_inst_sql = """select act_id, bundle_id, act_def_id, bundle_used, bundle_used_char, deadline_time as bundle_deadline,
        #                             deadline_limit as bundle_limit
        #                        from %(recTimeBundle)s where rec_id = %(rec_id)s
        #                   """
        #
        # wf_act_inst_list = query_for_list(biz_cur, act_inst_sql % wfParam)
        # wf_trans_inst_list = query_for_list(biz_cur, trans_inst_sql % wfParam)
        # rec_time_bundle_list = query_for_list(biz_cur, bundle_inst_sql % wfParam)
        # # 创建案件批转活动列表
        # wf_trans_act_list = []
        # try:
        #     for wf_act_inst_dict in wf_act_inst_list:
        #         wf_trans_act_dict = {}
        #         copy(wf_act_inst_dict, wf_trans_act_dict)
        #         actID = wf_act_inst_dict["act_id"]
        #         actDefID = wf_act_inst_dict["act_def_id"]
        #         # 批转相关信息
        #         for wf_trans_inst_dict in wf_trans_inst_list:
        #             if wf_trans_inst_dict["act_id"] == actID:
        #                 wf_trans_act_dict["next_role_id"] = wf_trans_inst_dict["next_role_id"]
        #                 wf_trans_act_dict["item_type_id"] = wf_trans_inst_dict["item_type_id"]
        #                 wf_trans_act_dict["next_act_def_id"] = wf_trans_inst_dict["next_act_def_id"]
        #                 wf_trans_act_dict["next_act_id"] = wf_trans_inst_dict["next_act_id"]
        #         if not wf_trans_act_dict.has_key("next_role_id"):
        #             wf_trans_act_dict["next_role_id"] = None
        #             wf_trans_act_dict["item_type_id"] = None
        #             wf_trans_act_dict["next_act_def_id"] = None
        #             wf_trans_act_dict["next_act_id"] = None
        #         # 绑定计时相关信息
        #         for rec_time_bundle_dict in rec_time_bundle_list:
        #             if rec_time_bundle_dict["act_id"] == actID and rec_time_bundle_dict["act_def_id"] == actDefID:
        #                 wf_trans_act_dict["bundle_used"] = rec_time_bundle_dict["bundle_used"]
        #                 wf_trans_act_dict["bundle_used_char"] = rec_time_bundle_dict["bundle_used_char"]
        #                 wf_trans_act_dict["bundle_limit"] = rec_time_bundle_dict["bundle_limit"]
        #                 wf_trans_act_dict["bundle_deadline"] = rec_time_bundle_dict["bundle_deadline"]
        #
        #         # 如果没有绑定信息，则把当前阶段信息赋给绑定信息
        #         if not wf_trans_act_dict.has_key("bundle_used"):
        #             wf_trans_act_dict["bundle_used"] = wf_trans_act_dict["act_used"]
        #             wf_trans_act_dict["bundle_used_char"] = wf_trans_act_dict["act_used_char"]
        #             wf_trans_act_dict["bundle_limit"] = wf_trans_act_dict["act_limit"]
        #             wf_trans_act_dict["bundle_deadline"] = wf_trans_act_dict["deadline_time"]
        #         if wf_trans_act_dict:
        #             wf_trans_act_list.append(wf_trans_act_dict)
        # except Exception, e:
        #     logger.error("wf_trans_act_list init error: %s" % str(e))
        #     wf_trans_act_list = []
        # return wf_trans_act_list

    def __get_patrol_task_info(self, biz_cur, stat_cur):
        # 获取监督员核查核实任务信息
        # @return: 结果格式list<dict>

        # patrolTask = (schemaConst.dlhist_ + "to_mi_patrol_task_history") if self.__isHisRec else schemaConst.dlmis_ + "to_mi_patrol_task"
        """
            主键 案件标识 创建时间 完成标识 完成时间 接收标识 接收时间
            工卡号 发送人员标识(human_id) 任务类型 读取标识 读取时间
            作废标识 作废时间 任务号 任务用时
        """
        rec_id = self.__recID
        patrolTask = schemaConst.dlmis_ + "to_mi_patrol_task"
        sql = """select patrol_task_id, rec_id, create_time, done_flag, done_time, receive_flag, receive_time,
                        card_id, human_id, task_type, read_flag, read_time, 
                        cancel_flag, cancel_time, task_num, used_time
                 from %(patrolTask)s where rec_id = %(rec_id)s
              """
        param = {"patrolTask": patrolTask, "rec_id": rec_id}
        patrol_task_list = query_for_list(biz_cur, sql % param)
        
        hisPatrolTask = schemaConst.dlhist_ + "to_his_mi_patrol_task"
        sql = """select patrol_task_id, rec_id, create_time, done_flag, done_time, receive_flag, receive_time,
                        card_id, human_id, task_type, read_flag, read_time, 
                        cancel_flag, cancel_time, task_num, used_time
                 from %(hisPatrolTask)s where rec_id = %(rec_id)s
              """
        param = {"hisPatrolTask": hisPatrolTask, "rec_id": rec_id}
        his_patrol_task_list = query_for_list(biz_cur, sql % param)
        # 合并监督员任务与历史任务
        if patrol_task_list:
            if his_patrol_task_list:
                patrol_task_list = patrol_task_list + his_patrol_task_list
        else:
            patrol_task_list = his_patrol_task_list
        return patrol_task_list;

    def __get_act_ard_info(self, biz_cur, stat_cur):
        # 获取案件授权信息
        # @return 结果格式list<dict>
        """
            授权状态标识(act_ard_state_id) 
            申请授权活动标识(apply_act_id) 申请授权时间(apply_date) 申请授权参与者标识(apply_part_id)
            答复授权活动标识(reply_act_id) 答复授权时间(reply_date) 答复授权参与者标识(reply_part_id)
        """
        # rec_id = self.__recID
        # wf_act_ard = schemaConst.dlhist_ + "to_his_wf_act_ard" if self.__isHisRec else schemaConst.dlmis_ + "to_wf_act_ard"
        # sql = """select act_ard_state_id, apply_act_id, apply_date, apply_part_id,
        #                 reply_act_id, reply_date, reply_part_id
        #          from %(wf_act_ard)s where rec_id = %(rec_id)s"""
        # param = {"wf_act_ard": wf_act_ard, "rec_id": rec_id}
        # act_ard_list = query_for_list(biz_cur, sql % param)
        return self.__data["wf_act_ard_list"]

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
    def get_data(self, key=None):
        if key and key in self.__data:
            return self.__data[key]
        else:
            return self.__data

# if __name__ == "__main__":
#     from tools.utils import get_statdb_conn, get_bizdb_conn
#     # stat_conn = get_statdb_conn()
#     # biz_conn = get_bizdb_conn()
#     stat_cur = get_statdb_conn().cursor()
#     biz_cur = get_bizdb_conn().cursor()
#     recInfo1 = recInfoFactory(stat_cur = stat_cur, biz_cur = biz_cur, rec_id = 3461)
#     recInfo2 = recInfoFactory(stat_cur = stat_cur, biz_cur = biz_cur, rec_id = 3465)
#     print recInfo1.get_data("rec_id")
#     print recInfo2.get_data("rec_id")
#     testFile = open("test.txt", "w")
#     testFile.write(str(recInfo1.get_data()))