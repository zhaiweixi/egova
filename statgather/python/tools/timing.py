#coding: utf-8
"""
    zwx 2016-05-27
    计时工具 参考java web程序的TimingManager
    @ get_minutes 获取两个时间点之间的分钟数
    @ get_hours 获取两个时间点之间的小时数
    @ get_minutes_str 获取两个时间点之间的分钟字符串
    @ get_hours_str  获取两个时间点之间的小时字符串
"""
import sys
sys.path.append("..")
from datetime import datetime, timedelta

def get_minutes(timing_dict, time_sys_id, begin_time, end_time):
    #获取两个时间点之间的工作分钟数
    calendar_list = timing_dict["calendar"]
    schedule_list = timing_dict["schedule"]
    if not begin_time or not end_time:
        return 0
    if begin_time > end_time:
        return 0
        
    minutes = 0

    default_am_start_date = datetime.strptime("2010-01-01 08:00:00", "%Y-%m-%d %H:%M:%S")
    default_am_end_date = datetime.strptime("2010-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")
    default_pm_start_date = datetime.strptime("2010-01-01 14:00:00", "%Y-%m-%d %H:%M:%S")
    default_pm_end_date = datetime.strptime("2010-01-01 18:00:00", "%Y-%m-%d %H:%M:%S")
    default_minutes_per_day = 480
    default_hours_perday = 8

    while begin_time < end_time:
        if not is_work_day(calendar_list, time_sys_id, end_time):
            # 非工作日则向前推一天，直到工作日开始计算
            end_time = get_pm_end_time(schedule_list, time_sys_id, end_time, -1)
            continue

        if not is_same_day(begin_time, end_time):
            # 不在同一天，则向前推一天，递归计算分钟数
            minutes += get_minutes(timing_dict, time_sys_id, get_am_start(schedule_list, time_sys_id, end_time, 0), end_time)
            end_time = get_pm_end_time(schedule_list, time_sys_id, end_time, -1)
            continue
        # 获取日历
        schedule = get_schedule(schedule_list, time_sys_id, end_time)
        if end_time.time() > schedule["pm_end_time"].time():
            # 如果结束时间在下班之后，则需要调整至下班时间
            end_time = get_pm_end_time(schedule_list, time_sys_id, end_time, 0)
        if begin_time.time() < schedule["am_start_time"].time():
            # 如果开始时间在上班时间之前，则需要调整至上班时间
            begin_time = get_am_start(schedule_list, time_sys_id, begin_time, 0)
        
        if begin_time > end_time:
            # 调整后如果没有时间差，则返回
            break
        if end_time.time() > schedule["pm_start_time"].time():
            # 结束时间下午上班之后
            if begin_time.time() > schedule["pm_start_time"].time():
                minutes += get_minutes_of_two_time(begin_time, end_time)
            else:
                minutes += get_minutes_of_two_time(schedule["pm_start_time"], end_time)
                if begin_time.time() < schedule["am_end_time"].time():
                    minutes += get_minutes_of_two_time(begin_time, schedule["am_end_time"])
        elif end_time.time() > schedule["am_end_time"].time():
            minutes += get_minutes_of_two_time(begin_time, schedule["am_end_time"])
        else:
            minutes += get_minutes_of_two_time(begin_time, end_time)
        break

    return minutes


def is_work_day(calendar_list, time_sys_id, date):
	# 判断是否是工作日
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    calendar = None
    for cal in calendar_list:
        if cal["time_sys_id"] == time_sys_id and cal["sys_year"] == int(year):
            calendar = cal
            break
        continue
    if calendar:
        if month == "01":
            bit = calendar["sys_january"]
        elif month == "02":
            bit = calendar["sys_february"]
        elif month == "03":
            bit = calendar["sys_march"]
        elif month == "04":
            bit = calendar["sys_april"]
        elif month == "05":
            bit = calendar["sys_may"]
        elif month == "06":
            bit = calendar["sys_june"]
        elif month == "07":
            bit = calendar["sys_july"]
        elif month == "08":
            bit = calendar["sys_august"]
        elif month == "09":
            bit = calendar["sys_september"]
        elif month == "10":
            bit = calendar["sys_october"]
        elif month == "11":
            bit = calendar["sys_november"]
        else:
            bit = calendar["sys_december"]

        if bit:
            return get_bit_value(bit, int(day)) == 1
        else:
            return True
    else:
        return True

def get_bit_value(bit, pos):
    return (bit >> (pos-1)) & 1

def get_pm_end_time(schedule_list, time_sys_id, date, days):
    real_date = date + timedelta(days = days)
    schedule = get_schedule(schedule_list, time_sys_id, real_date)
    date_str = real_date.strftime("%Y-%m-%d")
    time_str = schedule["pm_end_time"].strftime("%H:%M:%S")

    return datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M:%S")

def get_am_start(schedule_list, time_sys_id, date, days):
    real_date = date + timedelta(days = days)
    schedule = get_schedule(schedule_list, time_sys_id, real_date)
    date_str = real_date.strftime("%Y-%m-%d")
    time_str = schedule["am_start_time"].strftime("%H:%M:%S")

    return datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M:%S")

def is_same_day(begin_time, end_time):
    return begin_time.strftime("%Y-%m-%d") == end_time.strftime("%Y-%m-%d")

def get_schedule(schedule_list, time_sys_id, date):
    default_am_start_date = datetime.strptime("2010-01-01 08:00:00", "%Y-%m-%d %H:%M:%S")
    default_am_end_date = datetime.strptime("2010-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")
    default_pm_start_date = datetime.strptime("2010-01-01 14:00:00", "%Y-%m-%d %H:%M:%S")
    default_pm_end_date = datetime.strptime("2010-01-01 18:00:00", "%Y-%m-%d %H:%M:%S")
    default_minutes_per_day = 480
    default_hours_perday = 8
    schedule = schedule_list[0]
    for temp_schedule in schedule_list:
        if temp_schedule["time_sys_id"] == time_sys_id and temp_schedule["valid_from_date"] < date \
                and (not temp_schedule["valid_from_date"] or temp_schedule["valid_from_date"] + timedelta(days = 1) > date):
            schedule = temp_schedule
    if not schedule:
        schedule = {}
        schedule["am_start_time"] = default_am_start_date
        schedule["am_end_time"] = default_am_end_date
        schedule["pm_start_time"] = default_pm_start_date
        schedule["pm_end_time"] = default_pm_end_date
        schedule["minutes_per_day"] = default_minutes_per_day
        schedule["hours_per_day"] = default_hours_perday
    return schedule

def get_minutes_of_two_time(start, end):
    return round((end-start).seconds/60, 2)

def get_hours(timing_dict, time_sys_id, begin_time, end_time):
    return round(get_minutes(timing_dict, time_sys_id, begin_time, end_time)/60)

def get_minutes_str(timing_dict, time_sys_id, begin_time, end_time):
    return str(get_minutes(timing_dict, time_sys_id, begin_time, end_time)) + "分钟"

def get_hours_str(timing_dict, time_sys_id, begin_time, end_time):
    minutes = get_minutes(timing_dict, time_sys_id, begin_time, end_time)
    real_minutes = minutes % 60
    hours = (minutes - real_minutes)/60
    return str(hours) + "小时" + str(real_minutes) + "分钟"

# test
"""
if __name__ == "__main__":
    from utils import query_for_list, query_for_dict
    begin_date = datetime.now()
    conn = pymysql.connect(host="192.168.101.14", port=3306, db="hzcg", user="root", password="egova", charset="utf8")
    cur = conn.cursor()
    schedule_list = query_for_list(cur, "select * from tc_sys_schedule")
    calendar_list = query_for_list(cur, "select * from tc_sys_calendar")
    timing_dict = {"schedule": schedule_list, "calendar": calendar_list}
    begin_time = datetime.strptime("2016-03-11 09:00:00", "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime("2017-03-14 17:30:00", "%Y-%m-%d %H:%M:%S")
    minutes = get_minutes(timing_dict, 1, begin_time, end_time)
    hours_str = get_hours_str(timing_dict, 1, begin_time, end_time)
    print "耗时:", (datetime.now() - begin_date).seconds, "秒"
    print minutes
    print hours_str
"""