import requests
import socket
import subprocess
from langchain_core.tools import tool

@tool
def get_public_ip_info():
    """
    [IP溯源] 查询本机公网IP及地理位置信息。
    指令：“我是谁”、“查IP”。
    """
    try:
        res = requests.get("http://ip-api.com/json/", timeout=5).json()
        return f"""
        [NETWORK IDENTITY]
        IP: {res.get('query')}
        ISP: {res.get('isp')}
        LOC: {res.get('country')}, {res.get('city')}
        """
    except Exception as e:
        return f"TRACE_FAILED: 无法连接至追踪网络 ({str(e)})"

@tool
def scan_local_ports():
    """
    [端口猎手] 快速扫描本机常用端口 (20-1024 & 8000-8080)。
    指令：“扫描端口”、“检查开放端口”。
    """
    target = "127.0.0.1"
    open_ports = []
    # 常用端口列表，避免全扫描太慢
    common_ports = [21, 22, 80, 443, 3306, 5432, 6379, 8000, 8080, 8888]
    
    for port in common_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        result = sock.connect_ex((target, port))
        if result == 0:
            open_ports.append(str(port))
        sock.close()
        
    if open_ports:
        return f"PORT_HUNTER: 发现开放端口 -> {', '.join(open_ports)}"
    else:
        return "PORT_HUNTER: 目标区域无常用端口开放。"