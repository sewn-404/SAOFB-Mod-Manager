import os
import winreg
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
import customtkinter as ctk
import configparser
from datetime import datetime
import json
import re

# --- Appearance & Theme ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- Path Configuration ---
APP_DATA_DIR = os.path.join(
    os.environ["LOCALAPPDATA"], "SAOFB", "Saved", "Config", "ModManager"
)
os.makedirs(APP_DATA_DIR, exist_ok=True)

SETTINGS_FILE = os.path.join(APP_DATA_DIR, "settings.ini")
PACK_DIR = os.path.join(APP_DATA_DIR, "Modpacks")
LANG_FILE = os.path.join(APP_DATA_DIR, "lang.json")
BACKUP_FOLDER = os.path.join(APP_DATA_DIR, "SaveGameBackups")

os.makedirs(PACK_DIR, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# --- Configuration & Globals ---
GAME_FOLDER_NAME = "SWORD ART ONLINE FATAL BULLET"
GAME_MOD_PATH_RELATIVE = "SAOFB\\Content\\Paks\\~mods"
LOGIC_MOD_PATH_RELATIVE = "SAOFB\\Content\\Paks\\LogicMods"
DISABLED_LOGICMOD_PATH_RELATIVE = "SAOFB\\Content\\disabled_LogicMods"
DISABLED_MOD_PATH_RELATIVE = "SAOFB\\Content\\disabled_mods"
GAME_PATH = ""
SAVE_FILE_PATH = os.path.expanduser(r"~\AppData\Local\SAOFB\Saved\SaveGames")

mod_colors = {
    "enabled": "#2ecc71",
    "disabled": "#e74c3c",
    "logicmod": "#3498db",
    "logicmod_disabled": "#9b59b6",
}
current_lang = "en"
lang_data = {}

# --- Language Engine ---
DEFAULT_LANGUAGES = {
    "en": {
        "search": "Search mods...",
        "refresh": "↻ Refresh",
        "enable": "Enable",
        "disable": "Disable",
        "rename": "Rename",
        "delete": "Delete",
        "save_pack": "Save Pack",
        "load_pack": "Load Pack",
        "all": "All",
        "mods": "mods",
        "logic": "LogicMods",
        "settings": "Settings",
        "save": "Saves",
        "backup": "Backup Save",
        "open_backups": "Open Backups",
        "open_config": "Config Folder",
        "info": "ℹ Help",
        "preview": "Color Preview",
        "restart_title": "Restart Required",
        "restart_msg": "Language changed. Restart now to apply?",
        "add_lang": "Add Language",
        "lang_added": "Language added!",
        "edit_translations": "Edit Translations",
        "save_changes": "Save Changes",
        "error_no_name": "Please enter a name for the Modpack!",
        "error_title": "Missing Name",
        "color_settings": "Color Settings",
        "pick_color": "Pick Color",
    }
}


def load_language():
    global lang_data, current_lang
    if not os.path.exists(LANG_FILE):
        with open(LANG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_LANGUAGES, f, indent=4)
        lang_data = DEFAULT_LANGUAGES
    else:
        try:
            with open(LANG_FILE, "r", encoding="utf-8") as f:
                lang_data = json.load(f)
        except:
            lang_data = DEFAULT_LANGUAGES


def t(key):
    return lang_data.get(current_lang, lang_data.get("en", {})).get(key, key)


def load_settings():
    global SAVE_FILE_PATH, current_lang, mod_colors
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
        if "Paths" in config:
            SAVE_FILE_PATH = config["Paths"].get("save_file_path", SAVE_FILE_PATH)
        if "Settings" in config:
            current_lang = config["Settings"].get("language", "en")
        if "Colors" in config:
            for k in mod_colors:
                mod_colors[k] = config["Colors"].get(k, mod_colors[k])


def save_settings_to_file():
    config = configparser.ConfigParser()
    config["Paths"] = {"save_file_path": SAVE_FILE_PATH}
    config["Settings"] = {"language": current_lang}
    config["Colors"] = mod_colors
    with open(SETTINGS_FILE, "w") as f:
        config.write(f)


# --- Help/Info UI ---
class InfoWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Mod Manager Guide")
        self.geometry("700x910")
        self.attributes("-topmost", True)

        ctk.CTkLabel(self, text="Interface Guide", font=("Roboto", 22, "bold")).pack(
            pady=20
        )
        frame = ctk.CTkScrollableFrame(self, width=540, height=580)
        frame.pack(padx=20, pady=10, fill="both", expand=True)

        sections = [
            (
                "Top Bar",
                "• Search: Filters the list by filename.\n• Refresh: Rescans game folders.\n• Filters: Only shows specific mod types.",
            ),
            (
                "Mod List",
                "• Green: Active .pak mods.\n• Red: Disabled mods.\n• Blue: LogicMods.\n• Purple: Disabled LogicMods.",
            ),
            (
                "Action Buttons",
                "• Enable/Disable: Moves files between folders.\n• Rename: Changes the .pak filename.\n• Delete: Removes file permanently.",
            ),
            (
                "Modpacks",
                "• Save Pack: Saves current active mods list.\n• Load Pack: Restores a saved list.",
            ),
            ("Footer", "• Backup Save: Creates a dated copy of your save data."),
        ]
        for title, content in sections:
            ctk.CTkLabel(
                frame, text=title, font=("", 15, "bold"), text_color="#3498db"
            ).pack(anchor="w", pady=(10, 0))
            ctk.CTkLabel(frame, text=content, justify="left", font=("", 12)).pack(
                anchor="w", padx=10, pady=(0, 10)
            )


# --- Memory Chips UI ---
class MemoryChipsApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("SAOFB Memory Chips Reference")
        self.geometry("850x850")
        self.attributes("-topmost", True)

        ctk.CTkLabel(
            self, text="Memory Chip Maximum Caps", font=("Roboto", 24, "bold")
        ).pack(pady=20)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        self.tab_weapons = self.tabview.add("Weapon Chips")
        self.tab_accessories = self.tabview.add("Accessory Chips")
        self.tab_info = self.tabview.add("Requirements & Tips")

        self.setup_weapon_tab()
        self.setup_accessory_tab()
        self.setup_info_tab()

    def setup_weapon_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_weapons)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Categorized by Soft Cap Percentage exactly as in the source
        weapon_data = [
            (
                "Soft Cap 15%",
                [("Weapon Attack", "+22.00%"), ("Experience Points", "+22.00%")],
            ),
            (
                "Soft Cap 20%",
                [
                    ("Physical Attack", "+29.50%"),
                    ("Optical Attack", "+29.50%"),
                    ("Explosive Attack", "+29.50%"),
                    ("Damage vs. Humanoids", "+29.50%"),
                    ("Damage vs. Lifeforms", "+29.50%"),
                    ("Damage vs. Mechs", "+29.50%"),
                    ("Damage at Max HP", "+29.50%"),
                    ("Weak Spot Damage", "+29.50%"),
                ],
            ),
            (
                "Soft Cap 25%",
                [
                    ("Debuff Stacking", "+37.00%"),
                    ("Medal Gauge Increase", "+37.00%"),
                    ("Effective Range", "+37.00%"),
                ],
            ),
            (
                "Soft Cap 30%",
                [
                    ("Damage When Off-Guard", "+44.50%"),
                    ("Damage From Behind", "+44.50%"),
                    ("Damage When Near Death", "+44.50%"),
                    ("Critical Damage", "+44.50%"),
                    ("Critical Rate", "+44.50%"),
                ],
            ),
            (
                "Soft Cap 50%",
                [("Auto-Reload Rate", "+74.50%"), ("Ammo Capacity", "+74.50%")],
            ),
            ("Soft Cap 75%", [("Bullet Circle Accuracy", "+111.00%")]),
            (
                "Soft Cap 100%",
                [
                    ("Bullet Circle Stabilization Speed", "+147.50%"),
                    ("Trade Value", "+147.50%"),
                ],
            ),
            ("Soft Cap 200%", [("Ammo Acquired", "+295.00%")]),
            (
                "Soft Cap 50% (Lower is Better)",
                [("Overheat Buildup & Duration", "27.50%")],
            ),
        ]

        for section, chips in weapon_data:
            ctk.CTkLabel(
                frame, text=section, font=("", 16, "bold"), text_color="#3498db"
            ).pack(anchor="w", pady=(15, 5))
            for name, cap in chips:
                f = ctk.CTkFrame(frame, fg_color="#2b2b2b")
                f.pack(fill="x", pady=2, padx=5)
                ctk.CTkLabel(f, text=name, anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(
                    f, text=cap, text_color="#2ecc71", font=("", 12, "bold")
                ).pack(side="right", padx=10)

    def setup_accessory_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_accessories)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Categorized Logic for clearer UI, but contains ALL data from source
        acc_data = [
            ("Stats", [("STR / VIT / INT / AGI / DEX / LUC", "+30")]),
            (
                "Offense & Defense",
                [
                    ("Gadget Attack", "+29.50%"),
                    ("Physical Defense", "+18.25%"),
                    ("Optical Defense", "+18.25%"),
                    ("Explosive Defense", "+18.25%"),
                    ("Melee Defense", "+18.25%"),
                    ("Defense vs. Humanoids", "+18.25%"),
                    ("Defense vs. Lifeforms", "+18.25%"),
                    ("Defense vs. Mechs", "+18.25%"),
                ],
            ),
            (
                "Resistances",
                [
                    ("Blaze Damage", "-18.25%"),
                    ("Poison Damage", "-18.25%"),
                    ("Debuff Resistance", "+22.00%"),
                    ("Debuff Duration", "-29.50%"),
                    ("Blaze Resistance", "+29.50%"),
                    ("Poison Resistance", "+29.50%"),
                    ("Suppression Resistance", "+29.50%"),
                    ("Electromagnetic Resistance", "+29.50%"),
                ],
            ),
            (
                "Recovery & Utility",
                [
                    ("HP Recovered Over Time", "+147.00%"),
                    ("HP Recovery", "+147.50%"),
                    ("Max HP", "+29.50%"),
                    ("Movement Speed", "+14.50%"),
                    ("Reload Speed", "+29.50%"),
                    ("Avoid Instant Death", "+10.00%"),
                    ("Recharge Time", "-22.00%"),
                    ("Weight", "-22.00%"),
                ],
            ),
            (
                "Loot & Rewards",
                [
                    ("Item Drop Rate", "+37.00%"),
                    ("Rare Item Drop Rate", "+7.45%"),
                    ("Medals Acquired", "+1"),
                    ("Trade Value", "+149.50%"),
                    ("Experience Points", "+22.00%"),
                ],
            ),
        ]

        for section, chips in acc_data:
            ctk.CTkLabel(
                frame, text=section, font=("", 16, "bold"), text_color="#e67e22"
            ).pack(anchor="w", pady=(15, 5))
            for name, cap in chips:
                f = ctk.CTkFrame(frame, fg_color="#2b2b2b")
                f.pack(fill="x", pady=2, padx=5)
                ctk.CTkLabel(f, text=name, anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(
                    f, text=cap, text_color="#2ecc71", font=("", 12, "bold")
                ).pack(side="right", padx=10)

    def setup_info_tab(self):
        info_text = (
            "Requirements for Max Caps:\n"
            "• Unlock Lisbeth's Weapon Modification Lv. 12.\n"
            "• Complete the base game twice (Normal + NG+).\n"
            "• Own all 4 DLCs.\n\n"
            "Important Notes:\n"
            "• The 0.50% difference between 'HP Recovered Over Time' (147.00%) and 'HP Recovery' (147.50%) is correct.\n"
            "• 'Overheat Buildup & Duration' makes you shoot ~3.6x longer.\n\n"
            "Farming Tip:\n"
            "• For Medals: Run Party Hero Quests 16, 17, or 18. They give 300 to all 3 medal types.\n"
            "\nSource: Steam Community Guide (1630039266)"
        )
        ctk.CTkLabel(self.tab_info, text=info_text, justify="left", font=("", 14)).pack(
            padx=20, pady=20, anchor="nw"
        )


# --- Main Application ---
class ModManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        load_language()
        self.title(f"SAOFB Mod Manager - V1.8 [{current_lang.upper()}]")
        self.geometry("1300x920")
        self.configure(fg_color="#1a1a1a")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=30,
            borderwidth=0,
        )
        self.style.map("Treeview", background=[("selected", "#1f538d")])

        self.setup_ui()

    def setup_ui(self):
        # SAOFB Color Palette
        SAO_BLUE = "#00d2ff"  # Das typische GGO Cyan
        SAO_DARK = "#0d1117"  # Tiefer Hintergrund
        SAO_SIDEBAR = "#161b22"  # Sidebar-Kontrast
        SAO_BTN_HOVER = "#005f73"  # Dunkleres Cyan für Hover

        # --- Root Grid Configuration ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Main Content Wrapper
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nsew")

        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (SAOFB Style) ---
        self.sidebar = ctk.CTkScrollableFrame(
            self.main_frame,
            width=240,
            fg_color=SAO_SIDEBAR,
            border_color=SAO_BLUE,
            border_width=1,
        )
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        # Sektion: Suche
        ctk.CTkLabel(
            self.sidebar,
            text="SEARCH",
            text_color=SAO_BLUE,
            font=("Roboto", 10, "bold"),
        ).pack(pady=(10, 0))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_list())
        ctk.CTkEntry(
            self.sidebar,
            textvariable=self.search_var,
            placeholder_text=t("search"),
            border_color=SAO_BLUE,
        ).pack(fill="x", padx=10, pady=5)

        # Sektion: Navigation
        ctk.CTkLabel(
            self.sidebar,
            text="NAVIGATION",
            text_color=SAO_BLUE,
            font=("Roboto", 10, "bold"),
        ).pack(pady=(15, 0))
        ctk.CTkButton(
            self.sidebar,
            text=t("info"),
            fg_color="#8e44ad",
            hover_color="#732d91",
            command=lambda: InfoWindow(self),
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar,
            text=t("refresh"),
            fg_color=SAO_BLUE,
            text_color="black",
            hover_color=SAO_BTN_HOVER,
            command=self.refresh_list,
        ).pack(fill="x", padx=10, pady=2)

        self.filter_mode = ctk.StringVar(value="all")
        for text, mode in [
            ("All Mods", "all"),
            ("Logic Mods", "logic"),
            ("Standard Mods", "mods"),
        ]:
            ctk.CTkButton(
                self.sidebar,
                text=text,
                border_width=1,
                border_color=SAO_BLUE,
                fg_color="transparent",
                hover_color=SAO_BTN_HOVER,
                command=lambda m=mode: self.set_filter(m),
                height=32,
            ).pack(fill="x", padx=10, pady=2)

        # Sektion: Status Filter
        ctk.CTkLabel(
            self.sidebar,
            text="STATUS FILTER",
            text_color=SAO_BLUE,
            font=("Roboto", 10, "bold"),
        ).pack(pady=(15, 0))
        self.show_active_only = ctk.BooleanVar(value=False)
        self.show_disabled_only = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.sidebar,
            text="Active Only",
            checkmark_color=SAO_BLUE,
            variable=self.show_active_only,
            command=self.refresh_list,
        ).pack(anchor="w", padx=15, pady=2)
        ctk.CTkCheckBox(
            self.sidebar,
            text="Disabled Only",
            checkmark_color=SAO_BLUE,
            variable=self.show_disabled_only,
            command=self.refresh_list,
        ).pack(anchor="w", padx=15, pady=2)

        # Sektion: Mod Aktionen
        ctk.CTkLabel(
            self.sidebar,
            text="ACTIONS",
            text_color=SAO_BLUE,
            font=("Roboto", 10, "bold"),
        ).pack(pady=(20, 0))
        ctk.CTkButton(
            self.sidebar,
            text=t("enable"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            text_color="black",
            command=lambda: self.move_mod(True),
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar,
            text=t("disable"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            text_color="white",
            command=lambda: self.move_mod(False),
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar,
            text="➕ Add Mod",
            fg_color="#1abc9c",
            text_color="black",
            command=self.add_mod,
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar,
            text=t("rename"),
            border_width=1,
            border_color=SAO_BLUE,
            fg_color="transparent",
            command=self.rename_mod,
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar, text=t("delete"), fg_color="#c0392b", command=self.delete_mod
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar,
            text="🧹 Cleanup",
            fg_color="#f39c12",
            text_color="black",
            command=self.cleanup_orphans,
        ).pack(fill="x", padx=10, pady=2)

        # Sektion: Management
        ctk.CTkLabel(
            self.sidebar,
            text="MANAGEMENT",
            text_color=SAO_BLUE,
            font=("Roboto", 10, "bold"),
        ).pack(pady=(20, 0))
        ctk.CTkButton(
            self.sidebar,
            text="💾 " + t("save_pack"),
            fg_color="#3498db",
            command=self.create_modpack_ui,
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar,
            text="📂 " + t("load_pack"),
            fg_color="#2980b9",
            command=self.load_modpack_ui,
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar,
            text="💎 Memory Chips",
            fg_color=SAO_BLUE,
            text_color="black",
            hover_color=SAO_BTN_HOVER,
            command=lambda: MemoryChipsApp(self),
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar,
            text="📁 Open Mods Folder",
            border_width=1,
            fg_color="transparent",
            border_color=SAO_BLUE,
            command=lambda: self.open_path(GAME_MOD_PATH_RELATIVE),
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar,
            text="⚙ Open Config Folder",
            border_width=1,
            fg_color="transparent",
            border_color=SAO_BLUE,
            command=lambda: os.startfile(APP_DATA_DIR),
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar,
            text="🛡 Backup Save",
            fg_color="#16a085",
            text_color="black",
            command=self.backup_saves,
        ).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(
            self.sidebar,
            text="🔧 Settings",
            border_width=1,
            fg_color="transparent",
            border_color=SAO_BLUE,
            command=self.open_settings_win,
        ).pack(fill="x", padx=10, pady=2)

        # Sektion: Game Launch
        ctk.CTkLabel(
            self.sidebar, text="GAME", text_color=SAO_BLUE, font=("Roboto", 10, "bold")
        ).pack(pady=(20, 0))
        ctk.CTkButton(
            self.sidebar,
            text="▶ LAUNCH GAME",
            fg_color=SAO_BLUE,
            text_color="black",
            hover_color=SAO_BTN_HOVER,
            height=45,
            font=("Roboto", 13, "bold"),
            command=self.launch_game,
        ).pack(fill="x", padx=10, pady=(5, 20))

        # --- TREEVIEW (SAOFB Dark Style) ---
        self.tree_frame = ctk.CTkFrame(
            self.main_frame, fg_color=SAO_DARK, border_color=SAO_BLUE, border_width=1
        )
        self.tree_frame.grid(row=0, column=1, sticky="nsew")

        # Customizing the TTK Treeview colors via style
        self.style.configure(
            "Treeview",
            background=SAO_DARK,
            foreground="white",
            fieldbackground=SAO_DARK,
            borderwidth=0,
        )
        self.style.configure(
            "Treeview.Heading",
            background=SAO_SIDEBAR,
            foreground=SAO_BLUE,
            font=("Roboto", 10, "bold"),
        )

        self.mods_tree = ttk.Treeview(
            self.tree_frame,
            columns=("mod", "status", "type"),
            show="headings",
            style="Treeview",
        )
        self.mods_tree.heading("mod", text="FILE")
        self.mods_tree.column("mod", width=650)
        self.mods_tree.heading("status", text="STATUS")
        self.mods_tree.column("status", width=120)
        self.mods_tree.heading("type", text="TYPE")
        self.mods_tree.column("type", width=120)
        self.mods_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            self.tree_frame,
            fg_color=SAO_SIDEBAR,
            button_color=SAO_BLUE,
            button_hover_color=SAO_BTN_HOVER,
            command=self.mods_tree.yview,
        )
        scrollbar.pack(side="right", fill="y")
        self.mods_tree.configure(yscrollcommand=scrollbar.set)

        # --- STATUS BAR ---
        self.status_label = ctk.CTkLabel(
            self, text="Ready", text_color=SAO_BLUE, anchor="w"
        )
        self.status_label.grid(row=1, column=0, padx=30, pady=(5, 10), sticky="sw")

    def get_type_paths(self, t_type):
        if t_type == "Mod":
            return (
                os.path.join(GAME_PATH, GAME_MOD_PATH_RELATIVE),
                os.path.join(GAME_PATH, DISABLED_MOD_PATH_RELATIVE),
            )
        return (
            os.path.join(GAME_PATH, LOGIC_MOD_PATH_RELATIVE),
            os.path.join(GAME_PATH, DISABLED_LOGICMOD_PATH_RELATIVE),
        )

    def refresh_list(self):
        self.mods_tree.delete(*self.mods_tree.get_children())
        if not GAME_PATH:
            return
        search = self.search_var.get().lower()
        row_index = 0
        paths = {
            "m": (
                os.path.join(GAME_PATH, GAME_MOD_PATH_RELATIVE),
                "Mod",
                "enabled",
                True,
            ),
            "dm": (
                os.path.join(GAME_PATH, DISABLED_MOD_PATH_RELATIVE),
                "Mod",
                "disabled",
                False,
            ),
            "l": (
                os.path.join(GAME_PATH, LOGIC_MOD_PATH_RELATIVE),
                "LogicMod",
                "logicmod",
                True,
            ),
            "dl": (
                os.path.join(GAME_PATH, DISABLED_LOGICMOD_PATH_RELATIVE),
                "LogicMod",
                "logicmod_disabled",
                False,
            ),
        }
        for _, (p, m_type, color_tag, is_active) in paths.items():
            if self.filter_mode.get() == "mods" and m_type != "Mod":
                continue
            if self.filter_mode.get() == "logic" and m_type != "LogicMod":
                continue
            if self.show_active_only.get() and not is_active:
                continue
            if self.show_disabled_only.get() and is_active:
                continue
            if not os.path.exists(p):
                continue
            for f in os.listdir(p):
                if not f.lower().endswith(".pak"):
                    continue
                if search and search not in f.lower():
                    continue
                status = "Active" if is_active else "Off"
                zebra = "even" if row_index % 2 == 0 else "odd"
                self.mods_tree.insert(
                    "",
                    "end",
                    values=(f, status, m_type),
                    tags=(zebra, color_tag),
                )
                row_index += 1
                for t_tag, color in mod_colors.items():
                    self.mods_tree.tag_configure(t_tag, foreground=color)
                    self.status_label.configure(
                        text=f"Showing {row_index} mods", text_color="#95a5a6"
                    )

    def move_mod(self, to_enable):
        for item in self.mods_tree.selection():
            f, s, t_type = self.mods_tree.item(item)["values"]
            active, disabled = self.get_type_paths(t_type)
            src, dst = (disabled, active) if to_enable else (active, disabled)
            if os.path.exists(os.path.join(src, f)):
                os.makedirs(dst, exist_ok=True)
                shutil.move(os.path.join(src, f), os.path.join(dst, f))
                sig = f.replace(".pak", ".sig")
                if os.path.exists(os.path.join(src, sig)):
                    shutil.move(os.path.join(src, sig), os.path.join(dst, sig))
        self.refresh_list()

    def rename_mod(self):
        sel = self.mods_tree.selection()
        if not sel:
            return
        old_f, s, t_type = self.mods_tree.item(sel[0])["values"]
        new = ctk.CTkInputDialog(text="New Name:", title="Rename").get_input()
        if new:
            active, disabled = self.get_type_paths(t_type)
            d = active if s == "Active" else disabled
            new_f = new.replace(".pak", "") + ".pak"
            if os.path.exists(os.path.join(d, old_f)):
                os.rename(os.path.join(d, old_f), os.path.join(d, new_f))
                osig, nsig = old_f.replace(".pak", ".sig"), new_f.replace(
                    ".pak", ".sig"
                )
                if os.path.exists(os.path.join(d, osig)):
                    os.rename(os.path.join(d, osig), os.path.join(d, nsig))
            self.refresh_list()

    def delete_mod(self):
        sel = self.mods_tree.selection()
        if not sel:
            return
        f, s, t_type = self.mods_tree.item(sel[0])["values"]
        if messagebox.askyesno("Delete", f"Delete {f} and .sig?"):
            active, disabled = self.get_type_paths(t_type)
            d = active if s == "Active" else disabled
            if os.path.exists(os.path.join(d, f)):
                os.remove(os.path.join(d, f))
            sig = f.replace(".pak", ".sig")
            if os.path.exists(os.path.join(d, sig)):
                os.remove(os.path.join(d, sig))
            self.refresh_list()

    def add_mod(self):
        files = filedialog.askopenfilenames(
            title="Select Mod Files", filetypes=[("PAK and SIG Files", "*.pak *.sig")]
        )
        if not files:
            return

        mod_dir = os.path.join(GAME_PATH, GAME_MOD_PATH_RELATIVE)
        os.makedirs(mod_dir, exist_ok=True)

        for f in files:
            shutil.copy(f, mod_dir)

        self.status_label.configure(
            text="Mod(s) added successfully.", text_color="#2ecc71"
        )
        self.refresh_list()

    def launch_game(self):
        if not GAME_PATH:
            messagebox.showerror("Error", "Game path not found.")
            return

        exe = os.path.join(
            GAME_PATH, "SAOFB", "Binaries", "Win64", "SAOFB-Win64-Shipping.exe"
        )
        if os.path.exists(exe):
            os.startfile(exe)
            self.status_label.configure(text="Launching game...", text_color="#3498db")
        else:
            messagebox.showerror("Error", "Game executable not found.")

    def cleanup_orphans(self):
        if not GAME_PATH:
            return

        folders = [
            GAME_MOD_PATH_RELATIVE,
            DISABLED_MOD_PATH_RELATIVE,
            LOGIC_MOD_PATH_RELATIVE,
            DISABLED_LOGICMOD_PATH_RELATIVE,
        ]

        removed = 0

        for rel in folders:
            full = os.path.join(GAME_PATH, rel)
            if not os.path.exists(full):
                continue

            files = os.listdir(full)
            paks = {f[:-4] for f in files if f.lower().endswith(".pak")}
            sigs = {f[:-4] for f in files if f.lower().endswith(".sig")}

            for name in sigs - paks:
                os.remove(os.path.join(full, name + ".sig"))
                removed += 1

            for name in paks - sigs:
                os.remove(os.path.join(full, name + ".pak"))
                removed += 1

        messagebox.showinfo("Cleanup Complete", f"Removed {removed} orphaned files.")
        self.refresh_list()

    def create_modpack_ui(self):
        name = ctk.CTkInputDialog(text="Pack Name:", title=t("save_pack")).get_input()
        if not name:
            return
        pack_data = {"mods": []}
        for child in self.mods_tree.get_children():
            f, s, t_type = self.mods_tree.item(child)["values"]
            pack_data["mods"].append(
                {"file": f, "active": (s == "Active"), "type": t_type}
            )
        with open(os.path.join(PACK_DIR, f"{name}.json"), "w") as f:
            json.dump(pack_data, f, indent=4)
        messagebox.showinfo("Success", f"Pack '{name}' saved.")

    def load_modpack_ui(self):
        files = [f for f in os.listdir(PACK_DIR) if f.endswith(".json")]
        if not files:
            messagebox.showinfo("Info", "No packs found.")
            return
        win = ctk.CTkToplevel(self)
        win.title(t("load_pack"))
        win.geometry("300x400")
        win.attributes("-topmost", True)
        win.grab_set()
        lb = tk.Listbox(win, bg="#2b2b2b", fg="white")
        lb.pack(fill="both", expand=True, padx=10, pady=10)
        for f in files:
            lb.insert("end", f.replace(".json", ""))

        def apply():
            sel = lb.curselection()
            if not sel:
                return
            with open(os.path.join(PACK_DIR, f"{lb.get(sel[0])}.json"), "r") as f:
                data = json.load(f)
            for m in data["mods"]:
                active, disabled = self.get_type_paths(m["type"])
                src = disabled if m["active"] else active
                dst = active if m["active"] else disabled
                for ext in [".pak", ".sig"]:
                    fname = m["file"].replace(".pak", ext)
                    if os.path.exists(os.path.join(src, fname)):
                        os.makedirs(dst, exist_ok=True)
                        shutil.move(os.path.join(src, fname), os.path.join(dst, fname))
            self.refresh_list()
            win.destroy()

        ctk.CTkButton(win, text="Apply", command=apply).pack(pady=10)

    def backup_saves(self):
        if not os.path.exists(SAVE_FILE_PATH):
            return
        dst = os.path.join(
            BACKUP_FOLDER, f"Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copytree(SAVE_FILE_PATH, dst)
        messagebox.showinfo("Backup", f"Saves backed up to {dst}")

    def open_settings_win(self):
        win = ctk.CTkToplevel(self)
        win.title(t("settings"))
        win.geometry("650x850")
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text=t("color_settings"), font=("", 16, "bold")).pack(pady=10)
        color_frame = ctk.CTkFrame(win)
        color_frame.pack(fill="x", padx=20, pady=5)

        def pick(k, lbl):
            c = colorchooser.askcolor(initialcolor=mod_colors[k])[1]
            if c:
                mod_colors[k] = c
                lbl.configure(text_color=c)
                self.mods_tree.tag_configure(k, foreground=c)

        opts = [
            ("Enabled Mod", "enabled"),
            ("Disabled Mod", "disabled"),
            ("LogicMod", "logicmod"),
            ("LogicMod Off", "logicmod_disabled"),
        ]
        for i, (label, key) in enumerate(opts):
            row = ctk.CTkFrame(color_frame)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, width=150).pack(side="left", padx=10)
            p_lbl = ctk.CTkLabel(
                row,
                text="Preview.pak",
                text_color=mod_colors[key],
                font=("", 12, "bold"),
            )
            p_lbl.pack(side="left", padx=10)
            ctk.CTkButton(
                row, text="Pick", width=80, command=lambda k=key, l=p_lbl: pick(k, l)
            ).pack(side="right", padx=10)

        ctk.CTkLabel(win, text=f"{t('save')} Path:").pack(pady=(20, 0))
        path_var = ctk.StringVar(value=SAVE_FILE_PATH)
        ctk.CTkEntry(win, textvariable=path_var, width=450).pack(pady=5)

        ctk.CTkLabel(win, text="Language Selection:").pack(pady=(10, 0))
        lang_var = ctk.StringVar(value=current_lang)
        ctk.CTkOptionMenu(win, values=list(lang_data.keys()), variable=lang_var).pack(
            pady=5
        )

        ctk.CTkButton(win, text=t("add_lang"), command=self.add_new_lang_ui).pack(
            pady=5
        )
        ctk.CTkButton(
            win,
            text=t("edit_translations"),
            command=lambda: self.open_translation_editor(lang_var.get()),
        ).pack(pady=5)

        def save_all():
            global current_lang, SAVE_FILE_PATH
            lang_changed = current_lang != lang_var.get()
            current_lang, SAVE_FILE_PATH = lang_var.get(), path_var.get()
            save_settings_to_file()
            if lang_changed:
                if messagebox.askyesno(t("restart_title"), t("restart_msg")):
                    os.execl(sys.executable, sys.executable, *sys.argv)
            self.refresh_list()
            win.destroy()

        ctk.CTkButton(
            win, text="Save & Apply", fg_color="#2ecc71", command=save_all
        ).pack(pady=30)

    def add_new_lang_ui(self):
        code = ctk.CTkInputDialog(text="Code:", title=t("add_lang")).get_input()
        if code and code not in lang_data:
            lang_data[code] = lang_data.get("en", {}).copy()
            with open(LANG_FILE, "w", encoding="utf-8") as f:
                json.dump(lang_data, f, indent=4)
            messagebox.showinfo("Success", t("lang_added"))

    def open_translation_editor(self, lang_code):
        editor = ctk.CTkToplevel(self)
        editor.title(f"Editing: {lang_code}")
        editor.geometry("600x700")
        scroll = ctk.CTkScrollableFrame(editor)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        entries = {}
        for key, value in lang_data.get(lang_code, lang_data["en"]).items():
            row = ctk.CTkFrame(scroll)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=key, width=150, anchor="w").pack(side="left", padx=5)
            ent = ctk.CTkEntry(row, width=350)
            ent.insert(0, value)
            ent.pack(side="left", padx=5)
            entries[key] = ent

        def save():
            for k, e in entries.items():
                lang_data[lang_code][k] = e.get()
            with open(LANG_FILE, "w", encoding="utf-8") as f:
                json.dump(lang_data, f, indent=4)
            editor.destroy()

        ctk.CTkButton(
            editor, text=t("save_changes"), fg_color="#2ecc71", command=save
        ).pack(pady=10)

    def open_path(self, p):
        if GAME_PATH:
            os.startfile(os.path.join(GAME_PATH, p))

    def set_filter(self, m):
        self.filter_mode.set(m)
        self.refresh_list()


def find_game_path_auto(app_instance):
    global GAME_PATH
    try:
        reg = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"
        )
        steam_p = winreg.QueryValueEx(reg, "InstallPath")[0]
        vdf = os.path.join(steam_p, "steamapps", "libraryfolders.vdf")
        libs = [steam_p]
        if os.path.exists(vdf):
            with open(vdf, "r") as f:
                libs.extend(
                    [
                        m.replace("\\\\", "\\")
                        for m in re.findall(r'"path"\s+"([^"]+)"', f.read())
                    ]
                )
        for p in set(libs):
            gp = os.path.join(p, "steamapps", "common", GAME_FOLDER_NAME)
            if os.path.exists(os.path.join(gp, "SAOFB")):
                GAME_PATH = gp
                app_instance.status_label.configure(
                    text=f"Path Found: {gp}", text_color="#2ecc71"
                )
                app_instance.refresh_list()
                return
    except:
        app_instance.status_label.configure(
            text="Game path not found. Check Steam.", text_color="#e74c3c"
        )


if __name__ == "__main__":
    load_settings()
    app = ModManager()
    find_game_path_auto(app)
    app.mainloop()
