=======================================================
zwx 2016.04.22
支持oracle采集，需要根据数据库修改/constant/schemaConst.py。
与数据库交互语句均使用tools/utils中封装的方法。
cursor.execute(sql, args)语句执行时应注意
pymysql 绑定变量形式 %(name)s，位置变量 %s, %s...
e.g. 
cursor.execute("insert into to_stat_info(rec_id, task_num, create_time) values(%s, %s, %s)", (1000, "1000", datetime.now()))
cursor.execute("insert into to_stat_info(rec_id, task_num, create_time) values(%(rec_id)s, %(task_num)s, %(create_time)s)", {"task_num": "1000", "rec_id": 1000, "create_time": datetime.now()})
cx_Oracle 绑定变量形式 :name，位置变量 :1, :2...
cursor.execute("insert into to_stat_info(rec_id, task_num, create_time) values(:1, :2, :3)", (1000, "1000", datetime.now()))
cursor.execute("insert into to_stat_info(rec_id, task_num, create_time) values(:rec_id, :task_num, :create_time)", {"task_num": "1000", "rec_id": 1000, "create_time": datetime.now()})

========================================================
1. python版本为 2.7
2. python 库
oracle数据库需安装cx_Oracle
mysql数据库需安装pymysql

linux 安装pymysql插件步骤
1) 安装pip插件
yum install python-pip python-wheel
2) pip安装pymysql插件
pip install pymysql

3. 修改settings.py中的数据库连接配置，数据库名称
4. 启动start.bat/start.sh

5. 开发注意
主版本表在maintable文件夹下，采集在mainmodules下
项目定制放到protable、promodules下

6. 杭州项目在mainmodules/dispose下有针对专业部门的采集