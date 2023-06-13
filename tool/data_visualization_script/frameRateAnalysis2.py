import sys
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtChart import (QChartView, QChart, QStackedBarSeries, QBarSet,
                           QLegend, QBarCategoryAxis, QValueAxis)


class FrameRageAnalysis():
    bar_text = 'FrameCompleted,IssueDrawCommandsStart,SyncStart,' \
               'SyncQueued,DrawStart,PerformTraversalsStart,' \
               'AnimationStart,HandleInputStart,Vsync'
    data_list = [[], [], [], [],
                 [], [], [], [], []]
    full_head_dict = {}
    failed_frame_index_list = []
    include_frame_index_list = []

    def __init__(self, data_path, data_encoding, tmp_path, res_path, tmp_res_encoding ):
        self.data_path = data_path
        self.data_encoding = data_encoding
        self.tmp_path = tmp_path
        self.res_path = res_path
        self.tmp_res_encoding = tmp_res_encoding

        self.createChart()

    def createChart(self):
        # 创建条状单元
        barSeries = QStackedBarSeries()
        header_index_list = []
        # 0: 未匹配到 1： 匹配到头部
        match_flag = 0
        frame_count = 0
        step = 5

        with open(self.data_path, 'r', encoding=self.data_encoding) as f:
            while True:
                line = f.readline()
                if len(header_index_list) == 0 and match_flag == 0 and line.strip() == '---PROFILEDATA---':
                    match_flag = 1
                    # 读取列标题行
                    line = f.readline().strip()
                    for index, header in enumerate(line.split(',')):
                        self.full_head_dict[header.strip()] = index
                        if len(header) != 0 and header in self.bar_text:
                            header_index_list.append(index)
                    print(header_index_list)
                # 装载数据
                elif match_flag == 1:
                    # print(line)
                    if line.strip() == '---PROFILEDATA---':
                        match_flag = 0
                    else:
                        frame_count = frame_count + 1
                        tmp_count = 0
                        raw_data = line.split(',')

                        if frame_count != 0 and frame_count % step != 0:
                            continue
                        self.include_frame_index_list.append(frame_count)

                        for index, data in enumerate(raw_data):
                            if raw_data[0] != '0':
                                print('>16ms')
                                self.failed_frame_index_list.append(frame_count)
                                break
                            if index in header_index_list:
                                # FrameCompleted
                                if tmp_count == 0:
                                    in_data = int(raw_data[self.full_head_dict['FrameCompleted']]) - \
                                              int(raw_data[self.full_head_dict['IntendedVsync']])
                                # IssueDrawCommandsStart
                                elif tmp_count == 1:
                                    in_data = int(raw_data[self.full_head_dict['FrameCompleted']]) - \
                                              int(raw_data[self.full_head_dict['IssueDrawCommandsStart']])
                                # SyncStart （约 > 0.4 毫秒）
                                elif tmp_count == 2:
                                    in_data = int(raw_data[self.full_head_dict['IssueDrawCommandsStart']]) - \
                                              int(raw_data[self.full_head_dict['SyncStart']])
                                # SyncQueued （约 > 0.1 毫秒）
                                elif tmp_count == 3:
                                    in_data = int(raw_data[self.full_head_dict['SyncStart']]) - \
                                              int(raw_data[self.full_head_dict['SyncQueued']])
                                # DrawStart
                                elif tmp_count == 4:
                                    in_data = int(raw_data[self.full_head_dict['SyncStart']]) - \
                                              int(raw_data[self.full_head_dict['DrawStart']])
                                # PerformTraversalsStart
                                elif tmp_count == 6:
                                    in_data = int(raw_data[self.full_head_dict['DrawStart']]) - \
                                              int(raw_data[self.full_head_dict['PerformTraversalsStart']])
                                # AnimationStart 高：（> 2 毫秒）
                                elif tmp_count == 7:
                                    in_data = int(raw_data[self.full_head_dict['PerformTraversalsStart']]) - \
                                              int(raw_data[self.full_head_dict['AnimationStart']])
                                # HandleInputStart 高：（> 2 毫秒）
                                elif tmp_count == 8:
                                    in_data = int(raw_data[self.full_head_dict['AnimationStart']]) - \
                                              int(raw_data[self.full_head_dict['HandleInputStart']])
                                # Vsync
                                elif tmp_count == 9:
                                    in_data = int(raw_data[self.full_head_dict['IntendedVsync']]) - \
                                              int(raw_data[self.full_head_dict['Vsync']])
                                in_data = round(float(in_data/1000/1000), 3)
                                self.data_list[tmp_count].append(in_data)
                                tmp_count = tmp_count + 1
                elif line == '':
                    break
                else:
                    continue

        print(self.failed_frame_index_list, frame_count, self.include_frame_index_list)
        print(self.full_head_dict)

        xDataStr = ''
        for index in self.include_frame_index_list:
            xDataStr = xDataStr + "'{}',".format(index)

        with open(self.tmp_path, 'r', encoding=self.tmp_res_encoding) as f1:
            html_str = f1.read()
            html_str = html_str.replace('@xData@', xDataStr)

            for index, data in enumerate(self.data_list):
                yData = ''
                for d in data:
                    yData = yData + '{},'.format(str(d))
                html_str = html_str.replace('@yData{:d}@'.format(index+1), yData)

            with open(self.res_path, 'w', encoding=self.tmp_res_encoding) as f2:
                f2.write(html_str)


def main():
    fra = FrameRageAnalysis(data_path=r'E:\wk-self\LinkADB\data\frame_data.txt',
                                 data_encoding='utf-16',
                                 tmp_path=r'E:\wk-self\LinkADB\tool\data_visualization_script\frameSCTmp.html',
                                 res_path=r'E:\wk-self\LinkADB\tool\data_visualization_script\frameSC.html',
                                 tmp_res_encoding='utf-8')

if __name__ == '__main__':
    main()