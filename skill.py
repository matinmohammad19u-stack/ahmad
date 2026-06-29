# skill.py

SKILL_DB = {

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
            {"name": "Sacred Wind Destruction", "damage": 280}
        ],
    },
# =========================
    # YONKO
    # =========================
    "Kaido": {
        "Base": [
            {"name": "Bolo Breath", "damage": 200},
            {"name": "Kaido Club Slam", "damage": 190},
        ],
        "Dragon Form": [
            {"name": "Tatsumaki Kaifu", "damage": 250},
            {"name": "Thunder Bagua", "damage": 260},
        ],
        "Hybrid Form": [
            {"name": "Ragnaraku", "damage": 270},
            {"name": "Shoryu Kaido", "damage": 280},
        ],
    },

    "Charlotte Linlin": {
        "Base": [
            {"name": "Fist of Mother", "damage": 185},
            {"name": "Soul Pocus", "damage": 170},
        ],
        "Awakened": [
            {"name": "Heavenly Fire", "damage": 240},
            {"name": "Indra", "damage": 255},
            {"name": "Ikoku", "damage": 260},
        ],
    },

    "Edward Newgate": {
        "Base": [
            {"name": "Quake Shockwave", "damage": 195},
            {"name": "Seismic Strike", "damage": 185},
        ],
        "Tremor Form": [
            {"name": "Gura Gura Crush", "damage": 255},
            {"name": "Tectonic Shatter", "damage": 265},
            {"name": "World Split", "damage": 280},
        ],
    },

    # =========================
    # COMMANDERS / SUPERNOVAS
    # =========================
    "Boa Hancock": {
        "Base": [
            {"name": "Slave Arrow", "damage": 120},
            {"name": "Pistol Kiss", "damage": 110},
        ],
        "Perfume Femur": [
            {"name": "Mero Mero Mellow", "damage": 175},
            {"name": "Slave Cannon", "damage": 185},
        ],
    },

    "Portgas D. Ace": {
        "Base": [
            {"name": "Fire Fist", "damage": 130},
            {"name": "Flame Shot", "damage": 120},
        ],
        "Awakened": [
            {"name": "Entei", "damage": 190},
            {"name": "Dai Enkai", "damage": 200},
        ],
    },

    "Sabo": {
        "Base": [
            {"name": "Dragon Claw", "damage": 125},
            {"name": "Hiken", "damage": 135},
        ],
        "Flame Form": [
            {"name": "Ryusoken", "damage": 180},
            {"name": "Ace's Will Fire Fist", "damage": 200},
        ],
    },

    "Trafalgar D. Water Law": {
        "Base": [
            {"name": "Gamma Knife", "damage": 120},
            {"name": "Shambles", "damage": 110},
        ],
        "Awakened": [
            {"name": "K-Room Spike", "damage": 180},
            {"name": "Puncture Wille", "damage": 195},
        ],
    },

    "Eustass Kid": {
        "Base": [
            {"name": "Punk Pistol", "damage": 130},
            {"name": "Metal Crush", "damage": 120},
        ],
        "Awakened": [
            {"name": "Damned Punk", "damage": 200},
            {"name": "Punk Corna Dio", "damage": 210},
        ],
    },

    "Killer": {
        "Base": [
            {"name": "Scythe Slash", "damage": 110},
            {"name": "Buzz Cut Blade", "damage": 120},
        ],
        "Sonic Form": [
            {"name": "Kamaa Sonic", "damage": 170},
            {"name": "Death Slash", "damage": 180},
        ],
    },

    "Jinbe": {
        "Base": [
            {"name": "Fishman Karate Punch", "damage": 120},
            {"name": "Vagabond Drill", "damage": 130},
        ],
        "Water Form": [
            {"name": "Arabesque Brick Fist", "damage": 180},
            {"name": "Sea Current Slam", "damage": 190},
        ],
    },

    "Crocodile": {
        "Base": [
            {"name": "Desert Spada", "damage": 120},
            {"name": "Sand Tomb", "damage": 110},
        ],
        "Awakened": [
            {"name": "Ground Secco", "damage": 175},
            {"name": "Desert Girasole", "damage": 185},
        ],
    },

    "Doflamingo": {
        "Base": [
            {"name": "Goshikito", "damage": 130},
            {"name": "Athlete", "damage": 120},
        ],
        "Awakened": [
            {"name": "Bird Cage", "damage": 160},
            {"name": "Ikkou Tobu", "damage": 200},
            {"name": "God Thread", "damage": 215},
        ],
    },

    "Issho": {
        "Base": [
            {"name": "Gravity Push", "damage": 120},
            {"name": "Meteor Pull", "damage": 140},
        ],
        "Awakened": [
            {"name": "Planet Crush", "damage": 220},
            {"name": "Gravity Collapse", "damage": 240},
        ],
    },
# =========================
    # CHARLOTTE FAMILY
    # =========================
    "Charlotte Smoothie": {
        "Base": [
            {"name": "Wring Slash", "damage": 115},
            {"name": "Juice Blade", "damage": 120},
        ],
        "Giant Form": [
            {"name": "Drought Slash", "damage": 175},
            {"name": "Squeeze Devastation", "damage": 185},
        ],
    },

    "Charlotte Cracker": {
        "Base": [
            {"name": "Biscuit Soldier", "damage": 110},
            {"name": "Cracker Slash", "damage": 120},
        ],
        "Biscuit Armor": [
            {"name": "Bis Bis Cannon", "damage": 170},
            {"name": "Thousand Arms Crush", "damage": 185},
        ],
    },

    "Charlotte Perospero": {
        "Base": [
            {"name": "Candy Sword", "damage": 105},
            {"name": "Lollipop Candy Shower", "damage": 115},
        ],
        "Candy Form": [
            {"name": "Candy Imprisonment", "damage": 160},
            {"name": "Perorin Shower", "damage": 170},
        ],
    },
    
# =========================
    # KAIDO'S FORCES
    # =========================
    "King": {
        "Base": [
            {"name": "Anesthetic Slash", "damage": 135},
            {"name": "Omori Karasuma", "damage": 145},
        ],
        "Pteranodon Form": [
            {"name": "Tempura Udon", "damage": 195},
            {"name": "Imperial Flames", "damage": 210},
        ],
    },

    "Queen": {
        "Base": [
            {"name": "Brachiosaurus Slam", "damage": 130},
            {"name": "Plague Rounds", "damage": 120},
        ],
        "Hybrid Form": [
            {"name": "Black Coffee", "damage": 185},
            {"name": "Cog of Destruction", "damage": 200},
        ],
    },

    "Jack": {
        "Base": [
            {"name": "Mammoth Stomp", "damage": 125},
            {"name": "Tusk Crash", "damage": 130},
        ],
        "Mammoth Form": [
            {"name": "Drought Devastation", "damage": 180},
            {"name": "Eternal Torment", "damage": 195},
        ],
    },
    # =========================
    # MARINES / CP0
    # =========================
    "Smoker": {
        "Base": [
            {"name": "Smoke Punch", "damage": 100},
            {"name": "White Out", "damage": 110},
        ],
        "Awakened": [
            {"name": "Smoke Binding", "damage": 160},
            {"name": "White Snake", "damage": 175},
        ],
    },

    "Coby": {
        "Base": [
            {"name": "Haki Punch", "damage": 95},
            {"name": "Soru Strike", "damage": 105},
        ],
        "Hero Mode": [
            {"name": "Honesty Impact", "damage": 160},
            {"name": "Marine Rising Star", "damage": 170},
        ],
    },

    "Rob Lucci": {
        "Base": [
            {"name": "Shigan", "damage": 115},
            {"name": "Rankyaku", "damage": 120},
        ],
        "Awakened Leopard": [
            {"name": "Leopard Barrage", "damage": 185},
            {"name": "Awakened Rokuogan", "damage": 200},
        ],
    },

    "Kaku": {
        "Base": [
            {"name": "Rankyaku", "damage": 105},
            {"name": "Bigan", "damage": 110},
        ],
        "Giraffe Hybrid": [
            {"name": "Pasta Machine", "damage": 165},
            {"name": "Giraffe Cannon", "damage": 175},
        ],
    },
# =========================
    # SUPERNOVA / OTHER PIRATES
    # =========================
    "Basil Hawkins": {
        "Base": [
            {"name": "Straw Man Slash", "damage": 105},
            {"name": "Nail Spike", "damage": 110},
        ],
        "Voodoo Form": [
            {"name": "Death Forecast", "damage": 160},
            {"name": "Card of Fate", "damage": 170},
        ],
    },

    "Scratchmen Apoo": {
        "Base": [
            {"name": "Scratch Punch", "damage": 100},
            {"name": "Beat Slash", "damage": 105},
        ],
        "Music Form": [
            {"name": "Tatakau Ongaku", "damage": 155},
            {"name": "Sound Shatter", "damage": 165},
        ],
    },

    "Urouge": {
        "Base": [
            {"name": "Damage Absorb Punch", "damage": 110},
            {"name": "Karma Slam", "damage": 115},
        ],
        "Sin Form": [
            {"name": "Heavenly Punishment", "damage": 165},
            {"name": "Enlarged Devastation", "damage": 180},
        ],
    },

    "X Drake": {
        "Base": [
            {"name": "Allosaurus Bite", "damage": 110},
            {"name": "Drake Claw", "damage": 115},
        ],
        "Hybrid Form": [
            {"name": "Dinosaur Rampage", "damage": 165},
            {"name": "Rear Admiral Strike", "damage": 180},
        ],
    },

    "Cavendish": {
        "Base": [
            {"name": "Durandal Slash", "damage": 115},
            {"name": "Pirate Prince Cut", "damage": 120},
        ],
        "Hakuba Mode": [
            {"name": "Slashing Gale", "damage": 175},
            {"name": "Hakuba Death Reap", "damage": 190},
        ],
    },
        # =========================
    # SPECIAL / LEGENDS
    # =========================
    "Monkey D. Dragon": {
        "Base": [
            {"name": "Wind Slash", "damage": 165},
            {"name": "Storm Strike", "damage": 175},
        ],
        "Storm Form": [
            {"name": "Revolutionary Tempest", "damage": 240},
            {"name": "Dragon's Wrath", "damage": 255},
            {"name": "World Liberation Storm", "damage": 270},
        ],
    },
}
