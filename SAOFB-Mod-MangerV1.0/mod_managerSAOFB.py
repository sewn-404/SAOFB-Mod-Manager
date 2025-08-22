import os
import winreg # This library is used to read the Windows Registry
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# --- Configuration ---
# The Steam App ID for Sword Art Online: Fatal Bullet
STEAM_APP_ID = "626690"
# The name of the game folder in "steamapps/common"
GAME_FOLDER_NAME = "SWORD ART ONLINE FATAL BULLET"
# The relative path from the game's root directory to the mods folder
GAME_MOD_PATH_RELATIVE = "SAOFB\\Content\\Paks\\~mods" 
# The game executable
GAME_EXECUTABLE = "SAOFB.exe"
GAME_PATH = "" # This will be set automatically

# --- File Management Functions ---

def find_steam_paths():
    """Finds all Steam library paths from the Windows Registry and libraryfolders.vdf."""
    paths = []
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam")
        steam_path = winreg.QueryValueEx(reg_key, "InstallPath")[0]
        paths.append(steam_path)
        # Parse libraryfolders.vdf for additional libraries
        vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf_path):
            with open(vdf_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if '"path"' in line:
                        # Extract path value
                        parts = line.split('"')
                        for i, part in enumerate(parts):
                            if part == "path" and i+2 < len(parts):
                                lib_path = parts[i+2].replace("\\\\", "\\")
                                if os.path.exists(lib_path):
                                    paths.append(lib_path)
        # Also check for numbered keys (Steam vdf format)
        if os.path.exists(vdf_path):
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
    return list(set(paths)) # Remove duplicates

def find_game_path_auto():
    """Attempts to automatically find the game's path in all Steam libraries and drives."""
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
    """Prompts the user to select the game's main folder."""
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

# --- Remaining functions (update_mod_lists, enable_mod, disable_mod, launch_game) ---
# These functions remain the same as they were in the previous version.
# You will need to copy and paste them from your original script.
# The only change is that get_game_path() is now split into an automatic and manual function.
# The `select_folder_btn` will need to be updated to call find_game_path_auto()

... # (paste the rest of your code here, including GUI setup)

root = tk.Tk()
root.title("SAOFB Mod Manager")
root.geometry("700x500")  # Set window size to 700x500


# Create the top frame for buttons
frame_top = tk.Frame(root)
frame_top.pack(fill=tk.X, pady=10)

# Status label for feedback
status_label = tk.Label(root, text="Waiting for game path detection...", anchor="w")
status_label.pack(fill=tk.X, padx=10, pady=5)

# Update the button command
select_folder_btn = tk.Button(frame_top, text="Reloade mods Folder", command=find_game_path_auto)
select_folder_btn.pack(side=tk.LEFT, padx=10)


frame_mods = tk.Frame(root)
frame_mods.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

mods_label = tk.Label(frame_mods, text="~mods Folder Contents:")
mods_label.pack(anchor="w")

# Info label about disabled_mods folder location
disabled_info_label = tk.Label(frame_mods, text="Note: Disabled mods are stored in the 'disabled_mods' folder inside the Content folder.", fg="gray", anchor="w")
disabled_info_label.pack(fill=tk.X, padx=2, pady=(0,8))

# Treeview for mod list with colored status
mods_tree = ttk.Treeview(frame_mods, columns=("mod", "status"), show="headings", height=15)
mods_tree.heading("mod", text="Mod File")
mods_tree.heading("status", text="Status")
mods_tree.column("mod", width=400)
mods_tree.column("status", width=100, anchor="center")
mods_tree.pack(fill=tk.BOTH, expand=True)

# Add tag styles for colored status
mods_tree.tag_configure("enabled", foreground="green")
mods_tree.tag_configure("disabled", foreground="red")

def update_mod_lists():
    mods_tree.delete(*mods_tree.get_children())
    mods_path = os.path.join(GAME_PATH, GAME_MOD_PATH_RELATIVE)
    content_folder = os.path.join(GAME_PATH, "SAOFB", "Content")
    disabled_path = os.path.join(content_folder, "disabled_mods")
    pak_mods = []
    disabled_mods = []
    if os.path.exists(mods_path):
        pak_mods = [f for f in os.listdir(mods_path) if f.lower().endswith('.pak') and os.path.isfile(os.path.join(mods_path, f))]
        if not os.path.exists(disabled_path):
            os.makedirs(disabled_path)
        disabled_mods = [f for f in os.listdir(disabled_path) if f.lower().endswith('.pak') and os.path.isfile(os.path.join(disabled_path, f))]
        for mod in pak_mods:
            mods_tree.insert("", "end", values=(mod, "Enabled"), tags=("enabled",))
        for mod in disabled_mods:
            mods_tree.insert("", "end", values=(mod, "Disabled"), tags=("disabled",))
        status_label.config(text=f"Enabled: {len(pak_mods)}, Disabled: {len(disabled_mods)} .pak mods.")
    else:
        status_label.config(text="~mods folder not found.")

def enable_mod():
    selection = mods_tree.selection()
    if not selection:
        messagebox.showinfo("Info", "Select a mod to enable.")
        return
    item = mods_tree.item(selection[0])
    mod_file = item['values'][0]
    status = item['values'][1]
    if status != "Disabled":
        messagebox.showinfo("Info", "Selected mod is already enabled.")
        return
    mods_path = os.path.join(GAME_PATH, GAME_MOD_PATH_RELATIVE)
    content_folder = os.path.join(GAME_PATH, "SAOFB", "Content")
    disabled_path = os.path.join(content_folder, "disabled_mods")
    src = os.path.join(disabled_path, mod_file)
    dst = os.path.join(mods_path, mod_file)
    sig_src = os.path.join(disabled_path, mod_file[:-4] + ".sig")
    sig_dst = os.path.join(mods_path, mod_file[:-4] + ".sig")
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
    if status != "Enabled":
        messagebox.showinfo("Info", "Selected mod is already disabled.")
        return
    mods_path = os.path.join(GAME_PATH, GAME_MOD_PATH_RELATIVE)
    content_folder = os.path.join(GAME_PATH, "SAOFB", "Content")
    disabled_path = os.path.join(content_folder, "disabled_mods")
    src = os.path.join(mods_path, mod_file)
    dst = os.path.join(disabled_path, mod_file)
    sig_src = os.path.join(mods_path, mod_file[:-4] + ".sig")
    sig_dst = os.path.join(disabled_path, mod_file[:-4] + ".sig")
    try:
        shutil.move(src, dst)
        if os.path.exists(sig_src):
            shutil.move(sig_src, sig_dst)
        update_mod_lists()
        status_label.config(text=f"Disabled: {mod_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to disable mod: {e}")


# Enable/Disable buttons
frame_buttons = tk.Frame(root)
frame_buttons.pack(fill=tk.X, padx=10, pady=5)

enable_btn = tk.Button(frame_buttons, text="Enable Selected Mod", command=enable_mod)
enable_btn.pack(side=tk.LEFT, padx=5)

disable_btn = tk.Button(frame_buttons, text="Disable Selected Mod", command=disable_mod)
disable_btn.pack(side=tk.LEFT, padx=5)

# Call the auto-detection function at the start
find_game_path_auto()
root.mainloop()