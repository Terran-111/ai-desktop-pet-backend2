import os
import shutil
from langchain_core.tools import tool

@tool
def organize_desktop():
    """
    [智能归档] 一键整理桌面文件。
    将图片、文档、压缩包归类到 Desktop/AutoArchive 下的对应文件夹。
    """
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    base_dir = os.path.join(desktop, "AutoArchive")
    
    rules = {
        "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        "Docs": ['.doc', '.docx', '.pdf', '.txt', '.xlsx', '.ppt', '.md'],
        "Archives": ['.zip', '.rar', '.7z', '.tar', '.gz'],
        "Code": ['.py', '.js', '.html', '.css', '.cpp', '.java']
    }
    
    moved_count = 0
    
    for filename in os.listdir(desktop):
        src = os.path.join(desktop, filename)
        if os.path.isfile(src):
            ext = os.path.splitext(filename)[1].lower()
            for folder, exts in rules.items():
                if ext in exts:
                    target_dir = os.path.join(base_dir, folder)
                    os.makedirs(target_dir, exist_ok=True)
                    try:
                        shutil.move(src, os.path.join(target_dir, filename))
                        moved_count += 1
                    except:
                        pass
                    break
    
    return f"ARCHIVE_COMPLETE: 已迁移 {moved_count} 个文件至 {base_dir}。"

@tool
def search_large_files(directory: str = None):
    """
    [大文件捕手] 扫描指定目录(默认用户目录)下最大的5个文件。
    Args:
        directory: 扫描路径，默认为 None (扫描用户主目录)
    """
    if not directory:
        directory = os.path.expanduser("~")
        
    files_list = []
    try:
        # 限制扫描深度，防止太慢
        for root, dirs, files in os.walk(directory):
            # 跳过系统目录
            if 'Windows' in root or 'AppData' in root:
                continue
            for name in files:
                try:
                    path = os.path.join(root, name)
                    size = os.path.getsize(path)
                    files_list.append((name, size / (1024*1024))) # MB
                except:
                    continue
            if len(files_list) > 10000: break # 简单熔断
    except Exception as e:
        return f"SCAN_ERROR: {str(e)}"

    files_list.sort(key=lambda x: x[1], reverse=True)
    top5 = files_list[:5]
    
    res = "DISK_CLEANER_REPORT (Top 5):\n"
    for name, size in top5:
        res += f"- {name}: {size:.2f} MB\n"
    return res