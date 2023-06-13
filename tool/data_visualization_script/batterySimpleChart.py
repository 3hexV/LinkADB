import datetime
import re
import time


class BatteryDetailsAnalysis:

    def __init__(self, data_path='', data_encoding='utf-16', tmp_path='', res_path='', tmp_res_encoding='utf-8'):
        self.data_path = data_path
        self.data_encoding = data_encoding
        self.tmp_path = tmp_path
        self.res_path = res_path
        self.tmp_res_encoding = tmp_res_encoding

    def run(self):
        return self.analysis(self.data_path, self.data_encoding, self.tmp_path, self.res_path, self.tmp_res_encoding)

    def analysis(self, data_path, data_encoding, tmp_path, res_path, tmp_res_encoding):
        show_y_data = 50

        reset_time = ''
        batter_data = []
        line = ' '
        with open(data_path, 'r', encoding=data_encoding) as f:
            while line != '':
                line = f.readline().strip()
                if 'RESET:TIME' in line:
                    reset_time = re.findall(r'RESET:TIME:\s(.*?)$', line)[0]

                    local_time = datetime.datetime.strptime(reset_time, '%Y-%m-%d-%H-%M-%S')
                    # 将本地时间转换为 UTC 时间
                    utc_time = local_time.astimezone(datetime.timezone.utc)
                    # 将 UTC 时间转换为时间戳（自 1970 年 1 月 1 日 0 点开始的秒数）
                    timestamp = int(utc_time.timestamp())
                    # print(timestamp)
                else:
                    battery_level = re.findall(r'\)\s(\d+)', line)
                    time = re.findall(r'(.*?)\s\(', line)

                if len(battery_level) != 0 and len(time) != 0:
                    utc_time = datetime.datetime.utcfromtimestamp(timestamp + self.time_str_to_sec(time[0]))
                    time_str = utc_time.strftime("%Y-%m-%d %H:%M:%S")
                    batter_data.append(["'{}'".format(utc_time), battery_level[0]])

        # print(reset_time)
        data_len = len(batter_data)
        # print(data_len)
        y_step = int(data_len / show_y_data)

        xData = []
        yData = []
        Data = []
        for index, data in enumerate(batter_data):
            if index == 0 or index % y_step == 0 or index == data_len - 1:
                yData.append(data[1])
                xData.append("{}".format(data[0]))
                Data.append('["{}", {}]'.format(data[0].replace("'", ''), int(data[1])))

        xDataStr = ','.join(xData)
        yDataStr = ','.join(yData)

        # print(','.join(Data))

        with open(tmp_path, 'r', encoding=tmp_res_encoding) as f1:
            html_str = f1.read()
            html_str = html_str.replace('@xDataStr@', xDataStr).replace('@yDataStr@', yDataStr).replace('@yData1@',
                                                                                                        ','.join(Data))

            with open(res_path, 'w', encoding=tmp_res_encoding) as f2:
                f2.write(html_str)
        return True

    def time_str_to_sec(self, time_str, ms=False):
        hours = 0
        minutes = 0
        seconds = 0
        milliseconds = 0

        if time_str == '0':
            return 0

        if 'ms' in time_str:
            parts = re.findall(r'(\d+)ms', time_str)[0]
            milliseconds = int(parts)
            time_str = time_str.replace('{}ms'.format(parts), '')

        if 's' in time_str:
            parts = re.findall(r'(\d+)s', time_str)[0]
            seconds = int(parts)
            time_str = time_str.replace('{}s'.format(parts), '')

        if 'm' in time_str:
            parts = re.findall(r'(\d+)m', time_str)[0]
            minutes = int(parts)
            time_str = time_str.replace('{}m'.format(parts), '')

        if 'h' in time_str:
            parts = re.findall(r'(\d+)h', time_str)[0]
            hours = int(parts)
            time_str = time_str.replace('{}h'.format(parts), '')

        if not ms:
            total_seconds = (hours * 3600) + (minutes * 60) + seconds
            return total_seconds
        else:
            total_milliseconds = (hours * 3600 * 1000) + (minutes * 60 * 1000) + seconds * 1000 + milliseconds
            return total_milliseconds


# def main():
#     bbi = BatteryDetailsAnalysis(data_path=r'E:\wk-self\LinkADB\data\data2.txt',
#                                  data_encoding='utf-16',
#                                  tmp_path=r'E:\wk-self\LinkADB\tool\data_visualization_script\batterySCTmp.html',
#                                  res_path=r'E:\wk-self\LinkADB\tool\data_visualization_script\batterySC.html',
#                                  tmp_res_encoding='utf-8')
#
# if __name__ == '__main__':
#     main()
