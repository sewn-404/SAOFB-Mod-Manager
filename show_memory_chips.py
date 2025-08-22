import tkinter as tk

def show_memory_chips():
    root = tk.Tk()
    root.title("All Memory Chips")
    root.geometry("900x600")
    text = tk.Text(root, wrap=tk.WORD)
    text.pack(fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(root, command=text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text.config(yscrollcommand=scrollbar.set)

    chips_info = (
        "Weapon Memory Chips\n"
        "This requires having Lisbeth's Weapon Modification Lv. 12. You will need to have completed the base game twice and own all 4 DLCs.\n\n"
        "Soft Cap 15%:\n"
        "  • Weapon Attack: +22.00% (Max Cap)\n"
        "  • Experience Points: +22.00% (Max Cap)\n\n"
        "Soft Cap 20%:\n"
        "  • Physical Attack: +29.50% (Max Cap)\n"
        "  • Optical Attack: +29.50% (Max Cap)\n"
        "  • Explosive Attack: +29.50% (Max Cap)\n"
        "  • Damage vs. Humanoids: +29.50% (Max Cap)\n"
        "  • Damage vs. Lifeforms: +29.50% (Max Cap)\n"
        "  • Damage vs. Mechs: +29.50% (Max Cap)\n"
        "  • Damage at Max HP: +29.50% (Max Cap)\n"
        "  • Weak Spot Damage: +29.50% (Max Cap)\n\n"
        "Soft Cap 25%:\n"
        "  • Debuff Stacking: +37.00% (Max Cap)\n"
        "  • Medal Gauge Increase: +37.00% (Max Cap)\n"
        "  • Effective Range: +37.00% (Max Cap)\n\n"
        "Soft Cap 30%:\n"
        "  • Damage When Off-Guard: +44.50% (Max Cap)\n"
        "  • Damage From Behind: +44.50% (Max Cap)\n"
        "  • Damage When Near Death: +44.50% (Max Cap)\n"
        "  • Critical Damage: +44.50% (Max Cap)\n"
        "  • Critical Rate: +44.50% (Max Cap)\n\n"
        "Soft Cap 50%:\n"
        "  • Auto-Reload Rate: +74.50% (Max Cap)\n"
        "  • Ammo Capacity: +74.50% (Max Cap)\n\n"
        "Soft Cap 75%:\n"
        "  • Bullet Circle Accuracy: +111.00% (Max Cap)\n\n"
        "Soft Cap 100%:\n"
        "  • Bullet Circle Stabilization Speed: +147.50% (Max Cap)\n"
        "  • Trade Value: +147.50% (Max Cap)\n\n"
        "Soft Cap 200%:\n"
        "  • Ammo Acquired: +295.00% (Max Cap)\n\n"
        "Soft Cap 50% (Lower is Better):\n"
        "  • Overheat Buildup & Duration: 27.50% (Max Cap)\n"
        "    This will make you shoot 3.636363 times longer.\n\n"
        "Accessory Memory Chips\n\n"
        "Accessory Name           Max Cap\n"
        "  • STR                  +30\n"
        "  • VIT                  +30\n"
        "  • INT                  +30\n"
        "  • AGI                  +30\n"
        "  • DEX                  +30\n"
        "  • LUC                  +30\n"
        "  • Gadget Attack        +29.50%\n"
        "  • Physical Defense     +18.25%\n"
        "  • Optical Defense      +18.25%\n"
        "  • Explosive Defense    +18.25%\n"
        "  • Melee Defense        +18.25%\n"
        "  • Defense vs. Humanoids+18.25%\n"
        "  • Defense vs. Lifeforms+18.25%\n"
        "  • Defense vs. Mechs    +18.25%\n"
        "  • Blaze Damage         -18.25%\n"
        "  • Poison Damage        -18.25%\n"
        "  • Debuff Resistance    +22.00%\n"
        "  • Debuff Duration      -29.50%\n"
        "  • Blaze Resistance     +29.50%\n"
        "  • Poison Resistance    +29.50%\n"
        "  • Suppression Resistance+29.50%\n"
        "  • Electromagnetic Resistance+29.50%\n"
        "  • HP Recovered Over Time+147.00%\n"
        "  • Max HP               +29.50%\n"
        "  • HP Recovery          +147.50%\n"
        "  • Movement Speed       +14.50%\n"
        "  • Reload Speed         +29.50%\n"
        "  • Avoid Instant Death  +10.00%\n"
        "  • Recharge Time        -22.00%\n"
        "  • Item Drop Rate       +37.00%\n"
        "  • Rare Item Drop Rate  +7.45%\n"
        "  • Weight               -22.00%\n"
        "  • Medals Acquired      +1\n"
        "  • Trade Value          +149.50%\n"
        "  • Experience Points    +22.00%\n"
        "\nThe 0.50% difference between HP Recovered Over Time and HP Recovery is correct.\n"
        "Just do the Party Hero Quests number 16, 17 or 18. They give 300 to all 3 medal types.\n"
        "\nSource: https://steamcommunity.com/sharedfiles/filedetails/?id=1630039266"
    )

    text.insert(tk.END, chips_info)
    text.config(state=tk.DISABLED)
    root.mainloop()

if __name__ == "__main__":
    show_memory_chips()