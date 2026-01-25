import os
import winreg
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter import colorchooser
import configparser
from datetime import datetime
import zipfile

# --- Import show_memory_chips function ---
from show_memory_chips import show_memory_chips

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- Main Window ---
root = tk.Tk()
root.title("SAOFB Mod Manager")
try:
    icon_path = resource_path("icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    else:
        print(f"Icon not found at: {icon_path}")
except tk.TclError as e:
    print(f"Icon load error: {e}")
except Exception as e:
    print(f"Unexpected error loading icon: {e}")

root.geometry("800x600")

# --- Configuration ---
STEAM_APP_ID = "626690"
GAME_FOLDER_NAME = "SWORD ART ONLINE FATAL BULLET"
GAME_MOD_PATH_RELATIVE = "SAOFB\\Content\\Paks\\~mods"
LOGIC_MOD_PATH_RELATIVE = "SAOFB\\Content\\Paks\\LogicMods"
DISABLED_LOGICMOD_PATH_RELATIVE = "SAOFB\\Content\\disabled_LogicMods"
GAME_EXECUTABLE = "SAOFB.exe"
GAME_PATH = ""
# Default save file path - uses AppData for current Windows user
DEFAULT_SAVE_FILE_PATH = os.path.expanduser(r"~\AppData\Local\SAOFB\Saved\SaveGames")
SAVE_FILE_PATH = DEFAULT_SAVE_FILE_PATH
BACKUP_FOLDER = "SaveGameBackups"

SETTINGS_FILE = "settings.ini"

# --- Default Colors ---
mod_colors = {
    "enabled": "green",
    "disabled": "red",
    "logicmod": "blue",
    "logicmod_disabled": "purple"
}

# --- File Management Functions ---

def find_steam_paths():
    paths = []
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam")
        steam_path = winreg.QueryValueEx(reg_key, "InstallPath")[0]
        paths.append(steam_path)
        vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf_path):
            with open(vdf_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if '"path"' in line:
                        parts = line.split('"')
                        for i, part in enumerate(parts):
                            if part == "path" and i+2 < len(parts):
                                lib_path = parts[i+2].replace("\\\\", "\\")
                                if os.path.exists(lib_path):
                                    paths.append(lib_path)
            import re
            with open(vdf_path, "r", encoding="utf-8") as f:
                for line in f:
                    match = re.search(r'"\\d+"\s+"(.+?)"', line)
                    if match:
                        lib_path = match.group(1).replace("\\\\", "\\")
                        if os.path.exists(lib_path):
                            paths.append(lib_path)
    except Exception:
        pass
    return list(set(paths))

def find_game_path_auto():
    global GAME_PATH
    steam_paths = find_steam_paths()
    for steam_path in steam_paths:
        game_path = os.path.join(steam_path, "steamapps", "common", GAME_FOLDER_NAME)
        mods_path = os.path.join(game_path, GAME_MOD_PATH_RELATIVE)
        if os.path.exists(mods_path):
            GAME_PATH = game_path
            status_label.config(text=f"Game Path Found: {GAME_PATH}")
            update_mod_lists()
            return True
    messagebox.showwarning("Warning", "Automatic path detection failed. Please select the game folder manually.")
    get_game_path_manual()
    return False

def get_game_path_manual():
    global GAME_PATH
    GAME_PATH = filedialog.askdirectory(title="Select your SAO: Fatal Bullet folder")
    if not GAME_PATH:
        messagebox.showerror("Error", "Game folder not selected.")
        return False
    full_mods_path = os.path.join(GAME_PATH, GAME_MOD_PATH_RELATIVE)
    if not os.path.exists(full_mods_path):
        messagebox.showerror("Error", f"Could not find the game's mods folder at:\n{full_mods_path}")
        GAME_PATH = ""
        return False
    status_label.config(text=f"Game Path: {GAME_PATH}")
    update_mod_lists()
    return True

# --- UI Layout ---
frame_mods = tk.Frame(root)
frame_mods.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# --- Search Bar ---
search_var = tk.StringVar()
search_frame = tk.Frame(frame_mods)
search_frame.pack(fill=tk.X, pady=(0,5))
search_label = tk.Label(search_frame, text="Search Mods:")
search_label.pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame, textvariable=search_var)
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

# --- Mods/LogicMods Filter Row ---
filter_mode = tk.StringVar(value="all")  # "all", "mods", "paks", "logicmods"

def set_filter_mode(mode):
    filter_mode.set(mode)
    update_mod_lists()
    # Update label styles
    if mode == "mods":
        mods_label.config(font=("Segoe UI", 10, "bold"))
        paks_label.config(font=("Segoe UI", 10, "normal"))
        logicmods_label.config(font=("Segoe UI", 10, "normal"))
    elif mode == "paks":
        mods_label.config(font=("Segoe UI", 10, "normal"))
        paks_label.config(font=("Segoe UI", 10, "bold"))
        logicmods_label.config(font=("Segoe UI", 10, "normal"))
    elif mode == "logicmods":
        mods_label.config(font=("Segoe UI", 10, "normal"))
        paks_label.config(font=("Segoe UI", 10, "normal"))
        logicmods_label.config(font=("Segoe UI", 10, "bold"))
    else:
        mods_label.config(font=("Segoe UI", 10, "normal"))
        paks_label.config(font=("Segoe UI", 10, "normal"))
        logicmods_label.config(font=("Segoe UI", 10, "normal"))

labels_row = tk.Frame(frame_mods)
labels_row.pack(fill=tk.X)

mods_label = tk.Label(labels_row, text="~mods Folder Contents:", cursor="hand2", fg="#0055aa")
mods_label.pack(side=tk.LEFT, padx=(0,20))
mods_label.bind("<Button-1>", lambda e: set_filter_mode("mods"))

paks_label = tk.Label(labels_row, text="Paks Folder Contents:", cursor="hand2", fg="#0055aa")
paks_label.pack(side=tk.LEFT, padx=(0,20))
paks_label.bind("<Button-1>", lambda e: set_filter_mode("paks"))

logicmods_label = tk.Label(labels_row, text="LogicMods Folder Contents:", cursor="hand2", fg="#0055aa")
logicmods_label.pack(side=tk.LEFT)
logicmods_label.bind("<Button-1>", lambda e: set_filter_mode("logicmods"))

disabled_info_label = tk.Label(
    frame_mods,
    text=(
        "Note: Disabled mods are stored in the 'disabled_mods' folder inside Content.\n"
        "Disabled LogicMods are stored in the 'disabled_LogicMods' folder inside Content."
    ),
    fg="gray", anchor="w"
)
disabled_info_label.pack(fill=tk.X, padx=2, pady=(0,8))

mods_tree = ttk.Treeview(frame_mods, columns=("mod", "status", "type"), show="headings", height=15)
mods_tree.heading("mod", text="Mod File")
mods_tree.heading("status", text="Status")
mods_tree.heading("type", text="Type")
mods_tree.column("mod", width=350)
mods_tree.column("status", width=100, anchor="center")
mods_tree.column("type", width=100, anchor="center")
mods_tree.pack(fill=tk.BOTH, expand=True)

mods_tree.tag_configure("enabled", foreground="green")
mods_tree.tag_configure("disabled", foreground="red")
mods_tree.tag_configure("logicmod", foreground="blue")
mods_tree.tag_configure("logicmod_disabled", foreground="purple")

status_label = tk.Label(frame_mods, text="", anchor="w", fg="blue")
status_label.pack(fill=tk.X, padx=2, pady=(5,0))

# --- Mod List Functions ---

def filter_mods(*args):
    search_text = search_var.get().lower()
    mods_tree.delete(*mods_tree.get_children())
    # --- Regular mods ---
    mods_path = os.path.join(GAME_PATH, GAME_MOD_PATH_RELATIVE)
    main_paks_path = os.path.join(GAME_PATH, "SAOFB", "Content", "Paks")
    
    content_folder = os.path.join(GAME_PATH, "SAOFB", "Content")
    disabled_path = os.path.join(content_folder, "disabled_mods")
    # --- LogicMods ---
    logicmods_path = os.path.join(GAME_PATH, LOGIC_MOD_PATH_RELATIVE)
    disabled_logicmods_path = os.path.join(GAME_PATH, DISABLED_LOGICMOD_PATH_RELATIVE)
    pak_mods = []
    disabled_mods = []
    logic_mods = []
    disabled_logic_mods = []
    # Mods from ~mods folder
    if os.path.exists(mods_path):
        pak_mods = [f for f in os.listdir(mods_path) if f.lower().endswith('.pak') and os.path.isfile(os.path.join(mods_path, f))]
    # Mods from main Paks folder (excluding base game files)
    paks_mods = []
    if os.path.exists(main_paks_path):
        paks_mods = [f for f in os.listdir(main_paks_path) if f.lower().endswith('.pak') and os.path.isfile(os.path.join(main_paks_path, f))
                     and not f.lower().startswith('saofb-windowsnoeditor')]
    
    if not os.path.exists(disabled_path):
        os.makedirs(disabled_path)
    disabled_mods = [f for f in os.listdir(disabled_path) if f.lower().endswith('.pak') and os.path.isfile(os.path.join(disabled_path, f))]
    
    # LogicMods
    if os.path.exists(logicmods_path):
        logic_mods = [f for f in os.listdir(logicmods_path) if f.lower().endswith('.pak') and os.path.isfile(os.path.join(logicmods_path, f)) 
                      and not f.lower().startswith('saofb-windowsnoeditor')]
        if not os.path.exists(disabled_logicmods_path):
            os.makedirs(disabled_logicmods_path)
        disabled_logic_mods = [f for f in os.listdir(disabled_logicmods_path) if f.lower().endswith('.pak') and os.path.isfile(os.path.join(disabled_logicmods_path, f))
                               and not f.lower().startswith('saofb-windowsnoeditor')]
    # Insert mods based on filter
    mode = filter_mode.get()
    if mode == "mods":
        for mod in pak_mods:
            if search_text in mod.lower():
                mods_tree.insert("", "end", values=(mod, "Enabled", "Mod"), tags=("enabled",))
        for mod in disabled_mods:
            if search_text in mod.lower():
                mods_tree.insert("", "end", values=(mod, "Disabled", "Mod"), tags=("disabled",))
    elif mode == "paks":
        for mod in paks_mods:
            if search_text in mod.lower():
                mods_tree.insert("", "end", values=(mod, "Enabled", "Mod"), tags=("enabled",))
    elif mode == "logicmods":
        for mod in logic_mods:
            if search_text in mod.lower():
                mods_tree.insert("", "end", values=(mod, "Enabled", "LogicMod"), tags=("logicmod",))
        for mod in disabled_logic_mods:
            if search_text in mod.lower():
                mods_tree.insert("", "end", values=(mod, "Disabled", "LogicMod"), tags=("logicmod_disabled",))
    else:  # "all"
        for mod in pak_mods:
            if search_text in mod.lower():
                mods_tree.insert("", "end", values=(mod, "Enabled", "Mod"), tags=("enabled",))
        for mod in paks_mods:
            if search_text in mod.lower():
                mods_tree.insert("", "end", values=(mod, "Enabled", "Mod"), tags=("enabled",))
        for mod in disabled_mods:
            if search_text in mod.lower():
                mods_tree.insert("", "end", values=(mod, "Disabled", "Mod"), tags=("disabled",))
        for mod in logic_mods:
            if search_text in mod.lower():
                mods_tree.insert("", "end", values=(mod, "Enabled", "LogicMod"), tags=("logicmod",))
        for mod in disabled_logic_mods:
            if search_text in mod.lower():
                mods_tree.insert("", "end", values=(mod, "Disabled", "LogicMod"), tags=("logicmod_disabled",))
    status_label.config(
        text=f"~mods: {len(pak_mods)} | Paks: {len(paks_mods)} | LogicMods: {len(logic_mods)} | Disabled: {len(disabled_mods)} mods, {len(disabled_logic_mods)} logicmods."
    )

search_var.trace_add("write", filter_mods)

def update_mod_lists():
    filter_mods()

# --- Enable/Disable Functions ---

def enable_mod():
    selection = mods_tree.selection()
    if not selection:
        messagebox.showinfo("Info", "Select a mod to enable.")
        return
    item = mods_tree.item(selection[0])
    mod_file = item['values'][0]
    status = item['values'][1]
    mod_type = item['values'][2]
    if status != "Disabled":
        messagebox.showinfo("Info", "Selected mod is already enabled.")
        return
    if mod_type == "Mod":
        mods_path = os.path.join(GAME_PATH, GAME_MOD_PATH_RELATIVE)
        disabled_path = os.path.join(GAME_PATH, "SAOFB", "Content", "disabled_mods")
        src = os.path.join(disabled_path, mod_file)
        dst = os.path.join(mods_path, mod_file)
        sig_src = os.path.join(disabled_path, mod_file[:-4] + ".sig")
        sig_dst = os.path.join(mods_path, mod_file[:-4] + ".sig")
    elif mod_type == "LogicMod":
        mods_path = os.path.join(GAME_PATH, LOGIC_MOD_PATH_RELATIVE)
        disabled_path = os.path.join(GAME_PATH, DISABLED_LOGICMOD_PATH_RELATIVE)
        src = os.path.join(disabled_path, mod_file)
        dst = os.path.join(mods_path, mod_file)
        sig_src = os.path.join(disabled_path, mod_file[:-4] + ".sig")
        sig_dst = os.path.join(mods_path, mod_file[:-4] + ".sig")
    else:
        messagebox.showerror("Error", "Unknown mod type.")
        return
    try:
        shutil.move(src, dst)
        if os.path.exists(sig_src):
            shutil.move(sig_src, sig_dst)
        update_mod_lists()
        status_label.config(text=f"Enabled: {mod_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to enable mod: {e}")

def disable_mod():
    selection = mods_tree.selection()
    if not selection:
        messagebox.showinfo("Info", "Select a mod to disable.")
        return
    item = mods_tree.item(selection[0])
    mod_file = item['values'][0]
    status = item['values'][1]
    mod_type = item['values'][2]
    if status != "Enabled":
        messagebox.showinfo("Info", "Selected mod is already disabled.")
        return
    if mod_type == "Mod":
        mods_path = os.path.join(GAME_PATH, GAME_MOD_PATH_RELATIVE)
        disabled_path = os.path.join(GAME_PATH, "SAOFB", "Content", "disabled_mods")
        src = os.path.join(mods_path, mod_file)
        dst = os.path.join(disabled_path, mod_file)
        sig_src = os.path.join(mods_path, mod_file[:-4] + ".sig")
        sig_dst = os.path.join(disabled_path, mod_file[:-4] + ".sig")
    elif mod_type == "LogicMod":
        mods_path = os.path.join(GAME_PATH, LOGIC_MOD_PATH_RELATIVE)
        disabled_path = os.path.join(GAME_PATH, DISABLED_LOGICMOD_PATH_RELATIVE)
        src = os.path.join(mods_path, mod_file)
        dst = os.path.join(disabled_path, mod_file)
        sig_src = os.path.join(mods_path, mod_file[:-4] + ".sig")
        sig_dst = os.path.join(disabled_path, mod_file[:-4] + ".sig")
    else:
        messagebox.showerror("Error", "Unknown mod type.")
        return
    try:
        shutil.move(src, dst)
        if os.path.exists(sig_src):
            shutil.move(sig_src, sig_dst)
        update_mod_lists()
        status_label.config(text=f"Disabled: {mod_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to disable mod: {e}")

# --- Save File Backup Functions ---

def backup_save_files():
    """Backup the save game files to a timestamped folder."""
    if not os.path.exists(SAVE_FILE_PATH):
        messagebox.showerror("Error", f"Save file path not found:\n{SAVE_FILE_PATH}")
        return False
    
    # Create backup folder if it doesn't exist
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
    
    # Create timestamped backup folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_FOLDER, f"SaveGames_Backup_{timestamp}")
    
    try:
        # Create the backup directory
        os.makedirs(backup_path, exist_ok=True)
        
        # Copy all save files
        files_copied = 0
        for file in os.listdir(SAVE_FILE_PATH):
            src = os.path.join(SAVE_FILE_PATH, file)
            dst = os.path.join(backup_path, file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                files_copied += 1
        
        if files_copied > 0:
            messagebox.showinfo("Success", f"Backed up {files_copied} save file(s) to:\n{backup_path}")
            status_label.config(text=f"Backup completed: {files_copied} save file(s) backed up")
            return True
        else:
            messagebox.showwarning("Warning", "No save files found to backup.")
            return False
    except Exception as e:
        messagebox.showerror("Error", f"Failed to backup save files: {e}")
        return False

def open_backup_folder():
    """Open the backup folder in Windows Explorer."""
    if not os.path.exists(BACKUP_FOLDER):
        messagebox.showinfo("Info", f"Backup folder not found. Create a backup first.")
        return
    
    try:
        os.startfile(BACKUP_FOLDER)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open backup folder: {e}")

# --- Folder Opening Functions ---

def open_mods_folder():
    """Open the mods folder."""
    if not GAME_PATH:
        messagebox.showwarning("Warning", "Game path not found. Please detect or select game path first.")
        return
    mods_path = os.path.join(GAME_PATH, GAME_MOD_PATH_RELATIVE)
    if not os.path.exists(mods_path):
        messagebox.showerror("Error", f"Mods folder not found:\n{mods_path}")
        return
    try:
        os.startfile(mods_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open mods folder: {e}")

def open_logicmods_folder():
    """Open the LogicMods folder."""
    if not GAME_PATH:
        messagebox.showwarning("Warning", "Game path not found. Please detect or select game path first.")
        return
    logicmods_path = os.path.join(GAME_PATH, LOGIC_MOD_PATH_RELATIVE)
    if not os.path.exists(logicmods_path):
        messagebox.showerror("Error", f"LogicMods folder not found:\n{logicmods_path}")
        return
    try:
        os.startfile(logicmods_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open LogicMods folder: {e}")

def open_disabled_mods_folder():
    """Open the disabled mods folder."""
    if not GAME_PATH:
        messagebox.showwarning("Warning", "Game path not found. Please detect or select game path first.")
        return
    disabled_path = os.path.join(GAME_PATH, "SAOFB", "Content", "disabled_mods")
    if not os.path.exists(disabled_path):
        messagebox.showerror("Error", f"Disabled mods folder not found:\n{disabled_path}")
        return
    try:
        os.startfile(disabled_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open disabled mods folder: {e}")

def open_disabled_logicmods_folder():
    """Open the disabled LogicMods folder."""
    if not GAME_PATH:
        messagebox.showwarning("Warning", "Game path not found. Please detect or select game path first.")
        return
    disabled_logicmods_path = os.path.join(GAME_PATH, DISABLED_LOGICMOD_PATH_RELATIVE)
    if not os.path.exists(disabled_logicmods_path):
        messagebox.showerror("Error", f"Disabled LogicMods folder not found:\n{disabled_logicmods_path}")
        return
    try:
        os.startfile(disabled_logicmods_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open disabled LogicMods folder: {e}")

def open_save_games_folder():
    """Open the save games folder."""
    if not os.path.exists(SAVE_FILE_PATH):
        messagebox.showerror("Error", f"Save games folder not found:\n{SAVE_FILE_PATH}")
        return
    try:
        os.startfile(SAVE_FILE_PATH)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open save games folder: {e}")

# --- Buttons ---
frame_buttons = tk.Frame(root)
frame_buttons.pack(fill=tk.X, padx=10, pady=5)

enable_btn = tk.Button(frame_buttons, text="Enable Selected Mod", command=enable_mod)
enable_btn.pack(side=tk.LEFT, padx=5)

disable_btn = tk.Button(frame_buttons, text="Disable Selected Mod", command=disable_mod)
disable_btn.pack(side=tk.LEFT, padx=5)

reload_btn = tk.Button(frame_buttons, text="Reload Mods", command=update_mod_lists)
reload_btn.pack(side=tk.LEFT, padx=5)

backup_save_btn = tk.Button(frame_buttons, text="Backup Save Files", command=backup_save_files)
backup_save_btn.pack(side=tk.LEFT, padx=5)

open_backup_btn = tk.Button(frame_buttons, text="Open Backups", command=open_backup_folder)
open_backup_btn.pack(side=tk.LEFT, padx=5)

# --- Folder Access Buttons ---
folders_frame = tk.Frame(root)
folders_frame.pack(fill=tk.X, padx=10, pady=5)

tk.Label(folders_frame, text="Quick Folder Access:", fg="gray").pack(side=tk.LEFT, padx=5)

open_mods_btn = tk.Button(folders_frame, text="Open ~mods", command=open_mods_folder)
open_mods_btn.pack(side=tk.LEFT, padx=2)

open_logicmods_btn = tk.Button(folders_frame, text="Open LogicMods", command=open_logicmods_folder)
open_logicmods_btn.pack(side=tk.LEFT, padx=2)

open_disabled_btn = tk.Button(folders_frame, text="Open Disabled Mods", command=open_disabled_mods_folder)
open_disabled_btn.pack(side=tk.LEFT, padx=2)

open_disabled_logicmods_btn = tk.Button(folders_frame, text="Open Disabled LogicMods", command=open_disabled_logicmods_folder)
open_disabled_logicmods_btn.pack(side=tk.LEFT, padx=2)

open_savegames_btn = tk.Button(folders_frame, text="Open Save Games", command=open_save_games_folder)
open_savegames_btn.pack(side=tk.LEFT, padx=2)

def show_info():
    messagebox.showinfo(
        "Mod Manager Info",
        "SAOFB Mod Manager\n\n"
        "Mod Management:\n"
        "• Use the search bar to filter mods by name.\n"
        "• Select a mod and click Enable/Disable to toggle its status.\n"
        "• Reload Mods refreshes the mod list.\n"
        "• Disabled mods are moved to the 'disabled_mods' folder inside Content.\n\n"
        "Save File Backup:\n"
        "• Click 'Backup Save Files' to create a timestamped backup of your save games.\n"
        "• Click 'Open Backups' to view your backed up save files.\n"
        "• Backups are stored in the 'SaveGameBackups' folder."
    )

info_btn = tk.Button(frame_buttons, text="Info", command=show_info)
info_btn.pack(side=tk.LEFT, padx=5)

# --- Add Show Memory Chips Button ---
memory_chips_btn = tk.Button(frame_buttons, text="Show Memory Chips", command=show_memory_chips)
memory_chips_btn.pack(side=tk.LEFT, padx=5)

# --- Color Management ---
def apply_mod_colors():
    mods_tree.tag_configure("enabled", foreground=mod_colors["enabled"])
    mods_tree.tag_configure("disabled", foreground=mod_colors["disabled"])
    mods_tree.tag_configure("logicmod", foreground=mod_colors["logicmod"])
    mods_tree.tag_configure("logicmod_disabled", foreground=mod_colors["logicmod_disabled"])

def choose_color(tag, label):
    color = colorchooser.askcolor(title=f"Choose color for {label}")[1]
    if color:
        mod_colors[tag] = color
        apply_mod_colors()
        save_settings_to_file()  # <-- Save after change
        update_mod_lists()

# --- Load mod colors from settings file ---
def load_mod_colors():
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
        if "Colors" in config:
            for key in mod_colors:
                if key in config["Colors"]:
                    mod_colors[key] = config["Colors"][key]

def load_settings_from_file():
    global SAVE_FILE_PATH
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
        if "Paths" in config and "save_file_path" in config["Paths"]:
            SAVE_FILE_PATH = config["Paths"]["save_file_path"]

def save_mod_colors():
    config = configparser.ConfigParser()
    config["Colors"] = {k: v for k, v in mod_colors.items()}
    with open(SETTINGS_FILE, "w") as f:
        config.write(f)

def save_settings_to_file():
    config = configparser.ConfigParser()
    # Preserve existing colors
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
    config["Colors"] = {k: v for k, v in mod_colors.items()}
    config["Paths"] = {"save_file_path": SAVE_FILE_PATH}
    with open(SETTINGS_FILE, "w") as f:
        config.write(f)

def open_settings():
    settings_win = tk.Toplevel(root)
    settings_win.title("Settings")
    settings_win.resizable(False, False)
    
    # --- Mod Colors Section ---
    tk.Label(settings_win, text="Change mod list colors:", font=("Segoe UI", 10, "bold")).pack(pady=(10,5), padx=10, anchor="w")
    for tag, label in [
        ("enabled", "Enabled Mod"),
        ("disabled", "Disabled Mod"),
        ("logicmod", "Enabled LogicMod"),
        ("logicmod_disabled", "Disabled LogicMod")
    ]:
        row = tk.Frame(settings_win)
        row.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(row, text=label, width=18, anchor="w").pack(side=tk.LEFT)
        color_btn = tk.Button(row, text="Choose...", command=lambda t=tag, l=label: choose_color(t, l))
        color_btn.pack(side=tk.LEFT, padx=5)
        color_preview = tk.Label(row, bg=mod_colors[tag], width=4, relief="ridge")
        color_preview.pack(side=tk.LEFT, padx=5)
        # Update preview when color changes
        def update_preview(tag=tag, preview=color_preview):
            preview.config(bg=mod_colors[tag])
        color_btn.config(command=lambda t=tag, l=label, up=update_preview: [choose_color(t, l), up()])
    
    # --- Save File Path Section ---
    tk.Label(settings_win, text="Save File Path Settings:", font=("Segoe UI", 10, "bold")).pack(pady=(15,5), padx=10, anchor="w")
    
    path_frame = tk.Frame(settings_win)
    path_frame.pack(fill=tk.X, padx=10, pady=5)
    
    tk.Label(path_frame, text="Save Game Path:", anchor="w", width=15).pack(side=tk.LEFT)
    
    path_var = tk.StringVar(value=SAVE_FILE_PATH)
    path_entry = tk.Entry(path_frame, textvariable=path_var, width=50)
    path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def browse_save_path():
        folder = filedialog.askdirectory(title="Select Save Game Folder", initialdir=SAVE_FILE_PATH)
        if folder:
            path_var.set(folder)
    
    browse_btn = tk.Button(path_frame, text="Browse...", command=browse_save_path)
    browse_btn.pack(side=tk.LEFT, padx=5)
    
    def save_settings():
        global SAVE_FILE_PATH
        SAVE_FILE_PATH = path_var.get()
        save_mod_colors()
        save_settings_to_file()
        messagebox.showinfo("Success", "Settings saved!")
        settings_win.destroy()
    
    tk.Button(settings_win, text="Save Settings", command=save_settings).pack(pady=10)
    tk.Button(settings_win, text="Close", command=settings_win.destroy).pack(pady=5)

# --- Add Menu Bar ---
menu_bar = tk.Menu(root)
settings_menu = tk.Menu(menu_bar, tearoff=0)
settings_menu.add_command(label="Mod Colors...", command=open_settings)
menu_bar.add_cascade(label="Settings", menu=settings_menu)
root.config(menu=menu_bar)

# --- Apply colors at startup ---
load_mod_colors()
load_settings_from_file()
apply_mod_colors()

# --- Start ---
find_game_path_auto()
root.mainloop()