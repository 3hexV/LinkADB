import subprocess
import sys
import time

from PyQt5.QtWebEngine import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

import LinkADBDetailsWin
import LinkADBFileBrowserWin
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ADBCommand import ADBCommand
import LibLoadingMask
from GlobalCfg import *
from linkadb_res_rc import *
from tool.data_visualization_script.batterySimpleChart import BatteryDetailsAnalysis


class CmdDeviceGetInfo(QThread):
    _thread_finish = pyqtSignal(bool)
    _get_screen_flag = pyqtSignal(bool)
    _update_screen_flag = pyqtSignal(bool)
    _basic_info = pyqtSignal(list)
    _cmd_help_info = pyqtSignal(list)
    _battery_data_info = pyqtSignal(list)
    _battery_read_load_info = pyqtSignal(bool)
    _mem_and_storage_info = pyqtSignal(list)
    _screen_argument_info = pyqtSignal(list)
    _space_name_info = pyqtSignal(list)

    def __init__(self, parent=None, cmd_type='', cmd_str=''):
        super(CmdDeviceGetInfo, self).__init__(parent)
        self.cmd_str = cmd_str
        self.cmd_type = cmd_type

    def run(self):
        if self.cmd_type == 'get_screen':
            self.getDeviceScreen(self.cmd_str)
        elif self.cmd_type == 'update_screen':
            self.updateDeviceScreen(self.cmd_str)
        elif self.cmd_type == 'get_screen_info':
            self.getScreenInfo(self.cmd_str)
        elif self.cmd_type == 'get_basic_info':
            self.getBasicInfo(self.cmd_str)
        elif self.cmd_type == 'cmd_help':
            self.cmdHelpInfo(self.cmd_str)
        elif self.cmd_type == 'get_battery_data':
            self.getBatteryInfo(self.cmd_str)
        elif self.cmd_type == 'get_mem_and_storage_info':
            self.getMemAndStorageInfo(self.cmd_str)
        self._thread_finish.emit(True)

    def getScreenInfo(self, ip_or_id):
        res = []
        print(ip_or_id)
        # 分辨率
        cmd_str = adbCom.getShellCommandStr(ip_or_id, 'wm size')
        stdout, stderr = self.runPowershell(cmd_str)

        res.append(stdout.split(':')[1].split('x'))

        # dpi
        cmd_str = adbCom.getShellCommandStr(ip_or_id, 'wm density')
        stdout, stderr = self.runPowershell(cmd_str)
        res.append(stdout)

        print(res)
        self._screen_argument_info.emit(res)
    def getMemAndStorageInfo(self, ip_or_id):
        res = []

        # mem info
        cmd_str = adbCom.getShellCommandStr(ip_or_id, 'free')
        stdout, stderr = self.runPowershell(cmd_str)
        res.append(stdout)

        # mem details
        cmd_str = adbCom.getShellCommandStr(ip_or_id, 'cat /proc/meminfo')
        stdout, stderr = self.runPowershell(cmd_str)
        res.append(stdout)

        # storage info
        cmd_str = adbCom.getShellCommandStr(ip_or_id, 'df -ah')
        stdout, stderr = self.runPowershell(cmd_str)
        res.append(stdout)

        self._mem_and_storage_info.emit(res)

    def getBatteryInfo(self, para):
        res = []
        ip_or_id, script_path, data_path, battery_html_tmp_path, battery_html_res_path = para.split(',')
        print(para)

        # 1.get battery basic info
        cmd_str = adbCom.getShellCommandStr(ip_or_id, 'dumpsys battery')
        stdout, stderr = self.runPowershell(cmd_str)
        # analysis battery basic info
        battery_basic_info = {}
        for info in stdout.split('\n'):
            if 'Current Battery Service state' in info:
                continue
            elif len(info.strip()) != 0:
                key, val = info.split(':')
                battery_basic_info[key.strip()] = val.strip()
        res.append(battery_basic_info)

        # 2.get battery details
        cmd_str = adbCom.getShellCommandStr(ip_or_id, 'dumpsys batterystats --enable full-wake-history')
        stdout, stderr = self.runPowershell(cmd_str)

        cmd_str = adbCom.getShellCommandStr(ip_or_id, 'dumpsys batterystats --history > {}'.format(data_path))
        stdout, stderr = self.runPowershell(cmd_str)

        print('')
        # analysis battery details
        bbi = BatteryDetailsAnalysis(data_path=data_path,
                                     data_encoding='utf-16',
                                     tmp_path=battery_html_tmp_path,
                                     res_path=battery_html_res_path,
                                     tmp_res_encoding='utf-8')
        while not bbi.run():
            pass
        self._battery_data_info.emit(res)

    def cmdHelpInfo(self, cmd_str):
        stdout, stderr = self.runPowershell(cmd_str)
        self._cmd_help_info.emit([stdout, stderr])

    def getBasicInfo(self, id_or_ip):
        res = []
        # getprop
        cmd_str = adbCom.getShellCommandStr(id_or_ip, 'getprop ro.product.brand')
        stdout, stderr = self.runPowershell(cmd_str)
        res.append(stdout.strip())

        cmd_str = adbCom.getShellCommandStr(id_or_ip, 'getprop ro.product.manufacturer')
        stdout, stderr = self.runPowershell(cmd_str)
        res.append(stdout.strip())

        cmd_str = adbCom.getShellCommandStr(id_or_ip, 'getprop ro.product.name')
        stdout, stderr = self.runPowershell(cmd_str)
        res.append(stdout.strip())

        cmd_str = adbCom.getShellCommandStr(id_or_ip, 'getprop ro.product.marketname')
        stdout, stderr = self.runPowershell(cmd_str)
        res.append(stdout.strip())

        # dumpsys battery
        cmd_str = adbCom.getShellCommandStr(id_or_ip, 'dumpsys battery | findstr level')
        stdout, stderr = self.runPowershell(cmd_str)
        res.append(int(stdout.split(':')[1]))

        cmd_str = adbCom.getShellCommandStr(id_or_ip, 'dumpsys battery | findstr status')
        stdout, stderr = self.runPowershell(cmd_str)
        res.append(int(stdout.split(':')[1]))

        # ls /bin
        cmd_str = adbCom.getShellCommandStr(id_or_ip, 'ls /bin/ -1')
        stdout, stderr = self.runPowershell(cmd_str)
        res.append(stdout.strip())

        self._basic_info.emit(res)

    def getDeviceScreen(self, cmd_str):
        stdout, stderr = self.runPowershell(cmd_str)
        self._get_screen_flag.emit(True)

    def updateDeviceScreen(self, cmd_str):
        stdout, stderr = self.runPowershell(cmd_str)
        self._update_screen_flag.emit(True)

    def runPowershell(self, cmd_str):
        process = subprocess.Popen(['powershell.exe', '-Command', cmd_str], shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode(shell_code['powershell']), stderr.decode(shell_code['powershell'])


class LinkADBDetailsControl(QMainWindow, LinkADBDetailsWin.Ui_MainWindow):

    def __init__(self, parent=None, id=''):
        super(LinkADBDetailsControl, self).__init__(parent)
        self.setupUi(self)
        self.id = id

        self.loading_mask = LibLoadingMask.LoadingMask(self, './res/loading.gif')
        adbCom.setAdbPath(pathCfg['adb_exe_path'])

        self.setWindowTitle('LinkADB 详情 ({})'.format(self.id))
        self.setFixedSize(self.width(), self.height())

        self.le_screen.setStyleSheet("border: 2px solid red")
        self.le_screen.setScaledContents(True)

        self.table_battery.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_mem.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_mem_details.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_disk.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.btn_update_screen.clicked.connect(self.updateScreen)
        self.lw_command_list.doubleClicked.connect(self.getCmdHelp)
        self.le_cmd_search.textChanged.connect(self.cmdSearchRespond)
        self.tb_details.currentChanged.connect(self.updateTabInfo)

        self.getBasicInfo()

    def updateTabInfo(self, index):
        if index == 0:
            self.getBasicInfo()
        elif index == 1:
            self.getMemAndStorageInfo()
        elif index == 2:
            pass
        elif index == 3:
            pass
        elif index == 4:
            self.getBatteryInfo()
        elif index == 5:
            self.getScreenInfo()
        elif index == 6:
            pass
        elif index == 7:
            pass
        elif index == 8:
            pass
        elif index == 9:
            pass
        elif index == 10:
            pass
        elif index == 11:
            self.getNameSpaceInfo()

    def getNameSpaceInfo(self):
        device_info_thread = CmdDeviceGetInfo(self, 'get_space_name_info', self.id)
        device_info_thread._thread_finish.connect(self.deviceCmdThreadHandle)
        device_info_thread._space_name_info.connect(self.updateSpaceNameInfoHandle)

        device_info_thread.start()

    def updateSpaceNameInfoHandle(self, info):
        pass

    def getScreenInfo(self):
        self.loading_mask.show()
        self.getScreenArgument()

        self.updateScreen()

    def getScreenArgument(self):
        device_info_thread = CmdDeviceGetInfo(self, 'get_screen_info', self.id)
        device_info_thread._thread_finish.connect(self.deviceCmdThreadHandle)
        device_info_thread._screen_argument_info.connect(self.updateScreenInfoHandle)

        device_info_thread.start()

    def updateScreenInfoHandle(self, info):
        print(info)

    def getMemAndStorageInfo(self):
        self.loading_mask.show()
        device_info_thread = CmdDeviceGetInfo(self, 'get_mem_and_storage_info', self.id)
        device_info_thread._thread_finish.connect(self.deviceCmdThreadHandle)
        device_info_thread._mem_and_storage_info.connect(self.updateMemAndStorageInfoHandle)

        device_info_thread.start()


    def updateMemAndStorageInfoHandle(self, info):
        mem_info = info[0]
        mem_details = info[1]
        storage_info = info[2]

        self.updateMemInfo(mem_info)
        self.updateMemDetails(mem_details)
        self.updateStorage(storage_info)

    def updateStorage(self, storage_info):
        yData = []
        xDataUsed = []
        xDataAvail = []

        self.table_disk.setRowCount(0)
        self.table_disk.clearContents()

        for i, info in enumerate(storage_info.split('\n')):
            if len(info.strip()) == 0 or i == 0:
                continue

            kv = list(filter(None, info.split(' ')))
            row_count = self.table_disk.rowCount()  # 返回当前行数(尾部)
            self.table_disk.insertRow(row_count)  # 尾部插入一行

            for index, val in enumerate(kv):
                self.table_disk.setItem(row_count, index, QTableWidgetItem(val.strip()))
                # 只加入含有% 并且是一级目录的
                if '%' in val and len(kv[5].split('/')) == 2:
                    yData.append("'{}'".format(kv[5].strip()))
                    xDataUsed.append(val.replace('%', ''))
                    xDataAvail.append(str(100 - int(val.replace('%', ''))))

        print(yData, len(yData))
        print(xDataUsed, len(xDataUsed))
        print(xDataAvail, len(xDataAvail))

        with open(pathCfg['storage_tmp_path'], 'r', encoding='utf-8') as f:
            raw_html_str = f.read()
            html_str = raw_html_str.replace('@yData@', ','.join(yData)).\
                replace('@xDataUsed@', ','.join(xDataUsed)).\
                replace('@xDataAvail@', ','.join(xDataAvail))

            with open(pathCfg['storage_res_path'], 'w', encoding='utf-8') as f:
                f.write(html_str)
        self.web_browser_storage.load(QUrl(QFileInfo(pathCfg['storage_res_path']).absoluteFilePath()))

    def updateMemDetails(self, mem_details):

        self.table_mem_details.setRowCount(0)
        self.table_mem_details.clearContents()

        for details in mem_details.split('\n'):
            if len(details.strip()) == 0:
                continue
            row_count = self.table_mem_details.rowCount()  # 返回当前行数(尾部)
            self.table_mem_details.insertRow(row_count)  # 尾部插入一行

            key, val = details.split(':')
            item1 = QTableWidgetItem(key.strip())
            self.table_mem_details.setItem(row_count, 0, item1)
            item2 = QTableWidgetItem(val.strip())
            self.table_mem_details.setItem(row_count, 1, item2)

    def updateMemInfo(self, mem_info):
        # mem info
        self.table_mem.setRowCount(0)
        self.table_mem.clearContents()
        cache_parser = False
        mem_data = ["{value: @@, name: 'used'}",
                    "{value: @@, name: 'free'}",
                    "{value: @@, name: 'buffers'}"]

        # update mem table
        for info in mem_info.split('\r\n'):
            if 'total' in info or len(info.strip()) == 0:
                continue

            if 'buffers/cache' in info:
                cache_parser = True

            kv = list(filter(None, info.split(' ')))
            row_count = self.table_mem.rowCount()  # 返回当前行数(尾部)
            self.table_mem.insertRow(row_count)  # 尾部插入一行

            for index, val in enumerate(kv):
                if cache_parser:
                    if index == 0:
                        self.table_mem.setItem(row_count, index,
                                               QTableWidgetItem(val.strip() + kv[index + 1].strip()))
                    elif index == 1:
                        continue
                    elif index == 2:
                        item = QTableWidgetItem(self.byte2AdaptUnit(val.strip()))
                        item.setToolTip(val.strip() + ' B')
                        self.table_mem.setItem(row_count, index, item)
                    elif index == 3:
                        item = QTableWidgetItem(self.byte2AdaptUnit(val.strip()))
                        item.setToolTip(val.strip() + ' B')
                        self.table_mem.setItem(row_count, index, item)
                        cache_parser = False
                        mem_data[1] = mem_data[1].replace('@@', val)
                else:
                    item = QTableWidgetItem(self.byte2AdaptUnit(val.strip()))
                    if index != 0:
                        item.setToolTip(val.strip() + 'B')
                    self.table_mem.setItem(row_count, index, item)
                    if 'Mem' in info:
                        if index == 2:
                            mem_data[0] = mem_data[0].replace('@@', val)
                        elif index == 5:
                            mem_data[2] = mem_data[2].replace('@@', val)

        with open(pathCfg['mem_tmp_path'], 'r', encoding='utf-8') as f:
            raw_html_str = f.read()
            html_str = raw_html_str.replace('@Data@', ','.join(mem_data))

            with open(pathCfg['mem_res_path'], 'w', encoding='utf-8') as f:
                f.write(html_str)
        self.web_browser_mem.load(QUrl(QFileInfo(pathCfg['mem_res_path']).absoluteFilePath()))

    def byte2AdaptUnit(self, n):
        unit = [' B', ' KB', ' MB', ' GB']
        if not str.isdigit(n):
            return n
        n = int(n)
        count = 0
        while True:
            tmp = n/1024
            if int(tmp) == 0:
                break
            n = tmp
            count = count + 1

        return '{:.2f}{}'.format(n, unit[count])

    def getBatteryInfo(self):
        self.loading_mask.show()

        device_info_thread = CmdDeviceGetInfo(self, 'get_battery_data', '{},{},{},{},{}'.format(
                                                                    self.id,
                                                                    pathCfg['battery_script_path'],
                                                                    pathCfg['battery_data_path'],
                                                                    pathCfg['battery_html_tmp_path'],
                                                                    pathCfg['battery_html_res_path']))
        device_info_thread._thread_finish.connect(self.deviceCmdThreadHandle)
        device_info_thread._battery_data_info.connect(self.updateBatteryInfoHandle)

        device_info_thread.start()

    def updateBatteryInfoHandle(self, info):
        battery_badic_info = dict(info[0])

        self.table_battery.setRowCount(0)
        self.table_battery.clearContents()

        for key, val in battery_badic_info.items():
            if key == 'level':
                self.le_b_level.setText(val)
            elif key == 'status':
                self.cb_b_state.setCurrentIndex(int(val) - 2)
            row_count = self.table_battery.rowCount()
            self.table_battery.insertRow(row_count)
            self.table_battery.setItem(row_count, 0, QTableWidgetItem(key))
            self.table_battery.setItem(row_count, 1, QTableWidgetItem(val))

        self.web_browser.load(QUrl(QFileInfo(pathCfg['battery_html_res_path']).absoluteFilePath()))

    def cmdSearchRespond(self, text):
        # 如果没有输入任何内容，则显示所有项
        if not text:
            for i in range(self.lw_command_list.count()):
                item = self.lw_command_list.item(i)
                item.setHidden(False)
        # 否则只显示文本中包含所输入文本的项
        else:
            for i in range(self.lw_command_list.count()):
                item = self.lw_command_list.item(i)
                if text in item.text():
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def getCmdHelp(self):
        self.loading_mask.show()
        cmd = self.lw_command_list.currentItem().text()

        cmd_str = adbCom.getShellCommandStr(self.id, '{} --help'.format(cmd))
        device_info_thread = CmdDeviceGetInfo(self, 'cmd_help', cmd_str)
        device_info_thread._thread_finish.connect(self.deviceCmdThreadHandle)
        device_info_thread._cmd_help_info.connect(self.helpInfoHandle)

        device_info_thread.start()

    def helpInfoHandle(self, info):
        self.tb_cmd_help.setText('\n'.join(info).strip())

    def getBasicInfo(self):
        self.loading_mask.show()

        device_info_thread = CmdDeviceGetInfo(self, 'get_basic_info', self.id)
        device_info_thread._thread_finish.connect(self.deviceCmdThreadHandle)
        device_info_thread._basic_info.connect(self.updateBasicInfoHandle)
        device_info_thread.start()

    def updateBasicInfoHandle(self, info):
        self.le_brand.setText(info[0])
        self.le_manufacturer.setText(info[1])
        self.le_name.setText(info[2])
        self.le_marketname.setText(info[3])

        self.pb_battery.setValue(info[4])
        self.cb_b_state_only_show.setCurrentIndex(info[5]-2)

        cmd_list = info[6].split('\r\n')
        self.le_cmd_count.setText('识别到{}条'.format(len(cmd_list)))

        for cmd in cmd_list:
            QListWidgetItem(cmd, self.lw_command_list)

        # self.updateScreen()

    def updateScreen(self):
        self.loading_mask.show()

        cmd_str = adbCom.getShellCommandStr(self.id, 'screencap -p /sdcard/_link_adb_screen.png')
        device_info_thread = CmdDeviceGetInfo(self, 'get_screen', cmd_str)
        device_info_thread._thread_finish.connect(self.deviceCmdThreadHandle)
        device_info_thread._get_screen_flag.connect(self.deviceGetScreen)

        device_info_thread.start()

    def deviceCmdThreadHandle(self, finish):
        if finish:
            self.loading_mask.hide()

    def deviceGetScreen(self, get):
        if not get:
            return
        self.loading_mask.show()

        cmd_str = adbCom.getADBCommandStr(self.id, 'pull /sdcard/_link_adb_screen.png ./data/screen.png')
        device_info_thread = CmdDeviceGetInfo(self, 'update_screen', cmd_str)
        device_info_thread._thread_finish.connect(self.deviceCmdThreadHandle)
        device_info_thread._update_screen_flag.connect(self.deviceUpdateScreenHandle)

        device_info_thread.start()

    def deviceUpdateScreenHandle(self, update):
        if not update:
            return
        self.le_screen.setPixmap(QPixmap('./data/screen.png'))


def main():
    app = QApplication(sys.argv)
    win = LinkADBDetailsControl(id='e9264402')
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()