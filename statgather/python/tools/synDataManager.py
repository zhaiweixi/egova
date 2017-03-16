#coding: utf-8
import sys
sys.path.append("..")
from tools.utils import get_bizdb_conn, get_statdb_conn
import constant.schemaConst as schemaConst
import settings

def transferOnlyDataBiz2Stat(biz_conn, stat_conn, tableName):
    biz_cur = biz_conn.cursor()
    stat_cur = stat_conn.cursor()

    sql = " select * from %s " % tableName
    biz_cur.execute(sql)
    column_list = (val[0] for val in biz_cur.description)
    rows = biz_cur.fetchall()
    field_str = ""
    for column_name in column_list:
        field_str += "," + column_name

    try:
        stat_cur.execute("delete from %s" % tableName)
        for row in rows:
            value_str = ""
            value_param_list = []
            value_order = 1
            for item in row:
                if (settings.dbTypeName == "oracle"):
                    value_str += ", :" + str(value_order)
                else:
                    value_str += ",%s"
                value_param_list.append(item)
                value_order += 1

            insert_sql = "insert into %s (%s) values (%s) " % (tableName, field_str[1:], value_str[1:])
            stat_cur.execute(insert_sql, value_param_list)

        stat_conn.commit()
        print tableName, u"迁移成功"
        print "+--------------------------+"
    except Exception, e:
        stat_conn.rollback()
        print tableName, u"迁移失败，原因:"
        print e
        print "+--------------------------+"
    stat_cur.close()
    biz_cur.close()
    return 

def transferTableAllBiz2Stat(stat_conn, biz_conn, fromUserName, toUserName, tableName):
    pass

def get_need_syn_table(commandName):
    need_syn_table = []
    need_syn_table.append(schemaConst.dlsys_ + "tc_human")
    need_syn_table.append(schemaConst.dlsys_ + "tc_unit")
    need_syn_table.append(schemaConst.dlsys_ + "tc_role")
    need_syn_table.append(schemaConst.dlsys_ + "tc_human_role")
    need_syn_table.append(schemaConst.dlsys_ + "tc_part")
    need_syn_table.append(schemaConst.dlsys_ + "tc_region")
    need_syn_table.append(schemaConst.dlsys_ + "tc_sys_info")
    need_syn_table.append(schemaConst.dlsys_ + "tc_dic_event_any_type")
    need_syn_table.append(schemaConst.dlsys_ + "tc_dic_data_type")
    need_syn_table.append(schemaConst.dlsys_ + "tc_dic_event_src")
    need_syn_table.append(schemaConst.dlsys_ + "tc_dic_event_rec_type")
    need_syn_table.append(schemaConst.dlsys_ + "tc_dic_act_property")
    need_syn_table.append(schemaConst.dlsys_ + "tc_wf_trans_def")
    need_syn_table.append(schemaConst.dlsys_ + "tc_wf_act_part")
    need_syn_table.append(schemaConst.dlsys_ + "tc_wf_act_def")
    if commandName == "0":
        return need_syn_table
    else:
        commandID = int(commandName)
        return need_syn_table[commandID-1 : commandID]

def print_help_info():
    try:
        import readline
    except:
        print u"自动补全模块readline加载失败"
    print u"帮助:"
    print u"如果需要同步全部，请输入命令: 0"
    print u"同步人员(tc_human)表请输入命令: 1"
    print u"同步部门(tc_unit)表请输入命令: 2"
    print u"同步岗位(tc_role)表请输入命令: 3"
    print u"同步人员岗位(tc_human_role)表请输入命令: 4"
    print u"同步参与者(tc_part)表请输入命令: 5"
    print u"同步区域(tc_region)表请输入命令: 6"
    print u"同步子系统(tc_sys_info)表请输入命令: 7"
    print u"同步问题类型(tc_dic_event_any_type)表请输入命令: 8"
    print u"同步问题来源(tc_dic_event_src)表请输入命令: 9"
    print u"同步案件类型(tc_dic_event_rec_type)表请输入命令: 10"
    print u"同步活动属性(tc_dic_act_property)表请输入命令: 11"
    print u"同步工作流流向定义(tc_wf_trans_def)表请输入命令: 12"
    print u"同步工作流阶段参与者(tc_wf_act_part)表请输入命令: 13"
    print u"同步工作流节点定义(tc_wf_act_def)表请输入命令: 14"
    print u"退出请输入命令:exit 或者 -1"

if __name__ == "__main__":
    # 启动任务
    biz_conn = get_bizdb_conn()
    stat_conn = get_statdb_conn()

    # print u"帮助:"
    # print u"如果需要同步全部，请输入命令: 0"
    # print u"同步人员(tc_human)表请输入命令: 1"
    # print u"同步部门(tc_unit)表请输入命令: 2"
    # print u"同步岗位(tc_role)表请输入命令: 3"
    # print u"同步人员岗位(tc_human_role)表请输入命令: 4"
    # print u"同步参与者(tc_part)表请输入命令: 5"
    # print u"同步区域(tc_region)表请输入命令: 6"
    # print u"同步子系统(tc_sys_info)表请输入命令: 7"
    # print u"同步问题类型(tc_dic_event_any_type)表请输入命令: 8"
    # print u"同步问题来源(tc_dic_event_src)表请输入命令: 9"
    # print u"同步案件类型(tc_dic_event_rec_type)表请输入命令: 10"
    # print u"同步活动属性(tc_dic_act_property)表请输入命令: 11"
    # print u"同步工作流流向定义(tc_wf_trans_def)表请输入命令: 12"
    # print u"同步工作流阶段参与者(tc_wf_act_part)表请输入命令: 13"
    # print u"同步工作流节点定义(tc_wf_act_def)表请输入命令: 14"
    # print u"退出请输入命令:exit 或者 -1"
    print_help_info()
    print u"请输入命令:"
    while (True):
        commandName = raw_input()
        if commandName == "exit" or commandName == "-1":
            exit()
        else:
            need_syn_tables = get_need_syn_table(commandName)
            for table in need_syn_tables:
                transferOnlyDataBiz2Stat(biz_conn, stat_conn, table)
        print u"请输入命令:"