"""
UmaSwitcher - A More Compilacted Way To Use And Switch Between Umamusume Global and JP version
Made by: Duy Nguyeen (nguyennhimbth) with help of Gemini 3.0 Flash and 2.5 Flash, Claude Sonnet 4.6
Copyright (c) 2024 Duy Nguyeen (nguyennhimbth). This project is open-sourced under the [GNU GPLv3 License].
- This project is not affiliated with Cygames or any related entities, and it's not a mod or hack. 
- Use at your own risk. The author is not responsible for any damage or issues caused by using this software.
"""

import sys
import ctypes
from logic import is_admin
from gui import UmaLauncher

if __name__ == "__main__":
    # When debugging, sys.gettrace() is not None.
    # We skip the self-elevation when a debugger is attached to prevent it from crashing.
    if not is_admin() and sys.gettrace() is None:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    app = UmaLauncher()
    app.mainloop()