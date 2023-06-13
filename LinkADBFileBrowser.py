import os
import re
import subprocess
import sys
import pyperclip

import LinkADBFileBrowserWin
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ADBCommand import ADBCommand
import LibLoadingMask
from GlobalCfg import *
from LinkADBFileBrowserDetailsControl import LinkADBFileBrowserDetailsControl
from linkadb_file_browser_rc import *


class CmdDeviceFileRefresher(QThread):
    _thread_finish = pyqtSignal(bool)
    _file_info = pyqtSignal(list)
    _root_flag = pyqtSignal(bool)
    _push_info = pyqtSignal(list)
    _pull_info = pyqtSignal(list)
    _mkdir_info = pyqtSignal(list)
    _touch_info = pyqtSignal(list)
    _rm_info = pyqtSignal(list)
    _cp_info = pyqtSignal(list)
    _mv_info = pyqtSignal(list)
    _get_more_info = pyqtSignal(list)
    _details_info = pyqtSignal(str)

    def __init__(self, parent=None, cmd_type='', cmd_str='', path=''):
        super(CmdDeviceFileRefresher, self).__init__(parent)
        self.cmd_str = cmd_str
        self.cmd_type = cmd_type
        self.path = path

    def run(self):
        if self.cmd_type == 'ls':
            self.lsPath(self.cmd_str)
        elif self.cmd_type == 'pull':
            self.pull(self.cmd_str)
        elif self.cmd_type == 'push':
            self.push(self.cmd_str)
        elif self.cmd_type == 'mkdir':
            self.mkdir(self.cmd_str)
        elif self.cmd_type == 'touch':
            self.touch(self.cmd_str)
        elif self.cmd_type == 'rm':
            self.rm(self.cmd_str)
        elif self.cmd_type == 'cp':
            self.cp(self.cmd_str)
        elif self.cmd_type == 'mv':
            self.mv(self.cmd_str)
        elif self.cmd_type == 'get_more_info':
            self.getMoreInfo(self.cmd_str, self.path)
        self._thread_finish.emit(True)

    def getMoreInfo(self, id_or_ip, path):
        res = ''
        # 文件信息
        cmd_str = adbCom.getShellCommandStr(id_or_ip, 'stat -c "%n,%F,%N,%s,%b,%f,%a,%A,%u,%U,%g,%G,%m,%i,'
                                            '%h,%D,%d,%t,%T,%X,%Y,%Z,%x,%y,%z,%o,%B,%C" {}'.format(path))
        stdout, stderr = self.runPowershell(cmd_str)
        if not self.checkPermission(stderr):
            self._get_more_info.emit([False, stderr])
        else:
            res = stdout
            self._get_more_info.emit([True, cmd_str + ' is done'])
            # 文件系统信息
            cmd_str = adbCom.getShellCommandStr(id_or_ip, 'stat -f -c "%n,%l,%i,%t,%T,'
                                                          '%s,%S,%b,%f,%a,%c,%d" {}'.format(path))
            stdout, stderr = self.runPowershell(cmd_str)
            if not self.checkPermission(stderr):
                self._get_more_info.emit([False, stderr])
            else:
                res = res + '@G@' + stdout
                self._get_more_info.emit([True, cmd_str + ' is done'])

                # 文件类型信息
                cmd_str = adbCom.getShellCommandStr(id_or_ip, 'file -b {}'.format(path))
                stdout, stderr = self.runPowershell(cmd_str)
                if not self.checkPermission(stderr):
                    self._get_more_info.emit([False, stderr])
                else:
                    res = res + '@G@' + stdout.strip()
                    self._get_more_info.emit([True, cmd_str + ' is done'])

                    # 文件内容信息
                    cmd_str = adbCom.getShellCommandStr(id_or_ip, 'wc -lwcm {}'.format(path))
                    stdout, stderr = self.runPowershell(cmd_str)
                    if not self.checkPermission(stderr):
                        self._get_more_info.emit([False, stderr])
                    else:
                        res = res + '@G@' + stdout.strip()
                        self._get_more_info.emit([True, cmd_str + ' is done'])
                        self._details_info.emit(res)

    def mv(self, cmd_str):
        stdout, stderr = self.runPowershell(cmd_str)
        if not self.checkPermission(stderr):
            self._mv_info.emit([False, stderr])
        else:
            self._mv_info.emit([True, cmd_str + ' is done'])

    def cp(self, cmd_str):
        stdout, stderr = self.runPowershell(cmd_str)
        if not self.checkPermission(stderr):
            self._cp_info.emit([False, stderr])
        else:
            self._cp_info.emit([True, cmd_str + ' is done'])

    def rm(self, cmd_str):
        stdout, stderr = self.runPowershell(cmd_str)
        if not self.checkPermission(stderr):
            self._rm_info.emit([False, stderr])
        else:
            self._rm_info.emit([True, cmd_str + ' is done'])

    def touch(self, cmd_str):
        stdout, stderr = self.runPowershell(cmd_str)
        if not self.checkPermission(stderr):
            self._touch_info.emit([False, stderr])
        else:
            self._touch_info.emit([True, cmd_str + ' is done'])

    def mkdir(self, cmd_str):
        stdout, stderr = self.runPowershell(cmd_str)
        if not self.checkPermission(stderr):
            self._mkdir_info.emit([False, stderr])
        else:
            self._mkdir_info.emit([True, cmd_str + ' is done'])

    def push(self, cmd_str):
        stdout, stderr = self.runPowershell(cmd_str)
        if not self.checkPermission(stdout):
            self._push_info.emit([False, stdout])
        else:
            self._push_info.emit([True, stdout])

    def pull(self, cmd_str):
        stdout, stderr = self.runPowershell(cmd_str)
        if not self.checkPermission(stdout):
            self._pull_info.emit([False, stdout])
        else:
            self._pull_info.emit([True, stdout])
        print(stdout)

    def lsPath(self, cmd_str):
        stdout, stderr = self.runPowershell(cmd_str)
        if not self.checkPermission(stderr):
            self._file_info.emit([self.path, stderr, False])
        else:
            self._file_info.emit([self.path, stdout, True])
        return stdout

    def checkPermission(self, msg):
        if 'Permission denied' in msg:
            return False
        else:
            return True

    def runPowershell(self, cmd_str):
        process = subprocess.Popen(['powershell.exe', '-Command', cmd_str], shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode(shell_code['powershell']), stderr.decode(shell_code['powershell'])


class LinkADBFileBrowserControl(QMainWindow, LinkADBFileBrowserWin.Ui_MainWindow):
    id = ''
    root = None
    last_save_path = './data/'
    global_auto_log_id = 0

    def __init__(self, parent=None, id=''):
        super(LinkADBFileBrowserControl, self).__init__(parent)
        self.setupUi(self)
        self.id = id

        # self.tree_a.setDragEnabled(True)  # 启用拖拽
        # self.tree_a.setAcceptDrops(True)  # 接受拖放操作
        # self.tree_a.setDragDropMode(QTreeWidget.DragOnly)

        self.tree_a.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_a.customContextMenuRequested.connect(self.fileMenu)

        self.loading_mask = LibLoadingMask.LoadingMask(self, './res/loading.gif')
        adbCom.setAdbPath(pathCfg['adb_exe_path'])

        self.setWindowTitle('LinkADB FileBrowser ({})'.format(self.id))
        self.setFixedSize(self.width(), self.height())

        self.root = self.tree_a.invisibleRootItem()

        self.refreshDeviceFileTree('/')

        # 将双击事件绑定到 QTreeView 上
        self.tree_a.doubleClicked.connect(lambda: self.onDoubleClick(False))

    def fileMenu(self, pos):
        ft_right_menu = QMenu(self)

        # 新建
        new_menu = QMenu('新建')
        new_menu.setIcon(QIcon(QPixmap(':img/res/ft_new.png')))
        ft_right_menu.addMenu(new_menu)

        new_file_action = QAction('新建文件')
        new_file_action.setIcon(QIcon(QPixmap(':img/res/ft_file.png')))
        new_file_action.triggered.connect(self.createNewFile)
        new_menu.addAction(new_file_action)

        new_folder_action = QAction('新建文件夹')
        new_folder_action.setIcon(QIcon(QPixmap(':img/res/ft_folder.png')))
        new_folder_action.triggered.connect(self.createNewFolder)
        new_menu.addAction(new_folder_action)

        ft_right_menu.addMenu(new_menu)

        # 上传
        upload_action = QAction('上传')
        upload_action.setIcon(QIcon(QPixmap(':img/res/ft_upload.png')))
        upload_action.triggered.connect(self.upload)
        ft_right_menu.addAction(upload_action)

        # 下载
        download_action = QAction('下载')
        download_action.setIcon(QIcon(QPixmap(':img/res/ft_download.png')))
        download_action.triggered.connect(self.download)
        ft_right_menu.addAction(download_action)

        # 复制
        copy_menu = QMenu('复制')
        copy_menu.setIcon(QIcon(QPixmap(':img/res/ft_copy.png')))
        ft_right_menu.addMenu(copy_menu)

        copy_path_action = QAction('复制路径')
        copy_path_action.setIcon(QIcon(QPixmap(':img/res/ft_path.png')))
        copy_path_action.triggered.connect(self.copyPath)
        copy_menu.addAction(copy_path_action)

        copy2_action = QAction('复制到')
        copy2_action.setIcon(QIcon(QPixmap(':img/res/ft_copy2.png')))
        copy2_action.triggered.connect(self.copy2)
        copy_menu.addAction(copy2_action)

        cut2_action = QAction('剪切到')
        cut2_action.setIcon(QIcon(QPixmap(':img/res/ft_cut2.png')))
        cut2_action.triggered.connect(self.mv2)
        copy_menu.addAction(cut2_action)

        # 操作
        operate_menu = QMenu('操作')
        operate_menu.setIcon(QIcon(QPixmap(':img/res/ft_operate.png')))
        ft_right_menu.addMenu(operate_menu)

        edit_action = QAction('编辑文件')
        edit_action.setIcon(QIcon(QPixmap(':img/res/ft_edit.png')))
        # edit_action.triggered.connect(self.rmFileOrFolder)
        operate_menu.addAction(edit_action)

        details_action = QAction('详情')
        details_action.setIcon(QIcon(QPixmap(':img/res/ft_details.png')))
        details_action.triggered.connect(self.getMoreInfo)
        operate_menu.addAction(details_action)

        # 删除
        del_action = QAction('删除')
        del_action.setIcon(QIcon(QPixmap(':img/res/ft_del.png')))
        del_action.triggered.connect(self.rmFileOrFolder)
        ft_right_menu.addAction(del_action)

        ft_right_menu.exec_(
            QPoint(self.tree_a.mapToGlobal(pos).x() + 25,
                   self.tree_a.mapToGlobal(pos).y() + 20))

    def getMoreInfo(self):
        self.loading_mask.show()
        full_path = self.getSelectPath()
        self.deviceCmdThread('get_more_info', self.id, full_path)

    def mv2(self):
        full_path = self.getSelectPath()

        folder_name, okPressed = QInputDialog.getText(self, "剪切到", "输入剪切到文件夹路径：")

        if not okPressed and not folder_name != '':
            return

        cmd_str = adbCom.getShellCommandStr(self.id, 'mv -f {} {}'.format(full_path, folder_name))
        self.deviceCmdThread('mv', cmd_str, '')

    def copy2(self):
        full_path = self.getSelectPath()

        folder_name, okPressed = QInputDialog.getText(self, "复制到", "输入复制到文件夹路径：")

        if not okPressed and not folder_name != '':
            return

        cmd_str = adbCom.getShellCommandStr(self.id, 'cp -r {} {}'.format(full_path, folder_name))
        self.deviceCmdThread('cp', cmd_str, '')

    def copyPath(self):
        full_path = self.getSelectPath()
        pyperclip.copy(full_path)
        self.loading_mask.showToast(self, '已复制到剪切板', 500)

    def rmFileOrFolder(self):
        full_path = self.getSelectPath()
        if self.questionBox('删除文件', '即将删除:\n{}\n是否确认删除?'.format(full_path)):
            print('ok')
        else:
            print('no')
        cmd_str = adbCom.getShellCommandStr(self.id, 'rm -r {}'.format(full_path))
        self.deviceCmdThread('rm', cmd_str, '')

    def createNewFile(self):
        file_name, okPressed = QInputDialog.getText(self, "新建文件", "输入文件名：")

        if okPressed and file_name != '':
            res, info = self.isValidFolderName(file_name)
            if not res:
                self.warningBox('提示', info)
                return
        else:
            return

        full_path = self.getSelectPath()
        cmd_str = adbCom.getShellCommandStr(self.id, 'touch {}/{}'.format(full_path, file_name))
        self.deviceCmdThread('touch', cmd_str, '')

    def createNewFolder(self):
        folder_name, okPressed = QInputDialog.getText(self, "新建文件夹", "输入文件夹名：")

        if okPressed and folder_name != '':
            res, info = self.isValidFolderName(folder_name)
            if not res:
                self.warningBox('提示', info)
                return
        else:
            return

        full_path = self.getSelectPath()
        cmd_str = adbCom.getShellCommandStr(self.id, 'mkdir {}/{}'.format(full_path, folder_name))
        self.deviceCmdThread('mkdir', cmd_str, '')

    def isValidFolderName(self, name):
        # 判断长度是否合法
        if len(name) > 255:
            return [False, '名称超过255个字符']

        # 判断第一个字符是否合法
        if not re.match(r'[a-zA-Z_]', name[0]):
            return [False, '第一个字符不合法']

        # 判断其他字符是否合法
        pattern = r'^[a-zA-Z0-9_-]*$'
        if re.match(pattern, name) is None:
            return [False, '存在不合法字符']
        return [True, '']

    def upload(self):
        # 获得要上传的文件
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        local_file_names, _ = QFileDialog.getOpenFileNames(None, "选择上传的文件", "",
                                                           "All Files (*);;Text Files (*.txt)",
                                                           options=options)
        if local_file_names:
            pass
            # print('您选择的文件为：', file_names)
        else:
            # print('您取消了操作')
            return

        # adb push 报错
        full_path = self.getSelectPath()
        pyperclip.copy(full_path)
        folder_name, okPressed = QInputDialog.getText(self, "上传到",
                                                      "上传到文件夹路径(包含上传后的文件名)\n当前选择的文件夹路径已复制到剪切板：")

        if not okPressed and not folder_name != '':
            return

        self.loading_mask.show()

        cmd_str = adbCom.getADBCommandStr(self.id, 'push {} {}'.format(local_file_names[0], folder_name))
        print(cmd_str)
        self.deviceCmdThread('push', cmd_str, '')

    def download(self):
        # 获得保存位置
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        save_path = QFileDialog.getExistingDirectory(None, "选择文件夹", options=options)

        if save_path:
            # 用户选择了文件夹，则输出文件夹路径
            save_path = os.path.abspath(save_path)  # 获取文件夹的绝对路径
            # print('您选择的文件夹为：', save_path)
        else:
            # 用户点击了“取消”按钮
            # print('您取消了操作')
            return

        self.last_save_path = save_path

        self.loading_mask.show()

        full_path_list = self.getSelectPathList()
        for full_path in full_path_list:
            cmd_str = adbCom.getADBCommandStr(self.id, 'pull {} {}'.format(full_path, save_path))
            self.deviceCmdThread('pull', cmd_str, '')

    def getSelectPathList(self):
        selected_path_list = []
        selected_list = self.tree_a.selectedItems()
        for selected_item in selected_list:
            selected_path_list.append(self.getSelectPath(item=selected_item))
        return selected_path_list

    def getSelectName(self):
        return self.tree_a.currentItem().text(0)

    def getSelectPath(self, item=None):
        if item is None:
            tmp_item = self.tree_a.currentItem()
        else:
            tmp_item = item
        path = [tmp_item.text(0)]
        while tmp_item.parent():
            tmp_item = tmp_item.parent()
            path.insert(0, tmp_item.text(0))
        full_path = '/' + "/".join(path)
        return full_path

    # 双击事件处理函数
    def onDoubleClick(self, upper_level=False):
        full_path = self.getSelectPath()
        if upper_level:
            # 刷新上一层
            self.tree_a.setCurrentItem(self.tree_a.currentItem().parent())
            upper_path_list = full_path.split('/')
            upper_path_list.pop()
            upper_path = '/'.join(upper_path_list)
            print(upper_path)
            self.refreshDeviceFileTree(upper_path)
        else:
            self.refreshDeviceFileTree(full_path)

    def refreshDeviceFileTree(self, path):
        self.loading_mask.show()
        cmd_str = adbCom.getShellCommandStr(self.id, 'ls ' + path + '/ -1F')
        self.deviceCmdThread('ls', cmd_str, path)

    def deviceCmdThread(self, cmd_type, cmd_str, path):
        deviceFT_refresh_thread = CmdDeviceFileRefresher(self, cmd_type, cmd_str, path)
        deviceFT_refresh_thread._thread_finish.connect(self.deviceCmdThreadHandle)
        deviceFT_refresh_thread._file_info.connect(self.deviceFileTreeUpdate)
        if cmd_type == 'push':
            deviceFT_refresh_thread._push_info.connect(self.pushHandle)
        elif cmd_type == 'pull':
            deviceFT_refresh_thread._pull_info.connect(self.pullHandle)
        elif cmd_type == 'mkdir':
            deviceFT_refresh_thread._mkdir_info.connect(self.mkdirHandle)
        elif cmd_type == 'touch':
            deviceFT_refresh_thread._touch_info.connect(self.touchHandle)
        elif cmd_type == 'rm':
            deviceFT_refresh_thread._rm_info.connect(self.rmHandle)
        elif cmd_type == 'cp':
            deviceFT_refresh_thread._cp_info.connect(self.cpHandle)
        elif cmd_type == 'mv':
            deviceFT_refresh_thread._mv_info.connect(self.mvHandle)
        elif cmd_type == 'get_more_info':
            deviceFT_refresh_thread._get_more_info.connect(self.getMoreInfoHandle)
            deviceFT_refresh_thread._details_info.connect(self.showDetails)
        deviceFT_refresh_thread.start()

    def showDetails(self, res):
        info_list = res.split('@G@')

        lfd = LinkADBFileBrowserDetailsControl(self, info_list[0].split(','),
                                               info_list[1].split(','),
                                               info_list[2],
                                               info_list[3].split(' '))
        lfd.show()

    def getMoreInfoHandle(self, flag):
        if not flag[0]:
            self.warningBox('提示', flag[1])
        self.printMsg('get_more_info', flag[1])

    def mvHandle(self, flag):
        if not flag[0]:
            self.warningBox('提示', flag[1])
        self.printMsg('mv', flag[1])
        self.onDoubleClick(upper_level=True)

    def cpHandle(self, flag):
        if not flag[0]:
            self.warningBox('提示', flag[1])
        self.printMsg('cp', flag[1])
        self.onDoubleClick(upper_level=True)

    def rmHandle(self, flag):
        if not flag[0]:
            self.warningBox('提示', flag[1])
        self.printMsg('rm', flag[1])
        self.onDoubleClick(upper_level=True)

    def touchHandle(self, flag):
        if not flag[0]:
            self.warningBox('提示', flag[1])
        self.printMsg('touch', flag[1])
        self.onDoubleClick()

    def mkdirHandle(self, flag):
        if not flag[0]:
            self.warningBox('提示', flag[1])
        self.printMsg('mkdir', flag[1])
        self.onDoubleClick()

    def pullHandle(self, flag):
        if not flag[0]:
            self.warningBox('提示', flag[1])
        self.printMsg('download', flag[1])

    def pushHandle(self, flag):
        if not flag[0]:
            self.warningBox('提示', flag[1])
        self.printMsg('upload', flag[1])
        self.onDoubleClick()

    def printMsg(self, flag, msg):
        self.global_auto_log_id = self.global_auto_log_id + 1
        if flag == 'download':
            self.tb_info.setTextColor(QColor("green"))
            msg = '[download] ' + msg
        elif flag == 'upload':
            self.tb_info.setTextColor(QColor("blue"))
            msg = '[upload] ' + msg
        elif flag == 'mkdir':
            self.tb_info.setTextColor(QColor("darkBlue"))
            msg = '[mkdir] ' + msg
        elif flag == 'touch':
            self.tb_info.setTextColor(QColor("darkBlue"))
            msg = '[touch] ' + msg
        elif flag == 'ls':
            self.tb_info.setTextColor(QColor("black"))
            msg = '[ls] ' + msg
        elif flag == 'rm':
            self.tb_info.setTextColor(QColor("red"))
            msg = '[rm] ' + msg
        elif flag == 'cp':
            self.tb_info.setTextColor(QColor("darkGreen"))
            msg = '[cp] ' + msg
        elif flag == 'mv':
            self.tb_info.setTextColor(QColor("magenta"))
            msg = '[mv] ' + msg
        elif flag == 'get_more_info':
            self.tb_info.setTextColor(QColor("black"))
            msg = '[file info] ' + msg
        self.tb_info.append('- {:06} '.format(self.global_auto_log_id) + msg.strip())
        self.tb_info.setTextColor(QColor("black"))

    def deviceCmdThreadHandle(self, finish):
        if finish:
            self.loading_mask.hide()

    def warningBox(self, title, msg):
        messageBox = QMessageBox(QMessageBox.Warning, title, msg + "\t")
        messageBox.setWindowIcon(QIcon(QPixmap(':img/res/msg_warn.png')))
        icon = QIcon(QPixmap(':img/res/msg_info.png'))
        messageBox.setIconPixmap(icon.pixmap(32, 32))
        messageBox.addButton(self.tr("了解"), QMessageBox.YesRole)
        messageBox.exec_()

    def questionBox(self, title, msg):
        messageBox = QMessageBox(QMessageBox.Question, title, msg + "\t")
        messageBox.setWindowIcon(QIcon(QPixmap(':img/res/msg_warn.png')))
        icon = QIcon(QPixmap(':img/res/msg_info.png'))
        messageBox.setIconPixmap(icon.pixmap(32, 32))

        messageBox.addButton(self.tr("确定"), QMessageBox.YesRole)
        messageBox.addButton(self.tr("取消"), QMessageBox.NoRole)

        # 执行提示框，并获取用户按下的按钮
        result = messageBox.exec_()
        if result == 0:
            return True
        elif result == 1:
            return False

    def deviceFileTreeUpdate(self, file_tree_info):
        if not file_tree_info[2]:
            self.warningBox('提示', file_tree_info[1])
            return

        root_child_tree = str(file_tree_info[1]).split('\r\n')
        root_path = str(file_tree_info[0])
        # root_path_split = root_path.split('/')

        if root_path == root_child_tree[0] or root_path == root_child_tree[0][:-1] and root_child_tree[0][-1] in '@/*|':
            self.warningBox('提示', '这是个文件')
            return

        if root_path == '/':
            now_item = self.root
        else:
            now_item = self.tree_a.currentItem()

        for i in reversed(range(now_item.childCount())):
            child = now_item.child(i)
            now_item.removeChild(child)
            del child

        for item in root_child_tree:
            if len(item.strip()) != 0:
                node = QTreeWidgetItem(now_item)
                # /：斜杠表示是目录
                # @：At 符号表示是符号链接文件
                # *：星号表示是可执行文件
                # |：竖线符号表示是命名管道（FIFO）
                if item[-1] == '/':
                    node.setIcon(0, QIcon(QPixmap(':img/res/ft_folder.png')))
                    node.setText(0, item[:-1])
                elif item[-1] == '@':
                    node.setIcon(0, QIcon(QPixmap(':img/res/ft_link.png')))
                    node.setText(0, item[:-1])
                elif item[-1] == '*':
                    node.setIcon(0, QIcon(QPixmap(':img/res/ft_exe.png')))
                    node.setText(0, item[:-1])
                elif item[-1] == '|':
                    node.setIcon(0, QIcon(QPixmap(':img/res/ft_unknown.png')))
                    node.setText(0, item[:-1])
                else:
                    node.setIcon(0, QIcon(QPixmap(':img/res/ft_file.png')))
                    node.setText(0, item)
        now_item.setExpanded(True)
        self.printMsg('ls', root_path + ' is done')


def main():
    app = QApplication(sys.argv)
    win = LinkADBFileBrowserControl(id='e9264402')
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
