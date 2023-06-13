# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LinkADBMainWin.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1017, 598)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/img/res/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 1001, 541))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tree_adb_cmd = QtWidgets.QTreeWidget(self.horizontalLayoutWidget)
        self.tree_adb_cmd.setObjectName("tree_adb_cmd")
        item_0 = QtWidgets.QTreeWidgetItem(self.tree_adb_cmd)
        item_0 = QtWidgets.QTreeWidgetItem(self.tree_adb_cmd)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_0 = QtWidgets.QTreeWidgetItem(self.tree_adb_cmd)
        item_0 = QtWidgets.QTreeWidgetItem(self.tree_adb_cmd)
        item_0 = QtWidgets.QTreeWidgetItem(self.tree_adb_cmd)
        item_0 = QtWidgets.QTreeWidgetItem(self.tree_adb_cmd)
        item_0 = QtWidgets.QTreeWidgetItem(self.tree_adb_cmd)
        item_0 = QtWidgets.QTreeWidgetItem(self.tree_adb_cmd)
        item_0 = QtWidgets.QTreeWidgetItem(self.tree_adb_cmd)
        item_0 = QtWidgets.QTreeWidgetItem(self.tree_adb_cmd)
        self.horizontalLayout.addWidget(self.tree_adb_cmd)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lb_device_count = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.lb_device_count.setObjectName("lb_device_count")
        self.horizontalLayout_3.addWidget(self.lb_device_count)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.tbtn_adb_server_state = QtWidgets.QToolButton(self.horizontalLayoutWidget)
        self.tbtn_adb_server_state.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("res/adb_server_unactivated.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tbtn_adb_server_state.setIcon(icon1)
        self.tbtn_adb_server_state.setObjectName("tbtn_adb_server_state")
        self.horizontalLayout_3.addWidget(self.tbtn_adb_server_state)
        self.btn_adb_server_refresh = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/img/res/adb_server_refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_adb_server_refresh.setIcon(icon2)
        self.btn_adb_server_refresh.setObjectName("btn_adb_server_refresh")
        self.horizontalLayout_3.addWidget(self.btn_adb_server_refresh)
        self.label_3 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.le_adb_server_port = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.le_adb_server_port.setObjectName("le_adb_server_port")
        self.horizontalLayout_3.addWidget(self.le_adb_server_port)
        self.btn_adb_server_start = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/img/res/adb_server_start.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_adb_server_start.setIcon(icon3)
        self.btn_adb_server_start.setObjectName("btn_adb_server_start")
        self.horizontalLayout_3.addWidget(self.btn_adb_server_start)
        self.btn_asb_server_stop = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/img/res/adb_server_stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_asb_server_stop.setIcon(icon4)
        self.btn_asb_server_stop.setObjectName("btn_asb_server_stop")
        self.horizontalLayout_3.addWidget(self.btn_asb_server_stop)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.table_device_list = QtWidgets.QTableWidget(self.horizontalLayoutWidget)
        self.table_device_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectColumns)
        self.table_device_list.setObjectName("table_device_list")
        self.table_device_list.setColumnCount(3)
        self.table_device_list.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.table_device_list.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.table_device_list.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.table_device_list.setHorizontalHeaderItem(2, item)
        self.verticalLayout.addWidget(self.table_device_list)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.le_wifi_connect_ip = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.le_wifi_connect_ip.setObjectName("le_wifi_connect_ip")
        self.horizontalLayout_2.addWidget(self.le_wifi_connect_ip)
        self.le_wifi_connect_port = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.le_wifi_connect_port.setReadOnly(False)
        self.le_wifi_connect_port.setObjectName("le_wifi_connect_port")
        self.horizontalLayout_2.addWidget(self.le_wifi_connect_port)
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/img/res/adb_wifi_connect.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon5)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.tb_debug_log = QtWidgets.QTextBrowser(self.horizontalLayoutWidget)
        self.tb_debug_log.setObjectName("tb_debug_log")
        self.verticalLayout.addWidget(self.tb_debug_log)
        self.horizontalLayout.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1017, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tree_adb_cmd.headerItem().setText(0, _translate("MainWindow", "命令"))
        __sortingEnabled = self.tree_adb_cmd.isSortingEnabled()
        self.tree_adb_cmd.setSortingEnabled(False)
        self.tree_adb_cmd.topLevelItem(0).setText(0, _translate("MainWindow", "Networking"))
        self.tree_adb_cmd.topLevelItem(1).setText(0, _translate("MainWindow", "File Transfer"))
        self.tree_adb_cmd.topLevelItem(1).child(0).setText(0, _translate("MainWindow", "Push"))
        self.tree_adb_cmd.topLevelItem(1).child(1).setText(0, _translate("MainWindow", "Pop"))
        self.tree_adb_cmd.topLevelItem(1).child(2).setText(0, _translate("MainWindow", "Sync"))
        self.tree_adb_cmd.topLevelItem(2).setText(0, _translate("MainWindow", "Shell"))
        self.tree_adb_cmd.topLevelItem(3).setText(0, _translate("MainWindow", "App Installation"))
        self.tree_adb_cmd.topLevelItem(4).setText(0, _translate("MainWindow", "Debugging"))
        self.tree_adb_cmd.topLevelItem(5).setText(0, _translate("MainWindow", "Security"))
        self.tree_adb_cmd.topLevelItem(6).setText(0, _translate("MainWindow", "Scripting"))
        self.tree_adb_cmd.topLevelItem(7).setText(0, _translate("MainWindow", "Internal Debugging"))
        self.tree_adb_cmd.topLevelItem(8).setText(0, _translate("MainWindow", "USB"))
        self.tree_adb_cmd.topLevelItem(9).setText(0, _translate("MainWindow", "environment variables"))
        self.tree_adb_cmd.setSortingEnabled(__sortingEnabled)
        self.lb_device_count.setText(_translate("MainWindow", "统计: 0/0"))
        self.label_2.setText(_translate("MainWindow", "| ADB 状态"))
        self.btn_adb_server_refresh.setText(_translate("MainWindow", "刷新ADB状态"))
        self.label_3.setText(_translate("MainWindow", "| ADB 端口:"))
        self.le_adb_server_port.setText(_translate("MainWindow", "5037"))
        self.le_adb_server_port.setPlaceholderText(_translate("MainWindow", "5037"))
        self.btn_adb_server_start.setText(_translate("MainWindow", "启动ADB服务"))
        self.btn_asb_server_stop.setText(_translate("MainWindow", "停止ADB服务"))
        item = self.table_device_list.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "状态"))
        item = self.table_device_list.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "ID&IP"))
        item = self.table_device_list.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "更多信息"))
        self.label.setText(_translate("MainWindow", "设备IP和Port:"))
        self.le_wifi_connect_ip.setPlaceholderText(_translate("MainWindow", "192.168.1.1"))
        self.le_wifi_connect_port.setPlaceholderText(_translate("MainWindow", "5555"))
        self.pushButton.setText(_translate("MainWindow", "连接"))
import linkadb_res_rc
