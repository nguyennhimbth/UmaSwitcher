import os
import ctypes
import subprocess
import psutil
import time

STEAM_APP_ID = "1948430"
SYM_NAME_JP = "umamusume"
SYM_NAME_GLOBAL = "Umamusume"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def is_process_running(name):
    for p in psutil.process_iter(['name']):
        try:
            if p.info['name'] and p.info['name'].lower() == name.lower(): return True
        except: continue
    return False

def clean_all_symlinks(path_cygames):
    """Xóa cả hai loại tên thư mục để tránh xung đột hoặc lỗi 706"""
    for name in [SYM_NAME_JP, SYM_NAME_GLOBAL]:
        link_path = os.path.normpath(os.path.join(path_cygames, name))
        if os.path.lexists(link_path):
            try:
                # Juncktion/symlink removal
                subprocess.run(f'cmd /c rmdir /S /Q "{link_path}"', shell=True, check=True)
            except:
                try:
                    # rmidir fallback
                    os.remove(link_path)
                except:
                    pass

def launch_game_logic(version, config):
    """Xử lý logic symlink và khởi chạy game"""
    target_data = os.path.normpath(config[f"data_{version.lower()}"])
    game_exe = config[f"game_exe_{version.lower()}"]
    path_cygames = config["path_cygames"]
    
    if not target_data or not os.path.exists(target_data):
        raise ValueError("error_data")

    # Symlink name based on version
    current_sym_name = SYM_NAME_JP if version == "JP" else SYM_NAME_GLOBAL
    link_path = os.path.normpath(os.path.join(path_cygames, current_sym_name))

    parent = path_cygames
    if not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    
    # Clean existing symlinks before creating new one to avoid conflicts/errors
    clean_all_symlinks(path_cygames)
    
    # Symlink creation using CMD to ensure proper handling of Junctions/Symlinks and avoid error 706
    subprocess.run(f'mklink /D "{link_path}" "{target_data}"', shell=True, check=True)
    
    # Game launch logic
    if version == "JP":
        jp_mode = config.get("jp_launch_mode", "gcl")
        game_exe_jp_launch = config.get("game_exe_jp_launch", "")

        if jp_mode == "exe" and game_exe_jp_launch and os.path.exists(game_exe_jp_launch):
            # Chạy trực tiếp bằng file EXE
            subprocess.Popen(game_exe_jp_launch, cwd=os.path.dirname(game_exe_jp_launch))
        else:
            # Dùng GCL shortcut (mặc định)
            os.startfile("dmmgameplayer://play/GCL/umamusume/cl/win")
    else:
        if not is_process_running("steam.exe"):
            os.startfile("steam://")
            time.sleep(2)
        
        if game_exe and os.path.exists(game_exe):
            subprocess.Popen(game_exe, cwd=os.path.dirname(game_exe))
        else:
            os.startfile(f"steam://rungameid/{STEAM_APP_ID}")
            
    return current_sym_name