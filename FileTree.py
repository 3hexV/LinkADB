import re

from GlobalCfg import *

from xml.etree import ElementTree as ET

class FileTree:
    et_parser = None
    format_write = True

    def __init__(self, id='', format_write=True):
        # 建立XML文件
        self.id = id
        self.ft_path = '{}/{}.xml'.format(pathCfg['tmp_path'], self.id)
        self.format_write = format_write

        tmp_root = ET.Element('Root', {'id': self.id})
        tree = ET.ElementTree(tmp_root)
        tree.write(self.ft_path, encoding='utf-8', short_empty_elements=False)

        self.et_parser = ET.parse(self.ft_path)
        self.root = self.et_parser.getroot()

    def printTreeXML(self, root_node=None):
        self.indent(self.root)
        print(ET.tostring(self.root).decode('utf-8'))

    def indent(self, elem, level=0):
        # 是否格式化写入
        if not self.format_write:
            return
        i = "\n" + level * "\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def writeNode(self, file_path, file_tree):

        file_path = self.prePathHandle(file_path)
        file_tree = self.prePathTreeHandle(file_tree)
        print(file_path, file_tree)

        xpath_list, xpath_real = self.path2XPathList(file_path)
        flag, exist_node, rest_path = self.isExist(xpath_list)
        if flag:
            print('exist')
            print(exist_node, rest_path)
        else:
            # 不存在路径就跟创建路径
            print('not exist')
            if exist_node is None:
                rest_path = file_path
                exist_node = self.root
            print(exist_node, rest_path)

            for child in rest_path[1:].split('/'):
                tmp_node = ET.SubElement(exist_node, child, {'id': self.id})
                exist_node = tmp_node

        print('real', xpath_real)
        now_node = self.findNodeByXpath(xpath_real)
        # 删除原来的
        self.delNodeByRoot(now_node)

        print('now_ndoe', now_node)
        # 更新
        for child in file_tree:
            tmp_node = ET.Element(child, {'id': self.id})
            print('add', tmp_node)
            now_node.append(tmp_node)
        for i in now_node:
            print(i)

        self.save2XMLFile()
        print('-'*50)

    # 路径预处理,防止出现数字开头的路径
    def prePathHandle(self, file_path):
        step_tmp = []
        for raw in file_path.split('/'):
            if raw == '':
                step_tmp.append(raw)
                continue
            raw = self.rawPathHandle(raw)
            step_tmp.append(raw)
        return '/'.join(step_tmp)

    def prePathTreeHandle(self, file_tree):
        tmp = []
        for node in file_tree:
            tmp.append(self.rawPathHandle(node))
        return tmp

    def rawPathHandle(self, raw):
        # 不能以数字开头
        res = re.findall(r'^[0123456789]+.*?$', raw)
        if len(res) != 0:
            raw = '_N-' + raw
        # 标签名不得包含特殊字符（如小于号 <、大于号 >、引号 ' 或 " 等）
        raw = raw.replace("'", '_SQ-').replace('"', '_DQ-').replace('>', '_GS-').replace('<', '_LS-')
        return raw

    def un_rawPathHandle(self, raw):
        if raw[0:3] == '_N-':
            raw = raw[3:-1]
        # 标签名不得包含特殊字符（如小于号 <、大于号 >、引号 ' 或 " 等）
        raw = raw.replace("_SQ-", "'").replace('_DQ-', '"').replace('_GS-', '>').replace('_LS-', '<')
        return raw

    def delNodeByRoot(self, node):
        for n in node:
            print('del', n.tag)
            # node.remove(n)

    def save2XMLFile(self):
        self.indent(self.root)
        tree = ET.ElementTree(self.root)
        tree.write(self.ft_path, encoding='utf-8', short_empty_elements=False)

    def findNodeByXpath(self, xpath):
        return self.root.find(xpath)

    def path2XPathList(self, file_path):
        tmp_list = []
        sum_path = './'
        file_path = '.' + file_path
        for step in file_path.split('/'):
            if step != '.':
                sum_path = sum_path + step
                tmp_list.append(sum_path)
                sum_path = sum_path + '/'
        return [tmp_list, tmp_list[len(tmp_list) - 1]]

    def isExist(self, xpath_list):
        last = None
        for index, xpath in enumerate(xpath_list):
            res = self.root.find(xpath)
            if res is None:
                return [False, last, xpath_list[len(xpath_list) - 1].replace(xpath_list[index - 1], '')]
            else:
                last = res
                continue
        return [True, '', '']


ft = FileTree(id='e9264402')
ft.writeNode('''/a/b/c/d''', ['9', '5', '8'])
ft.writeNode('''/a/b/c/d''', ['56', '5', '333'])
ft.writeNode('''/a/b/c/d/5''', ['12', '2222', '222222'])
