#coding:utf-8
"""
   zwx 2016-05-27
   系统配置信息
"""
import sys
sys.path.append("..")
from tools.utils import query_for_list, query_for_dict
import constant.schemaConst as schemaConst

class sysInfoFactory(object):
    def __init__(self, biz_cur, stat_cur):
        self.__data = {}
        self.__data["timing_dict"] = {}
        self.__data["timing_dict"]["schedule"] = self.__get_schedule(stat_cur = stat_cur, biz_cur = biz_cur)
        self.__data["timing_dict"]["calendar"] = self.__get_calendar(stat_cur = stat_cur, biz_cur = biz_cur)
        # 受理节点号集合
        self.__data["accept_actdef_ids"] = []
        # 立案节点号集合
        self.__data["inst_actdef_ids"] = []
        # 派遣节点号集合
        self.__data["dispatch_actdef_ids"] = []
        # 处置节点号集合
        self.__data["dispose_actdef_ids"] = []
        # 督查节点号集合
        self.__data["supervise_actdef_ids"] = []
        # 核查节点号集合
        self.__data["check_actdef_ids"] = []
        # 值班长结案节点号集合
        self.__data["archive_actdef_ids"] = []
        # 办结节点号集合
        self.__data["finish_actdef_ids"] = []
        # 作废节点号集合
        self.__data["cancel_actdef_ids"] = []
        # 缓办节点号集合
        self.__data["hang_actdef_ids"] = []

        self.__initActDefInfo(stat_cur = stat_cur, biz_cur = biz_cur)

    def __get_schedule(self, stat_cur, biz_cur):
        sql = "select * from %s" % (schemaConst.dlsys_ + "tc_sys_schedule")
        return query_for_list(biz_cur, sql)

    def __get_calendar(self, stat_cur, biz_cur):
        sql = "select * from %s" % (schemaConst.dlsys_ + "tc_sys_calendar")
        return query_for_list(biz_cur, sql)
    # 初始化工作流节点集合
    def __initActDefInfo(self, stat_cur, biz_cur):
        act_def_ids_dict = {}
        sql = "select act_property_id, act_def_id from %s where proc_def_ver = 0" % (schemaConst.dlsys_ + "tc_wf_act_def")
        biz_cur.execute(sql)
        rows = biz_cur.fetchall()
        for row in rows:
            if row[0] in (1, 2):
                self.__data["accept_actdef_ids"].append(row[1])
            elif row[0] in (3, 4):
                self.__data["inst_actdef_ids"].append(row[1])
            elif row[0] in (5, 6):
                self.__data["dispatch_actdef_ids"].append(row[1])
            elif row[0] in (7, 8):
                self.__data["dispose_actdef_ids"].append(row[1])
            elif row[0] in (9, 10):
                self.__data["supervise_actdef_ids"].append(row[1])
            elif row[0] in (11, 13):
                self.__data["check_actdef_ids"].append(row[1])
            elif row[0] in (12, 14):
                self.__data["archive_actdef_ids"].append(row[1])
            elif row[0] in (101, ):
                self.__data["finish_actdef_ids"].append(row[1])
            elif row[0] in (102, ):
                self.__data["cancel_actdef_ids"].append(row[1])
            elif row[0] in (103, ):
                self.__data["hang_actdef_ids"].append(row[1])

    def getSysInfo(self):
        import copy
        return copy.deepcopy(self.__data)

    def get_data(self, key = None):
        import copy
        if key:
            if (self.__data.has_key(key)):
                return copy.deepcopy(self.__data[key])
            else:
                return None
        else:
            return copy.deepcopy(self.__data)

# if __name__ == "__main__":
#     from tools.utils import get_statdb_conn, get_bizdb_conn
#     stat_cur = get_statdb_conn().cursor()
#     biz_cur = get_bizdb_conn().cursor()

#     sysInfo = sysInfoFactory(stat_cur = stat_cur, biz_cur = biz_cur)
#     testFile = open("test.txt", "w")
#     testFile.write(str(sysInfo.get_data()))