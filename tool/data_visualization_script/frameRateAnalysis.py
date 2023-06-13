import sys
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtChart import (QChartView, QChart, QStackedBarSeries, QBarSet,
                           QLegend, QBarCategoryAxis, QValueAxis)


class DemoStackedBarSeries(QMainWindow):
    bar_text = 'FrameCompleted,IssueDrawCommandsStart,SyncStart,' \
               'SyncQueued,DrawStart,PerformTraversalsStart,' \
               'AnimationStart,HandleInputStart,Vsync'
    data_list = [[], [], [], [],
                 [], [], [], [], []]
    full_head_dict = {}
    failed_frame_index_list = []
    include_frame_index_list = []

    def __init__(self, parent=None):
        super(DemoStackedBarSeries, self).__init__(parent)

        # 设置窗口标题
        self.setWindowTitle('实战 Qt for Python: 堆积柱状图演示')
        # 设置窗口大小
        self.resize(1000, 500)

        self.createChart()

    def createChart(self):
        # 创建条状单元
        barSeries = QStackedBarSeries()
        header_index_list = []
        # 0: 未匹配到 1： 匹配到头部
        match_flag = 0
        frame_count = 0
        step = 5

        with open('../../data/frame_data.txt', 'r', encoding='utf-16') as f:
            while True:
                line = f.readline()
                if len(header_index_list) == 0 and match_flag == 0 and line.strip() == '---PROFILEDATA---':
                    match_flag = 1
                    # 读取列标题行
                    line = f.readline().strip()
                    for index, header in enumerate(line.split(',')):
                        self.full_head_dict[header.strip()] = index
                        print(index, header)
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
                        for index, data in enumerate(raw_data):
                            if frame_count != 0 and frame_count % step != 0:
                                break
                            self.include_frame_index_list.append(frame_count)
                            if raw_data[0] != '0':
                                print(index, data)
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
                                print(tmp_count, in_data)
                                self.data_list[tmp_count].append(in_data)
                                tmp_count = tmp_count + 1
                elif line == '':
                    break
                else:
                    continue

        print(self.failed_frame_index_list, frame_count, self.include_frame_index_list)
        print(self.data_list[0])

        chart = QChart()
        colors = [Qt.red, Qt.green, Qt.blue, Qt.black, Qt.white, Qt.gray, Qt.yellow, Qt.magenta, Qt.cyan]

        real_bar = self.bar_text.split(',')
        for index, bar_name in enumerate(real_bar):
            tmp_bar = QBarSet(bar_name)
            tmp_bar.append(self.data_list[index])
            barSeries.append(tmp_bar)

            legend = chart.legend()
            print(colors[index])
            legend.setLabelColor(colors[index])

        # 创建图表
        chart.addSeries(barSeries)
        chart.setTitle('简单堆积柱状图示例')
        chart.setAnimationOptions(QChart.SeriesAnimations)  # 设置成动画显示

        # 设置横向坐标(X轴)
        categories = []
        for index in self.include_frame_index_list:
            if index not in self.failed_frame_index_list:
                categories.append(str(index))

        axisX = QBarCategoryAxis()
        axisX.append(categories)
        chart.addAxis(axisX, Qt.AlignBottom)
        barSeries.attachAxis(axisX)

        # 设置纵向坐标(Y轴)
        axisY = QValueAxis()
        axisY.setRange(0, 60)
        axisY.setTickCount(4)
        chart.addAxis(axisY, Qt.AlignLeft)
        barSeries.attachAxis(axisY)

        # 图例属性
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)

        # 图表视图
        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)

        self.setCentralWidget(chartView)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DemoStackedBarSeries()
    window.show()
    sys.exit(app.exec())