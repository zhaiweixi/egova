# coding:utf-8
"""
   zwx 2016-05-27
   系统配置信息
"""
import sys
sys.path.append("..")
from tools.utils import query_for_list
import constant.schemaConst as schemaConst

class sysInfoFactory(object):
    def __init__(self, biz_cur, stat_cur):
        # self.__data = {}
        # self.__data["timing_dict"] = {}
        # self.__data["timing_dict"]["schedule"] = self.__get_schedule(biz_cur = biz_cur)
        # self.__data["timing_dict"]["calendar"] = self.__get_calendar(biz_cur = biz_cur)
        self.__data = {
            "timing_dict": {
                "schedule": self.__get_schedule(biz_cur = biz_cur),
                "calendar": self.__get_calendar(biz_cur = biz_cur)
            }
        }

        self.__initActDefInfo(biz_cur = biz_cur)
        self.__init_region(biz_cur = biz_cur)
        self.__init_human(biz_cur = biz_cur)
        self.__init_role(biz_cur = biz_cur)
        self.__init_unit(biz_cur = biz_cur)
        self.__init_patrol(biz_cur = biz_cur)

    @staticmethod
    def __get_schedule(biz_cur):
        sql = "select * from %s" % (schemaConst.dlsys_ + "tc_sys_schedule")
        return query_for_list(biz_cur, sql)

    @staticmethod
    def __get_calendar(biz_cur):
        sql = "select * from %s" % (schemaConst.dlsys_ + "tc_sys_calendar")
        return query_for_list(biz_cur, sql)

    # 初始化工作流节点集合
    def __initActDefInfo(self, biz_cur):
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

    # 初始区域信息
    # 2016-11-17 zwx 只缓存到社区级别
    def __init_region(self, biz_cur):
        self.__data["region"] = {}
        sql = "select region_id, region_name, region_type, senior_id from " + schemaConst.dlsys_ + "tc_region where region_type < 5"
        biz_cur.execute(sql)
        rows = biz_cur.fetchall()
        for row in rows:
            self.__data["region"][row[0]] = {
                "region_id": row[0],
                "region_name": row[1],
                "region_type": row[2],
                "senior_id": row[3]
            }

    # 初始化人员信息
    def __init_human(self, biz_cur):
        self.__data["human"] = {}
        sql = "select human_id, human_name, region_id, region_type, unit_id from " + schemaConst.dlsys_ + "tc_human"
        biz_cur.execute(sql)
        rows = biz_cur.fetchall()
        for row in rows:
            self.__data["human"][row[0]] = {
                "human_id": row[0],
                "human_name": row[1],
                "region_id": row[2],
                "region_type": row[3],
                "unit_id": row[4]
            }

    # 初始化岗位信息
    def __init_role(self, biz_cur):
        self.__data["role"] = {}
        sql = "select role_id, role_name, unit_id from " + schemaConst.dlsys_ + "tc_role"
        biz_cur.execute(sql)
        rows = biz_cur.fetchall()
        for row in rows:
            self.__data["role"][row[0]] = {
                "role_id": row[0],
                "role_name": row[1],
                "unit_id": row[2]
            }

    # 初始化部门信息
    def __init_unit(self, biz_cur):
        self.__data["unit"] = {}
        sql = "select unit_id, unit_name, senior_id, region_id, region_type from " + schemaConst.dlsys_ + "tc_unit"
        biz_cur.execute(sql)
        rows = biz_cur.fetchall()
        for row in rows:
            self.__data["unit"][row[0]] = {
                "unit_id": row[0],
                "unit_name": row[1],
                "senior_id": row[2],
                "region_id": row[3],
                "region_type": row[4]
            }

    # 初始化监督员信息, 生成两个字典, 分别以patrol_id card_id为键
    def __init_patrol(self, biz_cur):
        self.__data["patrol"] = {}
        self.__data["patrol_card"] = {}
        sql = "select a.patrol_id, a.patrol_name, a.card_id, a.region_id, b.unit_id as unit_id from " + schemaConst.dlsys_ + "tc_patrol a, " + schemaConst.dlsys_ + "tc_human b "
        sql += "where b.human_id = a.patrol_id"
        biz_cur.execute(sql)
        rows = biz_cur.fetchall()
        for row in rows:
            self.__data["patrol"][row[0]] = {
                "patrol_id": row[0],
                "patrol_name": row[1],
                "card_id": row[2],
                "region_id": row[3],
                "unit_id": row[4]
            }
            self.__data["patrol_card"][row[2]] = {
                "patrol_id": row[0],
                "patrol_name": row[1],
                "card_id": row[2],
                "region_id": row[3],
                "unit_id": row[4]
            }

    def getSysInfo(self):
        return self.__data

    def get_data(self, key = None):
        if key and key in self.__data:
            return self.__data[key]
        else:
            return None

# if __name__ == "__main__":
#     from tools.utils import get_statdb_conn, get_bizdb_conn
#     stat_cur = get_statdb_conn().cursor()
#     biz_cur = get_bizdb_conn().cursor()

#     sysInfo = sysInfoFactory(stat_cur = stat_cur, biz_cur = biz_cur)
#     testFile = open("test.txt", "w")
#     testFile.write(str(sysInfo.get_data()))