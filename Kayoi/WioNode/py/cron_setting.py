# cronの設定を実際に書き込む

import pandas as pd
from SetCrontab import SetCrontab
from get_filepath import get_filepath
from recieve_username_auth import recieve_username_auth

command_list = [
    f"sh {get_filepath('../sh/90_91_test_WioNode_data_period.sh')} >> $HOME/Desktop/Kayoi_GUI/Kayoi/WioNode/cron_stderr.log 2>&1",
    f"sh {get_filepath('../sh/92_test_LINE_Notify_alert.sh')} >> $HOME/Desktop/Kayoi_GUI/Kayoi/WioNode/cron_stderr.log 2>&1",
    f"sh {get_filepath('../sh/93_test_LINE_Notify_period.sh')} >> $HOME/Desktop/Kayoi_GUI/Kayoi/WioNode/cron_stderr.log 2>&1",
    f"sh {get_filepath('../sh/94_test_daily_report.sh')} >> $HOME/Desktop/Kayoi_GUI/Kayoi/WioNode/cron_stderr.log 2>&1",
    f"sh {get_filepath('../sh/95_test_WioNode_data_period_gzip.sh')} >> $HOME/Desktop/Kayoi_GUI/Kayoi/WioNode/cron_stderr.log 2>&1",
]

job_start_minute_list = [0,1,2,3,4]

file = "../resource/cron_setting.csv"
filepath = get_filepath(file)
try:
    df = pd.read_csv(filepath, encoding="shift-jis", header=0, index_col=0)
except FileNotFoundError:
    message = "cronの設定をまとめたファイルが存在しません"
    file = "../stderr.log"
    filepath = get_filepath(file)
    with open(filepath, mode = "a") as f:
        f.write(message + "\n")

is_recieve_username = recieve_username_auth()

for i, ind in enumerate(df.index):
    if (i <= 1) | (is_recieve_username):
        command = command_list[i]
        print(command)
        if df.loc[ind, "run_flag"] == False:
            # 削除のみ実行
            c = SetCrontab()
            c.delete_job(command)
        else:
            # cronを設定する。
            job_start_minute = job_start_minute_list[i]
            job_cycle_minute = df.loc[ind, "run_span"]
            job_cycle_hour = job_cycle_minute // 60
            job_cycle_minute = job_cycle_minute % 60
            
            if job_cycle_minute == 0:
                job_cycle_minute_com = f"{job_start_minute}"
            else:
                job_cycle_minute_com =  f"{job_start_minute}-59/{job_cycle_minute}"
            
            if job_cycle_hour >= 2:
                job_cycle_hour_com = f"*/{job_cycle_hour}"
            else:
                job_cycle_hour_com = "*"
            schedule = f"{job_cycle_minute_com} {job_cycle_hour_com} * * *"
            
            c = SetCrontab()
            c.write_job(command=command, schedule=schedule)
            # print(schedule, command)

# daily_report の設定をする
if is_recieve_username:
    file = "../resource/daily_report_run_flag.txt"
    daily_report_run_flag_filepath = get_filepath(file)
    try:
        with open(daily_report_run_flag_filepath, encoding="shift-jis", mode = "r") as f:
            daily_report_run_flag = True if f.read() == "True" else False
    # 初期設定としてはTrue
    except FileNotFoundError:
        daily_report_run_flag = True

    if daily_report_run_flag:
        command = command_list[i + 1]
        schedule = "3 0 * * *"
        c = SetCrontab()
        c.write_job(command=command, schedule=schedule)

# gzipの設定をする
command = command_list[-1]
schedule = "4 1 * * 1"
c = SetCrontab()
c.write_job(command=command, schedule=schedule)

