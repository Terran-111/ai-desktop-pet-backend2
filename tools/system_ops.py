import psutil
import platform
import sys
from langchain_core.tools import tool

@tool
def get_system_status():
    """
    [系统透视协议] 获取当前系统的硬件状态HUD。
    当用户问“系统状态”、“电脑卡不卡”、“查看硬件”时调用。
    """
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    battery = psutil.sensors_battery()
    
    status = f"""
    [SYSTEM OVERWATCH]
    ------------------
    CPU LOAD    : {cpu_percent}%
    RAM USAGE   : {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)
    DISK USAGE  : {disk.percent}%
    """
    if battery:
        plugged = "AC_ONLINE" if battery.power_plugged else "BATTERY"
        status += f"POWER       : {battery.percent}% [{plugged}]"
    
    return status

@tool
def kill_process_by_name(process_name: str):
    """
    [进程管理] 根据名称终止进程。
    当用户说“杀掉 Chrome”、“关闭微信”时调用。
    Args:
        process_name: 进程名称关键词
    """
    killed = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                proc.kill()
                killed.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    if killed:
        return f"TARGET_ELIMINATED: 已终止 {len(killed)} 个进程 ({', '.join(killed[:3])}...)"
    return f"TARGET_NOT_FOUND: 未发现名为 '{process_name}' 的活跃进程。"

@tool
def check_python_env():
    """
    [环境自检] 检查当前 Python 环境信息。
    """
    ver = sys.version.split()[0]
    os_info = f"{platform.system()} {platform.release()}"
    return f"ENV_CHECK:\nPython: {ver}\nOS: {os_info}\nInterpreter: {sys.executable}"