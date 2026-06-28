# skill.py

skills = {

    # =========================
    # LUFFY (Gear System)
    # =========================
    "Monkey D. Luffy": {
        "Base": [
            {"name": "Gomu Gomu no Pistol", "damage": 60},
            {"name": "Gomu Gomu no Bazooka", "damage": 90},
            {"name": "Gomu Gomu no Whip", "damage": 70},
            {"name": "Haki Punch", "damage": 100},
        ],
        "Gear 2": [
            {"name": "Jet Pistol", "damage": 110},
            {"name": "Jet Stamp", "damage": 120},
            {"name": "Jet Bazooka", "damage": 140},
            {"name": "Soru Rush", "damage": 130},
        ],
        "Gear 4 Boundman": [
            {"name": "Kong Gun", "damage": 170},
            {"name": "Leo Bazooka", "damage": 180},
            {"name": "Black Mamba", "damage": 190},
            {"name": "King Kong Gun", "damage": 210},
        ],
        "Gear 5": [
            {"name": "Dawn Rocket", "damage": 220},
            {"name": "Gomu Gomu no Fusen World", "damage": 230},
            {"name": "Toon Smash", "damage": 240},
            {"name": "Sun God Wrath", "damage": 260},
        ]
    },

    # =========================
    # ZORO (3 Sword Style)
    # =========================
    "Roronoa Zoro": {
        "Base": [
            {"name": "Onigiri", "damage": 80},
            {"name": "Tatsumaki", "damage": 90},
            {"name": "Iai Slash", "damage": 85},
        ],
        "Asura": [
            {"name": "Asura Ichibugin", "damage": 150},
            {"name": "Asura Bakkei", "damage": 170},
            {"name": "Nine Sword Style", "damage": 190},
        ],
        "King of Hell": [
            {"name": "Enma Release", "damage": 200},
            {"name": "Hellfire Oni Giri", "damage": 210},
            {"name": "King of Hell Three Dragons", "damage": 230},
        ]
    },

    # =========================
    # SANJI
    # =========================
    "Vinsmoke Sanji": {
        "Base": [
            {"name": "Diable Jambe", "damage": 90},
            {"name": "Collier Strike", "damage": 85},
            {"name": "Concassé", "damage": 95},
        ],
        "Ifrit Jambe": [
            {"name": "Hell Memories", "damage": 160},
            {"name": "Ifrit Sky Kick", "damage": 170},
            {"name": "Blue Flame Storm", "damage": 180},
        ]
    },

    # =========================
    # KATAKURI
    # =========================
    "Charlotte Katakuri": {
        "Base": [
            {"name": "Mochi Spear", "damage": 90},
            {"name": "Power Mochi", "damage": 110},
            {"name": "Buzz Cut Mochi", "damage": 120},
        ],
        "Awakening": [
            {"name": "Mochi Domain", "damage": 160},
            {"name": "Future Sight Trap", "damage": 0},
            {"name": "Piercing Mochi Rain", "damage": 180},
        ]
    },

    # =========================
    # MARCO
    # =========================
    "Marco": {
        "Base": [
            {"name": "Phoenix Kick", "damage": 80},
            {"name": "Blue Flame Shot", "damage": 85},
        ],
        "Phoenix Form": [
            {"name": "Regeneration Aura", "damage": 0},
            {"name": "Phoenix Dive", "damage": 150},
            {"name": "Immortal Wings", "damage": 0},
        ]
    },

    # =========================
    # YAMATO
    # =========================
    "Yamato": {
        "Base": [
            {"name": "Thunder Bagua", "damage": 120},
            {"name": "Ice Strike", "damage": 100},
        ],
        "Hybrid Form": [
            {"name": "Divine Wolf Claw", "damage": 170},
            {"name": "Ice Thunder Crash", "damage": 180},
        ]
    },

    # =========================
    # ODEN
    # =========================
    "Kozuki Oden": {
        "Base": [
            {"name": "Oden Two Sword Style", "damage": 150},
            {"name": "Paradise Totsuka", "damage": 160},
        ],
        "Legend Form": [
            {"name": "Oden Sword Domain", "damage": 200},
            {"name": "Divine Execution", "damage": 220},
        ]
    },

    # =========================
    # RAYLEIGH
    # =========================
    "Silvers Rayleigh": {
        "Base": [
            {"name": "Haki Slash", "damage": 120},
            {"name": "Coating Strike", "damage": 130},
        ],
        "Dark King Mode": [
            {"name": "Conqueror Burst", "damage": 180},
            {"name": "King's Silence", "damage": 190},
        ]
    },

    # =========================
    # MIHAWK
    # =========================
    "Dracule Mihawk": {
        "Base": [
            {"name": "Black Blade Slash", "damage": 140},
            {"name": "Moon Cut", "damage": 150},
        ],
        "World's Strongest Form": [
            {"name": "Dimension Slash", "damage": 210},
            {"name": "Night King Cut", "damage": 220},
        ]
    },

    # =========================
    # GARP
    # =========================
    "Monkey D. Garp": {
        "Base": [
            {"name": "Galaxy Punch", "damage": 150},
            {"name": "Meteor Fist", "damage": 160},
        ],
        "Hero Mode": [
            {"name": "Destroyer Punch", "damage": 200},
            {"name": "Marine Justice", "damage": 220},
        ]
    },

    # =========================
    # ADMIRALS
    # =========================
    "Akainu": {
        "Base": [
            {"name": "Magma Punch", "damage": 140},
            {"name": "Lava Burst", "damage": 150},
        ],
        "Awakened": [
            {"name": "Hell Eruption", "damage": 210},
            {"name": "Volcanic Judgment", "damage": 230},
        ]
    },

    "Aokiji": {
        "Base": [
            {"name": "Ice Spear", "damage": 130},
            {"name": "Ice Wall", "damage": 140},
        ],
        "Awakened": [
            {"name": "Ice Age", "damage": 210},
            {"name": "Absolute Zero Prison", "damage": 220},
        ]
    },

    "Kizaru": {
        "Base": [
            {"name": "Light Kick", "damage": 130},
            {"name": "Photon Shot", "damage": 140},
        ],
        "Awakened": [
            {"name": "Yasakani Barrage", "damage": 210},
            {"name": "Light Speed Annihilation", "damage": 230},
        ]
    },

    "Fujitora": {
        "Base": [
            {"name": "Gravity Push", "damage": 120},
            {"name": "Meteor Pull", "damage": 140},
        ],
        "Awakened": [
            {"name": "Planet Crush", "damage": 220},
            {"name": "Gravity Collapse", "damage": 240},
        ]
    },

    "Greenbull": {
        "Base": [
            {"name": "Root Drain", "damage": 110},
            {"name": "Wood Bind", "damage": 120},
        ],
        "Awakened": [
            {"name": "Forest Dominion", "damage": 200},
            {"name": "Nature Extinction", "damage": 220},
        ]
    },

    # =========================
    # SHANKS
    # =========================
    "Shanks": {
        "Base": [
            {"name": "Conqueror Slash", "damage": 160},
            {"name": "Sword Draw", "damage": 150},
        ],
        "Haki Form": [
            {"name": "Divine Departure", "damage": 220},
            {"name": "Red Haki Domain", "damage": 240},
        ]
    },

    # =========================
    # BLACKBEARD
    # =========================
    "Marshall D. Teach": {
        "Base": [
            {"name": "Dark Grip", "damage": 150},
            {"name": "Quake Punch", "damage": 160},
        ],
        "Awakened": [
            {"name": "Black Hole", "damage": 240},
            {"name": "World Destroyer", "damage": 260},
        ]
    },

    # =========================
    # ROGER
    # =========================
    "Gol D. Roger": {
        "Base": [
            {"name": "Pirate King Slash", "damage": 200},
            {"name": "Divine Haki Strike", "damage": 210},
        ],
        "Legend Form": [
            {"name": "Era Ender", "damage": 260},
            {"name": "One Piece Will", "damage": 280},
        ]
    },

    # =========================
    # GOROSEI
    # =========================
    "Saint Jaygarcia Saturn": {
        "Base": [
            {"name": "Spider Claw Strike", "damage": 180},
            {"name": "Dark Authority", "damage": 200},
            {"name": "Imus Command", "damage": 190},
        ],
        "Mythical Form": [
            {"name": "Underworld Domination", "damage": 270},
            {"name": "Spider God Wrath", "damage": 290},
            {"name": "World Government Erase", "damage": 310},
        ]
    },

    "Saint Ethanbaron V. Nusjuro": {
        "Base": [
            {"name": "Frost Blade", "damage": 170},
            {"name": "Ice Horse Slash", "damage": 185},
            {"name": "Noble Cut", "damage": 175},
        ],
        "Mythical Form": [
            {"name": "Absolute Freeze", "damage": 260},
            {"name": "Divine Horse Strike", "damage": 275},
            {"name": "Frozen Judgment", "damage": 290},
        ]
    },

    "Saint Topman Warcury": {
        "Base": [
            {"name": "Boar Charge", "damage": 175},
            {"name": "Tusk Crush", "damage": 185},
            {"name": "War Cry", "damage": 165},
        ],
        "Mythical Form": [
            {"name": "Divine Boar Rampage", "damage": 260},
            {"name": "Sacred Tusk Destruction", "damage": 280},
            {"name": "World Shatter", "damage": 300},
        ]
    },

    "Saint Shepherd Ju Peter": {
        "Base": [
            {"name": "Sand Vortex", "damage": 170},
            {"name": "Desert Pull", "damage": 180},
            {"name": "Worm Dive", "damage": 175},
        ],
        "Mythical Form": [
            {"name": "Sand God Burial", "damage": 255},
            {"name": "Earth Swallow", "damage": 270},
            {"name": "Divine Sandstorm", "damage": 285},
        ]
    },

    "Saint Marcus Mars": {
        "Base": [
            {"name": "Falcon Strike", "damage": 165},
            {"name": "Sky Dive", "damage": 175},
            {"name": "Wind Slash", "damage": 170},
        ],
        "Mythical Form": [
            {"name": "Divine Bird Assault", "damage": 250},
            {"name": "Heaven's Judgment", "damage": 265},
            {"name": "Sacred Wind Destruction", "damage": 280},
