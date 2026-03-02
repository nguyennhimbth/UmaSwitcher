# UmaSwitcher Project Mandates

## Project Overview
UmaSwitcher is a Python-based utility designed to toggle between the Japanese (JP) and Global versions of *Umamusume Pretty Derby* by managing symbolic links in the `AppData\LocalLow\Cygames` directory.

## Critical Logic & Technical Standards

### 1. Symbolic Link Management (The "Rule of Case")
The game's data directory name is case-sensitive depending on the version:
- **JP Version (DMM):** Must be named `umamusume` (all lowercase).
- **Global Version (Steam):** Must be named `Umamusume` (capitalized 'U').
- **Mandate:** Before creating a new link, ALWAYS search for and remove both `umamusume` and `Umamusume` to prevent "Error 706" or collision issues. Use `subprocess.run(['cmd', '/c', 'rmdir', ...])` for robust removal of junctions/links.

### 2. Privilege Escalation
- **Mandate:** The application MUST run with Administrator privileges to create symbolic links (`mklink`). Always include the `is_admin()` check and restart logic at the entry point.

### 3. Safety Protocols
- **Data Protection:** NEVER use recursive deletion (`shutil.rmtree`) on paths that could be symlinks/junctions unless you have verified they are NOT the source data folders. Always prefer `os.remove` or `os.rmdir` (which fails on non-empty directories) to ensure only the link is severed.

### 4. UI & UX Standards
- **Library:** Use `customtkinter` (ctk) for a modern, dark-themed UI.
- **Background Operation:** Maintain a system tray icon using `pystray` for persistent monitoring and quick access.
- **Status Feedback:** Provide clear visual feedback in the UI when a version is successfully linked or when an error occurs.

### 5. Path Configuration
- Paths should be normalized using `os.path.normpath`.
- Configurations are stored in `uma_config.json`. Always merge existing config with `DEFAULT_CONFIG` to handle missing keys gracefully.

## Tech Stack
- **Language:** Python 3.x
- **UI:** `customtkinter`, `tkinter`
- **System:** `psutil`, `ctypes`, `pystray`, `PIL` (Pillow)
- **Deployment:** Targets Windows OS.
