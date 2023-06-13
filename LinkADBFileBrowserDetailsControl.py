

import LinkADBFileBrowserWin
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import LinkADBFileBrowserDetailsDialog

class LinkADBFileBrowserDetailsControl(QDialog, LinkADBFileBrowserDetailsDialog.Ui_Dialog):

    def __init__(self, parent=None, file_info=None, fs_info_list=None, file_type=None, file_content_info=None):
        super(LinkADBFileBrowserDetailsControl, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle('LinkADB FileBrowser Details')
        self.setFixedSize(self.width(), self.height())

        self.table_file.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_fs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_file_content.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.file_info = file_info
        self.fs_info_list = fs_info_list
        self.file_type = file_type
        self.file_content_info = file_content_info

        self.loadData()

    def loadData(self):
        for i, info in enumerate(self.file_info):
            item = QTableWidgetItem(self.file_info[i])
            self.table_file.setItem(i, 1, item)

        for i, info in enumerate(self.fs_info_list):
            item = QTableWidgetItem(self.fs_info_list[i])
            self.table_fs.setItem(i, 1, item)

        item = QTableWidgetItem(self.file_type)
        self.table_file_content.setItem(0, 1, item)

        for i, info in enumerate(self.file_content_info):
            item = QTableWidgetItem(self.file_content_info[i])
            self.table_file_content.setItem(i+1, 1, item)




