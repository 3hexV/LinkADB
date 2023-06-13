from ADBCommand import ADBCommand

version = 'v1.1.2'
author = '3hex'
shell_code = {'cmd': 'gbk', 'powershell': 'utf-8'}
pathCfg = {
    'work_path': '',
    'adb_path': '',
    'tool_path': '',
    'adb_exe_path': r'E:\wk-self\LinkADB\tool\scrcpy\adb.exe',
    'tmp_path': r'E:\wk-self\LinkADB\tmp',
    'battery_data_path': r'E:\wk-self\LinkADB\data\battery_history_data.txt',
    'battery_script_path': r'E:\wk-self\LinkADB\tool\data_visualization_script\batterySimpleChart.py',
    'battery_html_tmp_path': r'E:\wk-self\LinkADB\tool\data_visualization_script\batterySCTmp.html',
    'battery_html_res_path': r'E:\wk-self\LinkADB\tool\data_visualization_script\batterySC.html',
    'mem_tmp_path': r'E:\wk-self\LinkADB\tool\data_visualization_script\memSCTmp.html',
    'mem_res_path': r'E:\wk-self\LinkADB\tool\data_visualization_script\memSC.html',
    'storage_tmp_path': r'E:\wk-self\LinkADB\tool\data_visualization_script\storageSCTmp.html',
    'storage_res_path': r'E:\wk-self\LinkADB\tool\data_visualization_script\storageSC.html',
}
adb_server_info = [False, 5037]

adbCom = ADBCommand('')
