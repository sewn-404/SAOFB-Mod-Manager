SAOFB Mod Manager V1.5
A specialized terminal-style mod manager for Sword Art Online: Fatal Bullet. Designed to handle both standard .pak mods and LogicMods with a sleek GGO-inspired interface.

🛠️ Installation
Download the SAOFBManagerV1.5.exe from the Files tab.

Place the .exe anywhere (Your desktop or a dedicated tool folder is fine).

Run the application. * Note: On the first launch, it will automatically search for your Steam folder to find where SAOFB is installed.

✨ Main Features
One-Click Toggle: Easily enable or disable mods. The manager automatically creates the necessary ~mods and LogicMods folders for you.

LogicMod Support: Specifically designed to handle the complex folder structures required for LogicMods.

Modpacks: Save your current "Active" list as a pack. Switch between a "Visual Only" setup and a "Gameplay Overhaul" setup in seconds.

Save Insurance: Use the Backup Save button before trying risky mods to ensure your progress is never lost.

Reference Guide: Built-in "Memory Chips" table showing the maximum possible stat rolls for weapons and accessories (Lv12 Lisbeth caps).

Auto-Cleanup: Cleans up "orphan" .sig files that often cause game crashes when mods are deleted manually.

📂 How it Works (Under the Hood)
When you run the manager, it handles the "messy" parts of modding SAOFB:

Registry Detection: It talks to Windows Registry to find your Steam Library—no more hunting for common/SWORD ART ONLINE FATAL BULLET.

File Moving: Instead of deleting files, it moves disabled mods to a disabled_mods folder. This keeps your ~mods folder clean and ensures the game loads faster.

Signature Pairing: Every .pak file in SAOFB needs a .sig file to work. This manager ensures that when you move a mod, its signature tag-along moves with it.

Config Storage: Your settings and modpacks are saved in: %LOCALAPPDATA%\SAOFB\Saved\Config\ModManager This keeps your game folder clean and your settings safe even if you update the manager.

⚠️ Requirements for Max Stats
To see the values shown in the built-in reference tool, your in-game character must have:

Lisbeth's Modification Level 12 (Requires NG+ and DLCs).

All 4 major DLCs installed.

📝 Credits & Technical
Developed by: Sewn404

Framework: Built with Python & CustomTkinter.
