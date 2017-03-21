# -*- coding: utf-8 -*-

VERSION = 2.0

# 数据库配置
# dbTypeName 数据库类型 oracle | mysql
# stat_conn 统计库连接配置
# stat_db_name 统计库名称
# biz_conn 业务库连接配置
# biz_db_name 业务库名称
dbTypeName = "mysql"
stat_conn = {
    "host": "127.0.0.1",
    "port": 3306,
    "db": "nbcgstat",
    "user": "root",
    "password": "admin",
    "charset": "utf8"
}
stat_db_name = "nbcgstat"
biz_conn = {
    "host": "127.0.0.1",
    "port": 3306,
    "db": "nbcg",
    "user": "root",
    "password": "admin",
    "charset": "utf8"
}
biz_db_name = "nbcg"
# ================================================================
# 采集配置
# 监督员上报问题来源标识
patrol_report_src_tuple = (1,)
# 受理阶段活动属性
ACCEPTOR_PROP = (1,2)
# 值班长阶段活动属性
GANGER_PROP = (3,4)
# 市派遣阶段活动属性
DISPATCH_PROP = (6,)
# 区派遣阶段活动属性
SECOND_DISPATCH_PROP = (5,)
# 处置阶段活动属性
DISPOSE_PROP = (7,8)
# 督查阶段活动属性
SUPERVISE_PROP = (9,10)
# 核查阶段活动属性
CHECK_PROP = (11,13)
# 值班长结案阶段
HUMAN_ARCHIVE_PROP = (12,14)
# 存档
FINISH_PROP = (101,)
# 作废
CANCEL_PROP = (102,)

# 监督员核查时限
CHECK_LIMIT = 120
VERIFY_LIMIT = 120

# 发核查核实时限
SEND_CHECK_LIMIT = 30
SEND_VERIFY_LIMIT = 30

street_check_limit = 60
town_check_limit = 120

# 采集间隔时间,单位秒
gather_interval = 300 * 1
# 默认计时方案
default_time_sys_id = 1
