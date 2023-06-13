import configparser

# author: ChatGPT

class IniParser:
    def __init__(self, path, encode='utf-8'):
        self.path = path
        self.encode = encode
        self.config = configparser.ConfigParser()
        self.config.read(path, encoding=self.encode)

    # 返回所有节点
    def getSections(self):
        return self.config.sections()

    # 添加节点或修改已存在节点
    def setSection(self, section):
        if not self.config.has_section(section):
            self.config.add_section(section)
            self.saveIniFile()

    # 移除指定节点
    def removeSection(self, section):
        if self.config.has_section(section):
            self.config.remove_section(section)
            self.saveIniFile()

    # 返回指定节点中所有键值对
    def getOptions(self, section):
        if self.config.has_section(section):
            return self.config.items(section)
        else:
            return []

    # 获取指定节点下的指定键值对的字符串值（默认返回）
    def getString(self, section, option):
        if self.config.has_option(section, option):
            return self.config.get(section, option)
        else:
            return ""

    # 获取指定节点下的指定键值对的布尔值
    def getBoolean(self, section, option):
        if self.config.has_option(section, option):
            return self.config.getboolean(section, option)
        else:
            return False

    # 获取指定节点下的指定键值对的整型值
    def getInt(self, section, option):
        if self.config.has_option(section, option):
            return self.config.getint(section, option)
        else:
            return 0

    # 获取指定节点下的指定键值对的浮点型值
    def getFloat(self, section, option):
        if self.config.has_option(section, option):
            return self.config.getfloat(section, option)
        else:
            return 0.0

    # 设置指定节点下的指定键值对（如果节点不存在，将创建一个新节点）
    def setOption(self, section, option, value):
        self.setSection(section)
        self.config.set(section, option, str(value))
        self.saveIniFile()

    # 移除指定节点下的指定键值对
    def removeOption(self, section, option):
        if self.config.has_section(section) and self.config.has_option:
            self.config.remove_option(section, option)
            self.saveIniFile()

    def saveIniFile(self):
        with open(self.path, 'w', encoding=self.encode) as f:
            self.config.write(f)

# iniParser = IniParser(r'./config/LinkADB_cfg.ini', 'utf-8')
# print(iniParser.getSections())
# iniParser.setOption('1', '2', 4)
# print(iniParser.getSections())

