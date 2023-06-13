import datetime
import os
import re
import subprocess
import sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from LibIniParser import IniParser
import LinkADBMainWin
import LibLoadingMask
from LinkADBDetails import LinkADBDetailsControl
from LinkADBFileBrowser import LinkADBFileBrowserControl

from GlobalCfg import *

class CmdAdbServerTaskThread(QThread):
    # 线程执行完成否
    _res = pyqtSignal(bool)
    # 线程执行过程中产生的消息
    _msg = pyqtSignal(str)
    # adb服务查询结果
    _query_res = pyqtSignal(bool)
    adb_server_cmd = ''
    _adb_version_info = pyqtSignal(str)
    query_flag = False
    adb_normal_port = 5037

    # adb_server_cmd: query, start, stop
    def __init__(self, parent=None, adb_server_cmd='', start_port=0,
                 stop_port=0, query_port=0,
                 auto_start=False, query_version=False):
        super(CmdAdbServerTaskThread, self).__init__(parent)
        self.adb_server_cmd = adb_server_cmd
        self.start_port = start_port
        self.stop_port = stop_port
        self.query_port = query_port
        self.auto_start = auto_start
        self.query_version = query_version

    def run(self):
        if len(self.adb_server_cmd.strip()) == 0:
            self._res.emit(True)
            return

        if self.adb_server_cmd == 'query':
            self.queryAdbServerState(self.query_port, self.auto_start, self.query_version)
        elif self.adb_server_cmd == 'start':
            self.startAdbServer(self.start_port)
        elif self.adb_server_cmd == 'stop':
            self.stopAdbServer(self.stop_port)
        elif self.adb_server_cmd == 'version':
            self.queryAdbVersion()
        self._res.emit(True)

    def queryAdbVersion(self):
        cmd_str = "{} --version".format(pathCfg['adb_exe_path'])
        res_str = self.runPowershell(cmd_str)
        self._adb_version_info.emit(res_str)

    def queryAdbServerState(self, query_port, auto_start=False, query_version=True):
        # 根据 LinkADB 启动的adb的端口查找 adb.exe的PID
        cmd_str = "netstat -ano | findstr '127.0.0.1:{:d} '".format(query_port)
        res_str = self.runPowershell(cmd_str)

        # 查询对于端口返回为空 则表示该端口没有启用 也没有查询到adb服务
        if len(str(res_str).strip()) == 0:
            # 查询失败
            self._query_res.emit(False)
            self.query_flag = False
        else:
            # 有返回数据，解析出PID
            pid_str = re.findall(r'\s(\d\d*)\s', str(res_str))[0]

            if int(pid_str) == 0:
                # 查询失败
                self._query_res.emit(False)
                self.query_flag = False
            else:
                # 根据PID确定对于程序是否为adb.exe
                cmd_str = 'tasklist | findstr {}'.format(pid_str)
                res_str = self.runPowershell(cmd_str)
                exe_str = re.findall(r'adb.exe', res_str)
                if len(exe_str) != 0:
                    # 查询成功
                    if query_version:
                        self.queryAdbVersion()
                    self._query_res.emit(True)
                    self.query_flag = True
                else:
                    # 查询失败
                    self._query_res.emit(False)
                    self.query_flag = False

        if auto_start and not self.query_flag:
            self.startAdbServer(self.adb_normal_port)

    def startAdbServer(self, start_port):
        cmd_str = '{} -P {:d} start-server'.format(pathCfg['adb_exe_path'], start_port)
        self.runPowershell(cmd_str)
        self.queryAdbServerState(start_port)

    def stopAdbServer(self, stop_port):
        cmd_str = '{} -P {:d} kill-server'.format(pathCfg['adb_exe_path'], stop_port)
        res_str = self.runPowershell(cmd_str)
        self.queryAdbServerState(stop_port)

    def runPowershell(self, cmd_str):
        process = subprocess.Popen(['powershell.exe', '-Command', cmd_str], shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        log_time = datetime.datetime.now().strftime('%m-%d %H:%M:%S')

        stdout, stderr = process.communicate()
        tmp_msg = ''
        tmp_msg += '[{}]:@TC@{}@CR@'.format(log_time, cmd_str) + '-' * 80 + '\n'
        tmp_msg += "[Standard Output]:\n{}\n".format(stdout.decode(shell_code['powershell'])) + \
                   "[Standard Error]:\n{}\n".format(stderr.decode(shell_code['powershell'])) + '-' * 80 + '\n'
        self._msg.emit(tmp_msg)
        return stdout.decode(shell_code['powershell'])


class CmdTaskThread(QThread):
    # 线程执行完成否
    _res = pyqtSignal(bool)
    # 指令执行成功否
    # ...
    # 线程执行过程中产生的消息
    _msg = pyqtSignal(str)
    _devices_list = pyqtSignal(list)
    cmd_str = ''

    def __init__(self, parent=None, cmd_str='', ip_or_id=''):
        super(CmdTaskThread, self).__init__(parent)
        self.cmd_str = cmd_str
        self.ip_or_id = ip_or_id

    def run(self):
        if len(self.cmd_str.strip()) == 0:
            self._res.emit(True)
            return

        if self.cmd_str == 'refresh_devices':
            self.refreshDevices()
        elif self.cmd_str == 'disconnect_device':
            self.disconnectDevice(self.ip_or_id)
        elif self.cmd_str == 'connect_device':
            self.connectDevice(self.ip_or_id)
        elif self.cmd_str == 'open_shell_cmd':
            self.openShellUseCmd(self.ip_or_id)
        elif self.cmd_str == 'open_shell_powershell':
            self.openShellUsePowershell(self.ip_or_id)
        elif self.cmd_str == 'screen_to_scrcpy':
            self.screenToScrcpy(self.ip_or_id)
        self._res.emit(True)

    def connectDevice(self, ip_or_id):
        if len(str(ip_or_id).strip()) == 0:
            return
        cmd = '{} connect {}'.format(pathCfg['adb_exe_path'], ip_or_id)
        self.runPowershell(cmd)

    def screenToScrcpy(self, ip_or_id):
        if len(str(ip_or_id).strip()) == 0:
            return
        cmd = 'Start-Process -FilePath "{}" -ArgumentList "-s", "{}", "--window-title", "{}"'. \
            format(pathCfg['scrcpy_exe_path'], ip_or_id, ip_or_id)
        self.runPowershell(cmd)

    def openShellUseCmd(self, ip_or_id):
        if len(str(ip_or_id).strip()) == 0:
            return
        cmd = 'Start-Process -FilePath "cmd" -ArgumentList "/k", "{}"'. \
            format('{} -s {} shell'.format(pathCfg['adb_exe_path'], ip_or_id))
        self.runPowershell(cmd)

    def openShellUsePowershell(self, ip_or_id):
        if len(str(ip_or_id).strip()) == 0:
            return
        cmd = 'Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "{}"'. \
            format('{} -s {} shell'.format(pathCfg['adb_exe_path'], ip_or_id))
        self.runPowershell(cmd)

    def disconnectDevice(self, ip_or_id):
        if len(str(ip_or_id).strip()) == 0:
            return
        cmd = '{} disconnect {}'.format(pathCfg['adb_exe_path'], ip_or_id)
        self.runPowershell(cmd)

    def refreshDevices(self):
        cmd = '{} devices -l'.format(pathCfg['adb_exe_path'])
        res = self.runPowershell(cmd)
        devices_list = str(res).split('\n')
        self._devices_list.emit(devices_list)

    def runPowershell(self, cmd_str):
        process = subprocess.Popen(['powershell.exe', '-Command', cmd_str], shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        log_time = datetime.datetime.now().strftime('%m-%d %H:%M:%S')

        stdout, stderr = process.communicate()
        tmp_msg = ''
        tmp_msg += '[{}]:@TC@{}@CR@'.format(log_time, cmd_str) + '-' * 80 + '\n'
        tmp_msg += "[Standard Output]:\n{}\n".format(stdout.decode(shell_code['powershell'])) + \
                   "[Standard Error]:\n{}\n".format(stderr.decode(shell_code['powershell'])) + '-' * 80 + '\n'
        self._msg.emit(tmp_msg)
        return stdout.decode(shell_code['powershell'])

    # def runCmd(self, cmd_str):
    #     process = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE,
    #                                stderr=subprocess.PIPE)
    #     log_time = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
    #
    #     stdout, stderr = process.communicate()
    #     tmp_msg = ''
    #     tmp_msg += '[{}]:@TC@{}@CR@'.format(log_time, cmd_str) + '-' * 80 + '\n'
    #     tmp_msg += "[Standard Output]:\n{}\n".format(stdout.decode(shell_code['cmd'])) + \
    #                "[Standard Error]:\n{}\n".format(stderr.decode(shell_code['cmd'])) + '-' * 80 + '\n'
    #     self._msg.emit(tmp_msg)
    #     return stdout.decode(shell_code['cmd'])


class LinkADBMainGUI(QMainWindow, LinkADBMainWin.Ui_MainWindow):
    loading_mask = None
    iniParser = None

    # adb server
    now_adb_server_port = 5037
    adb_server_run = False

    # devices list
    devices_table = []
    devices_total = [0, 0]

    def __init__(self, parent=None):
        super(LinkADBMainGUI, self).__init__(parent)
        self.setupUi(self)

        self.iniParser = IniParser(r'./config/LinkADB_cfg.ini', 'utf-8')
        self.loadPathCfg()

        self.loading_mask = LibLoadingMask.LoadingMask(self, './res/loading.gif')

        # 设置窗口标题和不可修改大小
        self.setWindowTitle('LinkADB | {} | {}'.format(version, author))
        self.setFixedSize(self.width(), self.height())

        # 设置表格内表项自适应
        self.table_device_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # table设置右击菜单
        self.table_device_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_device_list.customContextMenuRequested.connect(self.deviceTableMenu)

        # text browser设置右击菜单
        self.tb_debug_log.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tb_debug_log.customContextMenuRequested.connect(self.tbDebugLogMenu)

        # 绑定点击事件
        self.btn_adb_server_start.clicked.connect(self.adbServerStart)
        self.btn_asb_server_stop.clicked.connect(self.adbServerStop)
        self.btn_adb_server_refresh.clicked.connect(self.adbServerRefresh)
        self.tbtn_adb_server_state.clicked.connect(self.getAdbVersion)

        # self.IPLabel = QLabel('ip:')
        # self.statusbar.addPermanentWidget(self.IPLabel, 0)


        # 启动前检查adb服务是否开启,auto_start表示检查出adb服务未启动，是否默认端口启动
        self.adbServerRefresh(auto_start=True)

    def refreshDevices(self):
        if not self.getAdbServerState():
            return
        self.runCmd('refresh_devices')

    # ！！！没有测试无线连接的断开
    def disconnectDevices(self):
        if not self.getAdbServerState():
            return
        if len(self.devices_table) < 1:
            self.messageWarn("提示", "没有设备连接")
            return

        selected_item = self.table_device_list.selectedItems()

        for index, item in enumerate(selected_item):
            row = item.row()
            print(index, row)
            # if index != 0 and index % 2 == 0:
            if self.devices_table[row][-1] == 'wifi':
                self.runCmd('disconnect_device', ip_or_id=self.devices_table[item.row()][0])
            elif self.devices_table[row][-1] == 'usb':
                self.messageWarn("提示",
                                 "设备[ID:{}]是有线连接设备，无法通过adb命令断开连接。\n请直接拔出USB即可断开连接！".
                                 format(self.devices_table[item.row()][0]))
        self.refreshDevices()

    def screenToScrcpy(self):
        if not self.getAdbServerState():
            return
        if len(self.devices_table) < 1:
            self.messageWarn("提示", "没有设备连接")
            return
        row = self.table_device_list.currentIndex().row()
        self.runCmd('screen_to_scrcpy', ip_or_id=self.devices_table[row][0])

    def openShellUseCmd(self):
        if not self.getAdbServerState():
            return
        row = self.table_device_list.currentIndex().row()
        self.runCmd('open_shell_cmd', ip_or_id=self.devices_table[row][0])

    def openShellUsePowershell(self):
        if not self.getAdbServerState():
            return
        row = self.table_device_list.currentIndex().row()
        self.runCmd('open_shell_powershell', ip_or_id=self.devices_table[row][0])

    def getAdbServerState(self):
        res = self.adb_server_run
        if not res:
            self.messageWarn("提示", "adb服务未开启，请先开启adb服务")
        return res

    def adbServerStart(self):
        print('start')
        self.loading_mask.show()
        start_port = int(self.le_adb_server_port.text())
        self.now_adb_server_port = start_port
        adb_server_info[1] = start_port

        adb_thread = CmdAdbServerTaskThread(self, adb_server_cmd='start', start_port=start_port)
        adb_thread._res.connect(self.adbTaskIsFinish)
        adb_thread._msg.connect(self.adbTaskResMsg)
        adb_thread._query_res.connect(self.adbTaskQueryRes)
        adb_thread._adb_version_info.connect(self.updateAdbVersion)
        adb_thread.start()

    def adbServerStop(self):
        self.loading_mask.show()
        stop_port = int(self.le_adb_server_port.text())
        adb_thread = CmdAdbServerTaskThread(self, adb_server_cmd='stop', stop_port=stop_port)
        adb_thread._res.connect(self.adbTaskIsFinish)
        adb_thread._msg.connect(self.adbTaskResMsg)
        adb_thread._query_res.connect(self.adbTaskQueryRes)
        adb_thread.start()

    def adbServerRefresh(self, auto_start=False, query_version=True):
        self.loading_mask.show()
        query_port = int(self.le_adb_server_port.text())
        adb_thread = CmdAdbServerTaskThread(self, adb_server_cmd='query', query_port=query_port, auto_start=auto_start,
                                            query_version=query_version)
        adb_thread._res.connect(self.adbTaskIsFinish)
        adb_thread._msg.connect(self.adbTaskResMsg)
        adb_thread._query_res.connect(self.adbTaskQueryRes)
        if query_version:
            adb_thread._adb_version_info.connect(self.updateAdbVersion)
        adb_thread.start()

    def getAdbVersion(self):
        self.loading_mask.show()
        adb_thread = CmdAdbServerTaskThread(self, adb_server_cmd='version')
        adb_thread._res.connect(self.adbTaskIsFinish)
        adb_thread._msg.connect(self.adbTaskResMsg)
        adb_thread._adb_version_info.connect(self.updateAdbVersion)
        adb_thread.start()

    def updateAdbVersion(self, version_info):
        self.tbtn_adb_server_state.setToolTip('\n'.join(version_info.split('\n')[:-1:]))

    def adbTaskQueryRes(self, query_flag):
        if query_flag:
            self.tbtn_adb_server_state.setIcon(QIcon(QPixmap(':img/res/adb_server_activated.png')))
            self.adb_server_run = True
            self.btn_adb_server_start.setEnabled(False)
            self.btn_asb_server_stop.setEnabled(True)
            self.tbtn_adb_server_state.setEnabled(True)
            self.le_adb_server_port.setReadOnly(True)
            adb_server_info[0] = True
            self.refreshDevices()
        else:
            self.tbtn_adb_server_state.setIcon(QIcon(QPixmap(':img/res/adb_server_unactivated.png')))
            self.adb_server_run = False
            self.btn_adb_server_start.setEnabled(True)
            self.btn_asb_server_stop.setEnabled(False)
            self.tbtn_adb_server_state.setEnabled(False)
            self.tbtn_adb_server_state.setToolTip('')
            self.le_adb_server_port.setReadOnly(False)
            adb_server_info[0] = False

    def adbTaskIsFinish(self, finish):
        if finish:
            self.loading_mask.hide()

    def adbTaskResMsg(self, msg):
        self.printLog(msg)

    # 载入路径配置
    def loadPathCfg(self):
        pathCfg['work_path'] = os.getcwd()
        pathCfg['adb_path'] = pathCfg['work_path'] + self.iniParser.getString('path_cfg', 'adb_path')
        pathCfg['tool_path'] = pathCfg['work_path'] + self.iniParser.getString('path_cfg', 'tool_path')
        pathCfg['adb_exe_path'] = pathCfg['adb_path'] + 'adb.exe'
        pathCfg['scrcpy_exe_path'] = pathCfg['tool_path'] + r'scrcpy\scrcpy.exe'
        adbCom.setAdbPath(pathCfg['adb_exe_path'])
        print(pathCfg)

    # refresh_devices,
    def runCmd(self, cmd_str='', ip_or_id=''):
        self.loading_mask.show()
        cmd_thread = CmdTaskThread(self, cmd_str, ip_or_id=ip_or_id)
        cmd_thread._res.connect(self.cmdTaskIsFinish)
        cmd_thread._msg.connect(self.cmdTaskResMsg)
        if cmd_str == 'refresh_devices':
            cmd_thread._devices_list.connect(self.updateDevicesList)
        cmd_thread.start()

    def messageWarn(self, title="", msg=""):
        messageBox = QMessageBox(QMessageBox.Warning, title, msg + "\t")
        messageBox.setWindowIcon(QIcon(QPixmap(':img/res/msg_warn.png')))
        icon = QIcon(QPixmap(':img/res/msg_info.png'))
        messageBox.setIconPixmap(icon.pixmap(32, 32))
        messageBox.addButton(self.tr("了解"), QMessageBox.YesRole)
        messageBox.exec_()

    def updateDevicesList(self, devices_list):
        self.devices_table.clear()

        self.devices_total = [0, 0]

        self.table_device_list.setRowCount(0)
        self.table_device_list.clearContents()
        devices_list = devices_list[1:-2:]

        self.devices_total[1] = len(devices_list)

        for item in devices_list:
            item.replace(':', ':\t')
            devices_info_list = list(filter(None, item.split(' ')))

            row_count = self.table_device_list.rowCount()  # 返回当前行数(尾部)
            self.table_device_list.insertRow(row_count)  # 尾部插入一行

            state_img = ':img/res/device_@1_@2.png'
            if self.isWired(devices_info_list[0]):
                state_img = state_img.replace('@1', 'usb')
                devices_info_list.append('usb')
            else:
                state_img = state_img.replace('@1', 'wifi')
                devices_info_list.append('wifi')

            if self.isOffline(devices_info_list[1]):
                pass
                state_img = state_img.replace('@2', 'disconnect')
            else:
                state_img = state_img.replace('@2', 'connect')
                self.devices_total[0] = self.devices_total[0] + 1

            itemIP = QTableWidgetItem(devices_info_list[0])

            itemState = QTableWidgetItem(devices_info_list[1])
            itemState.setIcon(QIcon(QPixmap(state_img)))

            itemDetails = QTableWidgetItem('  '.join(devices_info_list[2::]))

            self.table_device_list.setItem(row_count, 0, itemState)
            self.table_device_list.setItem(row_count, 1, itemIP)
            self.table_device_list.setItem(row_count, 2, itemDetails)
            itemDetails.setToolTip('\n'.join(devices_info_list[2::]))

            self.lb_device_count.setText('总计: {}/{}'.format(self.devices_total[0], self.devices_total[1]))
            self.lb_device_count.setToolTip(
                "Online:\t{}\nOffline:\t{}".format(self.devices_total[0], self.devices_total[1]))
            self.devices_table.append(devices_info_list)

    def isWired(self, id_str):
        if re.match("\d+\.\d+\.\d+\.\d+:\d+", id_str):
            return False
        else:
            return True

    def isOffline(self, state_str):
        if state_str == 'offline':
            return True
        else:
            return False

    def cmdTaskResMsg(self, msg):
        self.printLog(msg)

    def cmdTaskIsFinish(self, finish):
        if finish:
            self.loading_mask.hide()

    def printLog(self, log):
        log = str(log).split('@CR@')
        log2 = str(log[0]).split('@TC@')
        self.tb_debug_log.setTextColor(QColor("red"))
        self.tb_debug_log.append(log2[0])

        self.tb_debug_log.setTextColor(QColor("blue"))
        self.tb_debug_log.append(log2[1].lstrip())

        self.tb_debug_log.setTextColor(QColor("black"))
        self.tb_debug_log.append(log[1])

    def tbDebugLogMenu(self, pos):
        log_right_menu = QMenu(self)

        clear_log_action = QAction('清空日志')
        clear_log_action.setIcon(QIcon(QPixmap(':img/res/tb_log_clear_log.png')))
        clear_log_action.triggered.connect(self.logClear)
        log_right_menu.addAction(clear_log_action)

        export_log_action = QAction('导出日志')
        export_log_action.setIcon(QIcon(QPixmap(':img/res/tb_log_export_log.png')))
        export_log_action.triggered.connect(self.logClear)
        log_right_menu.addAction(export_log_action)

        log_right_menu.exec_(
            QPoint(self.tb_debug_log.mapToGlobal(pos).x() + 15,
                   self.tb_debug_log.mapToGlobal(pos).y() + 0))

    def logClear(self):
        self.tb_debug_log.clear()

    def deviceTableMenu(self, pos):
        dt_right_menu = QMenu(self)

        refresh_action = QAction('刷新列表')
        refresh_action.setIcon(QIcon(QPixmap(':img/res/td_rm_refresh.png')))
        refresh_action.triggered.connect(self.refreshDevices)
        dt_right_menu.addAction(refresh_action)

        connect_action = QAction('连接设备')
        connect_action.setIcon(QIcon(QPixmap(':img/res/td_rm_connect.png')))
        connect_action.triggered.connect(self.connectDevices)
        dt_right_menu.addAction(connect_action)

        screen_menu = QMenu('投屏到')
        screen_menu.setIcon(QIcon(QPixmap(':img/res/td_rm_screen.png')))
        dt_right_menu.addMenu(screen_menu)

        screen_to_scrcpy_action = QAction('Scrcpy')
        screen_to_scrcpy_action.setIcon(QIcon(QPixmap(':3img/tool/scrcpy/icon.png')))
        screen_to_scrcpy_action.triggered.connect(self.screenToScrcpy)
        screen_menu.addAction(screen_to_scrcpy_action)

        shell_menu = QMenu('Shell')
        shell_menu.setIcon(QIcon(QPixmap(':img/res/td_rm_shell.png')))
        dt_right_menu.addMenu(shell_menu)

        shell_cmd_action = QAction('打开一个Shell (cmd)')
        shell_cmd_action.setIcon(QIcon(QPixmap(':img/res/td_rm_shell_cmd.png')))
        shell_cmd_action.triggered.connect(self.openShellUseCmd)
        shell_menu.addAction(shell_cmd_action)

        shell_powershell_action = QAction('打开一个Shell (PowerShell)')
        shell_powershell_action.setIcon(QIcon(QPixmap(':img/res/td_rm_shell_powershell.png')))
        shell_powershell_action.triggered.connect(self.openShellUsePowershell)
        shell_menu.addAction(shell_powershell_action)

        file_browser_action = QAction('文件浏览器')
        file_browser_action.setIcon(QIcon(QPixmap(':img/res/td_rm_file_browser.png')))
        file_browser_action.triggered.connect(self.fileBrowserWin)
        dt_right_menu.addAction(file_browser_action)

        more_details_action = QAction('更多信息')
        more_details_action.setIcon(QIcon(QPixmap(':img/res/td_rm_more_details.png')))
        more_details_action.triggered.connect(self.moreDetailsOperate)
        dt_right_menu.addAction(more_details_action)

        remote_control_action = QAction('遥控器')
        remote_control_action.setIcon(QIcon(QPixmap(':img/res/td_rm_remote_control.png')))
        remote_control_action.triggered.connect(self.disconnectDevices)
        dt_right_menu.addAction(remote_control_action)

        disconnect_action = QAction('断开连接')
        disconnect_action.setIcon(QIcon(QPixmap(':img/res/td_rm_disconnect.png')))
        disconnect_action.triggered.connect(self.disconnectDevices)
        dt_right_menu.addAction(disconnect_action)

        dt_right_menu.exec_(
            QPoint(self.table_device_list.mapToGlobal(pos).x() + 25,
                   self.table_device_list.mapToGlobal(pos).y() + 20))

    def moreDetailsOperate(self):
        if not self.getAdbServerState():
            return
        if len(self.devices_table) < 1:
            self.messageWarn("提示", "没有设备连接")
            return

        details_win = LinkADBDetailsControl(self, id='e9264402')
        details_win.show()

    def fileBrowserWin(self):
        if not self.getAdbServerState():
            return
        if len(self.devices_table) < 1:
            self.messageWarn("提示", "没有设备连接")
            return

        file_browser_win = LinkADBFileBrowserControl(self, id='e9264402')
        file_browser_win.show()

    def connectDevices(self):
        if not self.getAdbServerState():
            return
        if len(self.devices_table) < 1:
            self.messageWarn("提示", "没有设备连接")
            return

        selected_item = self.table_device_list.selectedItems()

        for index, item in enumerate(selected_item):
            row = item.row()
            print('select', index, row)
            if self.devices_table[row][-1] == 'wifi':
                self.runCmd('connect_device', ip_or_id=self.devices_table[item.row()][0])
            elif self.devices_table[row][-1] == 'usb':
                self.messageWarn("提示",
                                 "设备[ID:{}]是有线连接设备，无法通过adb命令连接。\n请直接插入USB后刷新即可！".
                                 format(self.devices_table[item.row()][0]))
        self.refreshDevices()

# 关闭adb服务
def closeWin():
    if adb_server_info[0]:
        subprocess.Popen(['powershell.exe', '-Command',
                          '{} -P {:d} kill-server'.format(pathCfg['adb_exe_path'], adb_server_info[1])],
                         shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        print('[debug] adb server closed')


def main():
    app = QApplication(sys.argv)
    win = LinkADBMainGUI()
    app.aboutToQuit.connect(closeWin)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
