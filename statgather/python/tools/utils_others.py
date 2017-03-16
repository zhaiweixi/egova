# -*- coding:utf-8 -*-
import sys
sys.path.append("..")
import settings
from datetime import date, datetime
import time
import logging
import logging.config
"""
    zwx 2016-04-01
    工具方法
    获取数据库连接方法 get_bizdb_conn get_statdb_conn
    获取查询结果方法 query_for_list query_for_dict
    插入数据库方法 insert_one insert_many
    复制dict方法 copy_dict2dict
    转数据库日期字符串 toDbDateStr
    获取数据库时间 get_db_now
"""
def get_bizdb_conn():
    # 获取城管数据库连接
    if settings.dbTypeName.lower() == "oracle":
        import cx_Oracle
        user = settings.biz_conn["user"]
        password = settings.biz_conn["password"]
        db = settings.biz_conn["host"] + ":" + str(settings.biz_conn["port"]) + "/" + settings.biz_conn["db"]
        conn = cx_Oracle.connect(user, password, db)
    elif settings.dbTypeName.lower() == "mysql":
        import pymysql
        conn = pymysql.connect(**settings.biz_conn)
    else:
        # 默认数据库连接为mysql
        import pymysql
        conn = pymysql.connect(**settings.biz_conn)
    return conn

def get_statdb_conn():
    # 获取统计数据库连接
    if settings.dbTypeName.lower() == "oracle":
        import cx_Oracle
        user = settings.stat_conn["user"]
        password = settings.stat_conn["password"]
        db = settings.stat_conn["host"] + ":" + str(settings.stat_conn["port"]) + "/" + settings.stat_conn["db"]
        conn = cx_Oracle.connect(user, password, db)
    elif settings.dbTypeName.lower() == "mysql":
        import pymysql
        conn = pymysql.connect(**settings.stat_conn)
    else:
        # 默认数据库连接为mysql
        import pymysql
        conn = pymysql.connect(**settings.stat_conn)
    return conn

def query_for_list(cur, sql, param=None):
    # 返回全部查询结果
    # @return list[dict]格式
    logger = logging.getLogger("main.tools.utils")
    result_list = []
    try:
        if param:
            cur.execute(sql, param)
        else:
            cur.execute(sql)
        columns = [val[0].lower() for val in cur.description]
        results = cur.fetchall()
        for result in results:
            result_dict = dict(zip(columns, result))
            result_list.append(result_dict)
    except Exception, e:
        logger.error("select error [%s]:[%s]:[%s]" %(sql, param, str(e)))
        result_list = None
    return result_list

def query_for_dict(cur, sql, param=None):
    # 返回案件单条查询结果
    # @return dict格式
    result_dict = {}
    try:
        if param:
            cur.execute(sql, param)
        else:
            cur.execute(sql)
        columns = [val[0].lower() for val in cur.description]
        result_dict = dict(zip(columns, cur.fetchone()))
    except Exception, e:
        result_dict = None
    return result_dict

def gen_insert_sql_one(table_name, table_dict, field_tuple):
    # 生成插入语句对象
    # {"sql": sql, "param": param}格式
    # [oracle] 
    # insert into table_name (field1, field2, field3 ...) values(:1, :2, :3 ...)
    # (value1, value2, value3 ...)
    # [mysql]
    # insert into table_name (field1, field2, field3 ...) values(%s, %s, %s ...)
    # (value1, value2, value3 ...)

    field_str = ""
    value_str = ""
    value_param_list = []
    param_order = 1
    for key, value in table_dict.items():
        if key in field_tuple and (value or value == 0):
            field_str += ", " + key
            if (settings.dbTypeName == "oracle"):
                value_str += ", :" + str(param_order)
            else:
                value_str += ", %s"
            value_param_list.append(value)
            param_order += 1
            continue
        else:
            continue
    if len(field_str) > 0:
        sql = "insert into %s (%s) values (%s)" % (table_name, field_str[1:], value_str[1:])
    else:
        return None
    return {"sql": sql, "param": tuple(value_param_list)}

def insert_one(cur, table_name, data_dict, field_tuple):
    # 插入单条数据
    # @param cur 数据库游标
    # @param table_name 表名称
    # @param data_dict 要插入的数据字典
    # @param field_tuple 表的字段元组
    insert_dict = gen_insert_sql_one(table_name, data_dict, field_tuple)
    logger = logging.getLogger("main.tools.utils")
    if insert_dict:
        cur.execute(insert_dict["sql"], insert_dict["param"])

def insert_many(cur, table_name, data_list, field_tuple):
    # 批量插入
    # @param cur 数据库游标
    # @param table_name 表名称
    # @param data_dict 要插入的数据列表
    # @param field_tuple 表的字段元组
    for data_dict in data_list:
        insert_one(cur, table_name, data_dict, field_tuple)

def copy_dict2dict(from_dict, to_dict):
    # 复制字典
    for key, value in from_dict.items():
        to_dict[key] = value

def toDbDateStr(date_str):
    # 将字符串转成对应数据库的日期类型字符串
    # @param date_str yyyy-mm-dd hh24:mi:ss
    # return 字符串
    if settings.dbTypeName.lower() == "oracle":
        return "to_date('" + date_str + "', 'yyyy-mm-dd hh24:mi:ss')"
    elif settings.dbTypeName.lower() == "mysql":
        return "str_to_date('" + date_str + "', '%Y-%m-%d %H:%i:%s')"
    else:
        return "str_to_date('" + date_str + "', '%Y-%m-%d %H:%i:%s')"

def get_db_now(cur):
    if settings.dbTypeName.lower() == "oracle":
        cur.execute("select sysdate from dual")
        return cur.fetchone()[0]
    elif settings.dbTypeName.lower() == "mysql":
        cur.execute("select now()")
        return cur.fetchone()[0]
    else:
        return datetime.now()