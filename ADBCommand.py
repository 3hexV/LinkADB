class ADBCommand:
    adb_shell_cmd_str = '@adb@ -s @id@ shell @cmd@'
    adb_cmd_str = '@adb@ -s @id@ @cmd@'

    def __init__(self, adb_path):
        self.adb_path = adb_path

    def setAdbPath(self, adb_path):
        self.adb_path = adb_path

    def getShellCommandStr(self,  ip_or_id, cmd_str=''):
        tmp = self.adb_shell_cmd_str.replace('@adb@', self.adb_path).replace('@id@', ip_or_id).replace('@cmd@', cmd_str)
        return tmp

    def getADBCommandStr(self,  ip_or_id, cmd_str=''):
        tmp = self.adb_cmd_str.replace('@adb@', self.adb_path).replace('@id@', ip_or_id).replace('@cmd@', cmd_str)
        return tmp



# adbCom = ADBCommand('adb.exe')
# cmd = adbCom.getShellCommandStr('12', 'ls')
# print(cmd)
#
# cmd = adbCom.getShellCommandStr('1ddddd', 'ls -l')
# print(cmd)
