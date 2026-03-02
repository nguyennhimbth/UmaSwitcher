"""
Uma Launcher Pro - Version Switcher
Quản lý phiên bản JP và Global của Umamusume thông qua Symbolic Links.
Yêu cầu quyền Administrator.
"""

import os
import sys
import json
import subprocess
import threading
import time
import ctypes
import customtkinter as ctk
from tkinter import filedialog, colorchooser
import psutil
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# ─────────────────────────────────────────────
# ĐẢM BẢO QUYỀN ADMIN
# ─────────────────────────────────────────────
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# ─────────────────────────────────────────────
# CẤU HÌNH MẶC ĐỊNH
# ─────────────────────────────────────────────
CONFIG_FILE = "uma_config.json"
STEAM_APP_ID = "1948430"

# Tên thư mục Symlink riêng biệt theo yêu cầu
SYM_NAME_JP = "umamusume"      # Bản JP dùng viết thường
SYM_NAME_GLOBAL = "Umamusume"  # Bản Global dùng viết hoa đầu

TRANSLATIONS = {
    "vi": {
        "title": "CÀI ĐẶT",
        "path_cat": "📁 Đường dẫn",
        "ui_cat": "🎨 Giao diện",
        "save_all": "LƯU TẤT CẢ",
        "path_cygames": "Thư mục Cygames (AppData):",
        "data_jp": "Thư mục Data JP gốc:",
        "data_global": "Thư mục Data Global gốc:",
        "game_exe_jp": "File umamusume.exe (JP - Nhận diện):",
        "game_exe_global": "File umamusume.exe (Global - Khởi chạy):",
        "browse": "Chọn",
        "system_theme": "Chủ đề hệ thống:",
        "lang_select": "Ngôn ngữ (Language):",
        "jp_color": "Màu nút JP:",
        "gb_color": "Màu nút Global:",
        "pick_color": "Chọn màu",
        "dark": "Tối",
        "light": "Sáng",
        "btn_jp": "BẢN NHẬT (JP)",
        "btn_global": "QUỐC TẾ (GB)",
        "btn_reset": "Dọn dẹp tất cả Symlink (Reset)",
        "btn_settings": "⚙️ Cài đặt",
        "status_ready": "Trạng thái: Sẵn sàng",
        "status_cleaned": "Đã dọn dẹp tất cả Symlink.",
        "status_active": "Đã kích hoạt {version} ({sym})!",
        "status_error_data": "Lỗi: Chưa cấu hình đường dẫn data!",
        "status_error": "Lỗi: {error}"
    },
    "en": {
        "title": "SETTINGS",
        "path_cat": "📁 File Paths",
        "ui_cat": "🎨 Appearance",
        "save_all": "SAVE ALL",
        "path_cygames": "Cygames Folder (AppData):",
        "data_jp": "Original JP Data Folder:",
        "data_global": "Original Global Data Folder:",
        "game_exe_jp": "umamusume.exe (JP - Detection):",
        "game_exe_global": "umamusume.exe (Global - Launch):",
        "browse": "Browse",
        "system_theme": "System Theme:",
        "lang_select": "Language:",
        "jp_color": "JP Button Color:",
        "gb_color": "Global Button Color:",
        "pick_color": "Pick Color",
        "dark": "Dark",
        "light": "Light",
        "btn_jp": "JAPAN VERSION (JP)",
        "btn_global": "GLOBAL VERSION (GB)",
        "btn_reset": "Clean All Symlinks (Reset)",
        "btn_settings": "⚙️ Settings",
        "status_ready": "Status: Ready",
        "status_cleaned": "All Symlinks cleaned.",
        "status_active": "Activated {version} ({sym})!",
        "status_error_data": "Error: Data path not configured!",
        "status_error": "Error: {error}"
    }
}

DEFAULT_CONFIG = {
    "path_cygames": os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Cygames"),
    "data_jp": "",
    "data_global": "",
    "game_exe_jp": "",
    "game_exe_global": "",
    "appearance_mode": "dark",
    "language": "vi",
    "color_jp": "#fd60c9",
    "color_global": "#00a2ed"
}

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, config, save_callback):
        super().__init__(parent)
        self.title("Cài đặt đường dẫn")
        self.geometry("650x500")
        self.config = config
        self.save_callback = save_callback
        self.attributes('-topmost', True)
        self.grab_set() 
        
        self.lang = self.config.get("language", "vi")
        self.texts = TRANSLATIONS[self.lang]
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_sidebar()
        self.setup_content_area()
        self.show_page("path")

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=160, corner_radius=10, fg_color=("gray85", "gray15"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        
        self.side_title = ctk.CTkLabel(self.sidebar_frame, text=self.texts["title"], font=ctk.CTkFont(size=16, weight="bold"))
        self.side_title.pack(pady=(20, 20))
        
        self.btn_path = ctk.CTkButton(self.sidebar_frame, text=self.texts["path_cat"], 
                                      fg_color="transparent", 
                                      text_color=("gray10", "gray90"),
                                      hover_color=("gray75", "gray25"),
                                      anchor="w",
                                      command=lambda: self.show_page("path"))
        self.btn_path.pack(fill="x", padx=10, pady=5)
        
        self.btn_ui = ctk.CTkButton(self.sidebar_frame, text=self.texts["ui_cat"], 
                                    fg_color="transparent", 
                                    text_color=("gray10", "gray90"),
                                    hover_color=("gray75", "gray25"),
                                    anchor="w",
                                    command=lambda: self.show_page("ui"))
        self.btn_ui.pack(fill="x", padx=10, pady=5)

        self.btn_save = ctk.CTkButton(self.sidebar_frame, text=self.texts["save_all"],
                                      fg_color="#2ecc71", hover_color="#27ae60",
                                      text_color="white", font=ctk.CTkFont(weight="bold"),
                                      command=self.save_all_settings)
        self.btn_save.pack(side="bottom", fill="x", padx=10, pady=20)

    def setup_content_area(self):
        # Path Page
        self.path_page = ctk.CTkFrame(self, fg_color="transparent")
        self.setup_path_content(self.path_page)
        
        # UI Page
        self.ui_page = ctk.CTkFrame(self, fg_color="transparent")
        self.setup_ui_content(self.ui_page)

    def setup_path_content(self, parent):
        scroll = ctk.CTkScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.entries = {}
        self.path_widgets = {} # Store labels to update text later
        
        fields = [
            ("path_cygames", False),
            ("data_jp", False),
            ("data_global", False),
            ("game_exe_jp", True),
            ("game_exe_global", True)
        ]
        for key, is_file in fields:
            lbl = ctk.CTkLabel(scroll, text=self.texts[key], font=ctk.CTkFont(weight="bold"))
            lbl.pack(anchor="w", pady=(10, 2))
            
            frame = ctk.CTkFrame(scroll, fg_color="transparent")
            frame.pack(fill="x")
            entry = ctk.CTkEntry(frame)
            entry.insert(0, self.config.get(key, ""))
            entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
            self.entries[key] = entry
            
            btn = ctk.CTkButton(frame, text=self.texts["browse"], width=60, command=lambda e=entry, f=is_file: self.browse(e, f))
            btn.pack(side="right")
            
            self.path_widgets[key] = {"label": lbl, "btn": btn}

    def setup_ui_content(self, parent):
        content_inner = ctk.CTkFrame(parent, fg_color="transparent")
        content_inner.pack(expand=True, fill="both", padx=20, pady=20)

        self.lbl_lang = ctk.CTkLabel(content_inner, text=self.texts["lang_select"], font=ctk.CTkFont(weight="bold"))
        self.lbl_lang.pack(anchor="w")
        self.lang_menu = ctk.CTkOptionMenu(content_inner, values=["Tiếng Việt", "English"], command=self.change_language)
        self.lang_menu.set("Tiếng Việt" if self.lang == "vi" else "English")
        self.lang_menu.pack(anchor="w", pady=(5, 20), fill="x")

        self.lbl_theme = ctk.CTkLabel(content_inner, text=self.texts["system_theme"], font=ctk.CTkFont(weight="bold"))
        self.lbl_theme.pack(anchor="w")
        self.appearance_menu = ctk.CTkOptionMenu(content_inner, values=[self.texts["dark"], self.texts["light"]], command=self.update_theme)
        current_theme = self.config.get("appearance_mode", "dark")
        self.appearance_menu.set(self.texts["dark"] if current_theme == "dark" else self.texts["light"])
        self.appearance_menu.pack(anchor="w", pady=(5, 20), fill="x")

        self.lbl_jp_color = ctk.CTkLabel(content_inner, text=self.texts["jp_color"], font=ctk.CTkFont(weight="bold"))
        self.lbl_jp_color.pack(anchor="w")
        self.jp_color_btn = ctk.CTkButton(content_inner, text=self.texts["pick_color"], fg_color=self.config.get("color_jp", "#7cfff5"), text_color="white", command=lambda: self.pick_color("color_jp"))
        self.jp_color_btn.pack(anchor="w", pady=(5, 20), fill="x")

        self.lbl_gb_color = ctk.CTkLabel(content_inner, text=self.texts["gb_color"], font=ctk.CTkFont(weight="bold"))
        self.lbl_gb_color.pack(anchor="w")
        self.gb_color_btn = ctk.CTkButton(content_inner, text=self.texts["pick_color"], fg_color=self.config.get("color_global", "#00a2ed"), text_color="white", command=lambda: self.pick_color("color_global"))
        self.gb_color_btn.pack(anchor="w", pady=(5, 20), fill="x")

    def show_page(self, page):
        self.path_page.grid_forget()
        self.ui_page.grid_forget()
        
        if page == "path":
            self.path_page.grid(row=0, column=1, sticky="nsew")
            self.btn_path.configure(fg_color=("gray70", "gray30"), text_color=("#1f6aa5", "#66b3ff"))
            self.btn_ui.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        else:
            self.ui_page.grid(row=0, column=1, sticky="nsew")
            self.btn_ui.configure(fg_color=("gray70", "gray30"), text_color=("#1f6aa5", "#66b3ff"))
            self.btn_path.configure(fg_color="transparent", text_color=("gray10", "gray90"))

    def browse(self, entry, is_file):
        path = filedialog.askopenfilename() if is_file else filedialog.askdirectory()
        if path:
            path = os.path.normpath(path)
            entry.delete(0, "end")
            entry.insert(0, path)

    def change_language(self, choice):
        new_lang = "vi" if choice == "Tiếng Việt" else "en"
        if new_lang != self.lang:
            self.config["language"] = new_lang
            self.lang = new_lang
            self.texts = TRANSLATIONS[new_lang]
            self.refresh_ui_texts()
            self.save_callback()

    def refresh_ui_texts(self):
        self.side_title.configure(text=self.texts["title"])
        self.btn_path.configure(text=self.texts["path_cat"])
        self.btn_ui.configure(text=self.texts["ui_cat"])
        
        self.lbl_lang.configure(text=self.texts["lang_select"])
        self.lbl_theme.configure(text=self.texts["system_theme"])
        self.lbl_jp_color.configure(text=self.texts["jp_color"])
        self.lbl_gb_color.configure(text=self.texts["gb_color"])
        self.jp_color_btn.configure(text=self.texts["pick_color"])
        self.gb_color_btn.configure(text=self.texts["pick_color"])
        self.btn_save.configure(text=self.texts["save_all"])
        
        for key, widgets in self.path_widgets.items():
            widgets["label"].configure(text=self.texts[key])
            widgets["btn"].configure(text=self.texts["browse"])
        
        self.appearance_menu.configure(values=[self.texts["dark"], self.texts["light"]])
        current_theme = self.config.get("appearance_mode", "dark")
        self.appearance_menu.set(self.texts["dark"] if current_theme == "dark" else self.texts["light"])

    def update_theme(self, mode_text):
        mode = "dark" if (mode_text == "Tối" or mode_text == "Dark") else "light"
        ctk.set_appearance_mode(mode)
        self.config["appearance_mode"] = mode.lower()

    def pick_color(self, key):
        color = colorchooser.askcolor(initialcolor=self.config.get(key))[1]
        if color:
            self.config[key] = color
            if key == "color_jp": self.jp_color_btn.configure(fg_color=color)
            else: self.gb_color_btn.configure(fg_color=color)

    def save_all_settings(self):
        new_config = {key: entry.get() for key, entry in self.entries.items()}
        self.save_callback(new_config)
        self.destroy()

class UmaLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("UmaSwitcher")
        self.geometry("500x320")
        
        ctk.set_default_color_theme("blue")
        
        self.load_config()
        self.tray_icon = None
        self.is_quitting = False
        
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        ctk.set_appearance_mode(self.config.get("appearance_mode", "dark"))
        
        self.lang = self.config.get("language", "vi")
        self.texts = TRANSLATIONS[self.lang]
        self.setup_ui()
        self.init_tray()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config = {**DEFAULT_CONFIG, **json.load(f)}
            except: self.config = DEFAULT_CONFIG.copy()
        else: self.config = DEFAULT_CONFIG.copy()

    def save_config(self, new_data=None):
        if new_data: self.config.update(new_data)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        
        ctk.set_appearance_mode(self.config.get("appearance_mode", "dark"))
        if hasattr(self, 'btn_jp'): self.btn_jp.configure(fg_color=self.config.get("color_jp", "#7cfff5"))
        if hasattr(self, 'btn_global'): self.btn_global.configure(fg_color=self.config.get("color_global", "#00a2ed"))
        
        # Refresh Main UI Language
        self.lang = self.config.get("language", "vi")
        self.texts = TRANSLATIONS[self.lang]
        self.refresh_main_ui()

    def setup_ui(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(self.main_container, text="UmaSwitcher", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(10, 5))

        # Button Row
        self.button_row = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.button_row.pack(fill="x", pady=(0, 10))

        # JP Button
        self.btn_jp = ctk.CTkButton(
            self.button_row, 
            text=self.texts["btn_jp"], 
            height=100, 
            corner_radius=12,
            fg_color=self.config.get("color_jp", "#fd60c9"), # Sửa tại đây
            hover_color="#e050a0",                           # Sửa tại đây
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self.launch_game("JP")
        )
        self.btn_jp.pack(side="left", expand=True, padx=(0, 5), fill="both")

        # Global Button
        self.btn_global = ctk.CTkButton(
            self.button_row, 
            text=self.texts["btn_global"], 
            height=100, 
            corner_radius=12,
            fg_color=self.config.get("color_global", "#00a2ed"), 
            hover_color="#0086c4",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self.launch_game("Global")
        )
        self.btn_global.pack(side="right", expand=True, padx=(5, 0), fill="both")

        # Reset Button
        self.btn_reset = ctk.CTkButton(
            self.main_container, 
            text=self.texts["btn_reset"], 
            height=45, 
            corner_radius=8,
            fg_color="#dc3545", 
            hover_color="#c82333",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.manual_reset_link
        )
        self.btn_reset.pack(fill="x", pady=(5, 0))

        # Settings Button
        self.btn_settings = ctk.CTkButton(self.main_container, text=self.texts["btn_settings"], fg_color="transparent", text_color="gray", command=lambda: SettingsWindow(self, self.config, self.save_config))
        self.btn_settings.pack(side="bottom", pady=5)

        # Status Label
        self.status_lbl = ctk.CTkLabel(self.main_container, text=self.texts["status_ready"], text_color="gray")
        self.status_lbl.pack(side="bottom", pady=(10, 0))

    def refresh_main_ui(self):
        self.btn_jp.configure(text=self.texts["btn_jp"])
        self.btn_global.configure(text=self.texts["btn_global"])
        self.btn_reset.configure(text=self.texts["btn_reset"])
        self.btn_settings.configure(text=self.texts["btn_settings"])
        self.status_lbl.configure(text=self.texts["status_ready"])

    def init_tray(self):
        def create_image():
            image = Image.new('RGB', (64, 64), color=(30, 30, 30))
            draw = ImageDraw.Draw(image)
            draw.ellipse((16, 16, 48, 48), fill=(0, 162, 237))
            return image
        
        menu = pystray.Menu(item('Hiện Launcher', self.show_from_tray, default=True), item('Dọn dẹp Symlink', lambda: self.after(0, self.manual_reset_link)), item('Thoát', self.quit_app))
        self.tray_icon = pystray.Icon("UmaLauncher", create_image(), "Uma Launcher Pro", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def hide_to_tray(self):
        if not self.is_quitting: self.after(0, self.withdraw)

    def show_from_tray(self, icon=None, item=None):
        if not self.is_quitting: self.after(0, self.deiconify)

    def quit_app(self, icon=None, item=None):
        self.is_quitting = True
        if self.tray_icon: self.tray_icon.stop()
        self.after(0, self.destroy)
        os._exit(0)

    def is_process_running(self, name):
        for p in psutil.process_iter(['name']):
            try:
                if p.info['name'] and p.info['name'].lower() == name.lower(): return True
            except: continue
        return False

    def clean_all_symlinks(self):
        """Xóa cả hai loại tên thư mục để tránh xung đột hoặc lỗi 706"""
        for name in [SYM_NAME_JP, SYM_NAME_GLOBAL]:
            link_path = os.path.normpath(os.path.join(self.config["path_cygames"], name))
            if os.path.lexists(link_path):
                try:
                    # Sử dụng lệnh CMD để xóa triệt để Junction/Symlink
                    subprocess.run(f'cmd /c rmdir /S /Q "{link_path}"', shell=True, check=True)
                except:
                    try:
                        # Fallback nếu rmdir thất bại
                        os.remove(link_path)
                    except:
                        pass

    def manual_reset_link(self):
        self.clean_all_symlinks()
        if self.winfo_exists():
            self.status_lbl.configure(text=self.texts["status_cleaned"], text_color="#28a745")

    def launch_game(self, version):
        target_data = os.path.normpath(self.config[f"data_{version.lower()}"])
        game_exe = self.config[f"game_exe_{version.lower()}"]
        
        if not target_data or not os.path.exists(target_data):
            self.status_lbl.configure(text=self.texts["status_error_data"], text_color="#dc3545")
            return

        # Xác định tên symlink dựa trên phiên bản yêu cầu
        current_sym_name = SYM_NAME_JP if version == "JP" else SYM_NAME_GLOBAL
        link_path = os.path.normpath(os.path.join(self.config["path_cygames"], current_sym_name))

        try:
            parent = self.config["path_cygames"]
            if not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
            
            # Luôn dọn dẹp cả hai (viết hoa và viết thường) trước khi tạo mới để tránh lỗi 706
            self.clean_all_symlinks()
            
            # Tạo liên kết mới với đúng tên yêu cầu (umamusume cho JP, Umamusume cho Global)
            subprocess.run(f'mklink /D "{link_path}" "{target_data}"', shell=True, check=True)
            
            if self.winfo_exists():
                self.status_lbl.configure(text=self.texts["status_active"].format(version=version, sym=current_sym_name), text_color="#28a745")

            # Khởi chạy ứng dụng tương ứng
            if version == "JP":
                os.startfile("dmmgameplayer://play/GCL/umamusume/cl/win")
            else:
                if not self.is_process_running("steam.exe"):
                    os.startfile("steam://")
                    time.sleep(2)
                
                if game_exe and os.path.exists(game_exe):
                    subprocess.Popen(game_exe, cwd=os.path.dirname(game_exe))
                else:
                    os.startfile(f"steam://rungameid/{STEAM_APP_ID}")
        except Exception as e:
            if self.winfo_exists():
                self.status_lbl.configure(text=self.texts["status_error"].format(error=str(e)), text_color="#dc3545")
            print(f"Lỗi khởi chạy: {e}")

if __name__ == "__main__":
    app = UmaLauncher()
    app.mainloop()