# Cronの設定のハンドラー
# schedule関連はうまく動くか分からない

from crontab import CronTab
import getpass


class SetCrontab:
    def __init__(self):
        self.cron = CronTab(user = getpass.getuser())
        self.job = None

    # ファイルにジョブを書き込むメソッド
    def write_job(self, command, schedule):
        # 
        self.cron.remove_all(command = command)
        self.cron.write()

        self.job = self.cron.new(command=command)
        self.job.setall(schedule)
        self.cron.write()

    # jobを削除する。
    # 削除コマンドは単独で設置し、削除だけを実行できるようにする。
    def delete_job(self, command):
        self.cron.remove_all(command=command)
        self.cron.write()

    # 時分秒をcrontab用に整形する
    # 定時実行か間隔実行かの情報は時分ごとに持ってるので、それをどう処理して持ってくるか
    def shape_schedule(self, hour, minute, periodic = True):
        # hour minute に対してループ
        # 入力が0なら*とみなす
        if minute == 0:
            minute == "*"
        else:
            # 一応1時間を超えた際の対処を書いているが、これで正常に動くかどうかは不明
            min_to_hour = minute // 60
            hour += min_to_hour
            minute = minute % 60

        # 定時ならそのまま、間隔なら*/inputとする
        if periodic == True:
            if hour == 0:
                hour == "*"
            else:
                hour = f"*/{hour}"
            if minute == 0:
                minute == "*"
            else:
                minute = f"*/{minute}"

        schedule = f"{minute} {hour} * * *"

        return schedule


    def return_scheduled_span(self, command):

        iter = self.cron.find_command(command)
        l_iter = list(iter)

        if len(l_iter) == 0:
            pre_setting_message = "リストから選択してください"
            return pre_setting_message
        else:
            minute_command = l_iter[0].minute
            hour_command = l_iter[0].hour
            
            skipFlag = 0
            
            str_minute_command = str(minute_command)
            if str_minute_command == "*":
                # [TODO] minute=* no shori
                # do-si-yo!
                # ひとまず、今回のコードでは分が*である可能性は考えなくてよい
                per_minute = True
                minute = 1
                skipFlag = 1
                pass
                print("minute = *")
            else:
                try:
                    minute = int(str_minute_command)
                    minute = 0
                    per_minute = False
                except ValueError:
                    try:
                        minute = int(str_minute_command.split("/")[1])
                    except IndexError:
                        minute_list = list(map(int, str_minute_command.split(",")))
                        minute = minute_list[1]-minute_list[0]
                    per_minute = True
            
            str_hour_command = str(hour_command)
            if str_hour_command == "*":
                if per_minute == True:
                    pass
                else:
                    minute = 60
            else:
                try:
                    hour = int(str_hour_command)
                    per_hour = False
                    skipFlag = 1
                except ValueError:
                    minute += int(str_hour_command.split("/")[1]) * 60
                    per_hour = True
                    
            if skipFlag == 1:
                print("skipped")
                pass
            else:
                return minute

# # コマンドを指定
# command = 'python3 ~/Desktop/Kayoi_GUI-main/kayoi/py/data_period.py'
# # スケジュールを指定
# schedule = '0 10 * * *'


# # インスタンス作成
# c = CrontabSetting()
# # ファイルに書き込む
# c.write_job(command, schedule)



# c = SetCrontab()

# command = "~/Desktop/Kayoi_GUI/Kayoi/sh/period.sh"
# schedule = "*/10 * * * *"
# c.delete_job(command = command)

# c.write_job(command=command, schedule = schedule)