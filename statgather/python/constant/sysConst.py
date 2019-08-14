# coding:utf-8

archive_type_dict = {1: u"正常结案", 2: u"超时结案", 3: u"差错结案", 4: u"特殊结案"}
event_state_dict = {1: u"受理", 2: u"立案", 3: u"派遣", 4: "处置中"}
check_limit = 30  # 分钟数
verify_limit = 30  # 分钟数
cixi_check_limit = 120 # 慈溪市核查时限为120分钟
default_sys_time_id = 1 # 默认计时标准

special_dispose_actdef_ids = [320, 321]