#coding: utf-8
"""
    zwx 2016-05-27
    系统工具方法
    get_human_byID 返回 人员标识 人员 所属部门标识 所属部门 所属区域标识 所属区域 所属区域类型
    get_region_byID 返回 区域标识 区域 区域类型 上级区域标识
    get_unit_byID 返回 部门标识 部门 区域标识 上级部门标识 所属区域标识 所属区域 所属区域类型
    get_role_byID 返回 岗位标识 岗位 所属部门标识 所属部门 所属部门上级部门 部门所属区域标识 部门所属区域 部门所属区域类型
    get_patrol_byID 返回 监督员标识 监督员 工卡号 所属部门标识 所属部门 所属区域标识 所属区域
    get_part_byPartID 返回 人员标识 人员 岗位标识 岗位 部门标识 部门 参与者类型
"""
from utils import query_for_dict
import sys
sys.path.append("..")
import constant.schemaConst as schemaConst

def get_human_byID(cur, human_id):
    # @return
    # 人员标识 人员 所属部门标识 所属部门 所属区域标识 所属区域 所属区域类型
    sql = "select a.human_id, a.human_name, a.unit_id, a.region_id, a.region_type, b.unit_name, c.region_name " +\
          "from %(tc_human)s a, %(tc_unit)s b, %(tc_region)s c where a.human_id = %(human_id)s and b.unit_id = a.unit_id and c.region_id = a.region_id"
    param = {"tc_human": schemaConst.dlsys_ + "tc_human", "tc_unit": schemaConst.dlsys_ + "tc_unit", "tc_region": schemaConst.dlsys_ + "tc_region", "human_id": human_id}
    human = query_for_dict(cur, sql % param)
    return human

def get_region_byID(cur, region_id):
    # @return
    # 区域标识 区域 区域类型 上级区域标识
    sql = "select region_id, region_name, region_type, senior_id from %(tc_region)s where region_id = %(region_id)s "
    param = {"tc_region": schemaConst.dlsys_ + "tc_region", "region_id": region_id}
    region = query_for_dict(cur, sql % param)
    return region

def get_unit_byID(cur, unit_id):
    # @return
    # 部门标识 部门 区域标识 上级部门标识 所属区域标识 所属区域 所属区域类型
    sql = "select a.unit_id, a.unit_name, a.region_id, a.senior_id, b.region_name, b.region_type" + \
          "  from %(tc_unit)s a, %(tc_region)s b" + \
          "  where a.unit_id = %(unit_id)s and b.region_id = a.region_id"
    param = {"tc_unit": schemaConst.dlsys_ + "tc_unit", "tc_region": schemaConst.dlsys_ + "tc_region", "unit_id": unit_id}
    unit = query_for_dict(cur, sql % param)
    if unit:
        try:
            cur.execute("select unit_name from %s where unit_id = %s" % (schemaConst.dlsys_ + "tc_unit", unit["senior_id"]))
            row = cur.fetchone()
            unit["senior_name"] = row[0]
        except:
            unit["senior_name"] = ""
    return unit

def get_role_byID(cur, role_id):
    # 岗位标识 岗位 所属部门标识 所属部门 所属部门上级部门 部门所属区域标识 部门所属区域 部门所属区域类型
    sql = "select a.role_id, a.role_name, a.unit_id, b.unit_name, b.senior_id, b.region_id, c.region_name, c.region_type " + \
          " from %(tc_role)s a, %(tc_unit)s b, %(tc_region)s c " + \
          " where a.role_id = %(role_id)s and b.unit_id = a.unit_id and c.region_id = b.region_id "
    param = {"tc_role": schemaConst.dlsys_ + "tc_role", "tc_unit": schemaConst.dlsys_ + "tc_unit", "tc_region": schemaConst.dlsys_ + "tc_region", "role_id": role_id}
    role = query_for_dict(cur, sql % param)
    return role

def get_patrol_byID(cur, patrol_id):
    # 监督员标识 监督员 工卡号 所属部门标识 所属部门 所属区域标识 所属区域
    sql = "select a.patrol_id, a.patrol_name, a.card_id, b.unit_id, c.unit_name, b.region_id, d.region_name " + \
          "  from %(tc_patrol)s a, %(tc_human)s b, %(tc_unit)s c, %(tc_region)s d" + \
          "  where a.patrol_id = %(patrol_id)s and b.human_id = a.patrol_id and c.unit_id = b.unit_id and d.region_id = b.region_id "
    param = {}
    param["tc_patrol"] = schemaConst.dlsys_ + "tc_patrol"
    param["tc_human"] = schemaConst.dlsys_ + "tc_human"
    param["tc_unit"] = schemaConst.dlsys_ + "tc_unit"
    param["tc_region"] = schemaConst.dlsys_ + "tc_region"
    param["patrol_id"] = patrol_id
    return query_for_dict(cur, sql % param)

def get_patrol_byCardID(cur, card_id):
    # 监督员标识 监督员 工卡号 所属部门标识 所属部门 所属区域标识 所属区域
    sql = "select a.patrol_id, a.patrol_name, a.card_id, b.unit_id, c.unit_name, b.region_id, d.region_name " + \
          "  from %(tc_patrol)s a, %(tc_human)s b, %(tc_unit)s c, %(tc_region)s d" + \
          "  where a.card_id = '%(card_id)s' and b.human_id = a.patrol_id and c.unit_id = b.unit_id and d.region_id = b.region_id "
    param = {}
    param["tc_patrol"] = schemaConst.dlsys_ + "tc_patrol"
    param["tc_human"] = schemaConst.dlsys_ + "tc_human"
    param["tc_unit"] = schemaConst.dlsys_ + "tc_unit"
    param["tc_region"] = schemaConst.dlsys_ + "tc_region"
    param["card_id"] = card_id
    return query_for_dict(cur, sql % param)

def get_part_byPartID(cur, part_id):
    # 人员标识 人员 岗位标识 岗位 部门标识 部门 参与者类型
    sql = "select a.human_id, a.human_name, a.role_id, a.role_name, a.unit_id, a.unit_name, a.part_type " + \
          "  from %(tc_part)s where part_id = %(part_id)s"
    param = {}
    param["tc_part"] = schemaConst.dlsys_ + "tc_part"
    param["part_id"] = part_id
    return query_for_dict(cur, sql % param)