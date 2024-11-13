TEAMS = { 
    "BCH": "Barley's Chewies",
    "TMT": "Team Two",
    "MRU": 'Memes "R" Us',
    "CTZ": "Confused Time Zoners",
    "FLO": "Floccinaucinihilipilification",
    "MVP": "MVP on a Loss FeelsAbzeerMan",
    "PBR": "Peanut Butter Randos",
    "DOH": "Disciples of the Highlord"
    }

MAPS = [
    "Alterac Pass",
    "Battlefield of Eternity",
    "Braxis Holdout",
    "Cursed Hollow",
    "Dragon Shire",
    "Garden of Terror",
    "Infernal Shrines",
    "Sky Temple",
    "Tomb of the Spider Queen",
    "Towers of Doom",
    "Volskaya Foundry"
    ]

HEROES = {
    "Tank": {
        "Anub'arak", "Arthas", "Blaze", "Cho", "Diablo",
        "E.T.C.", "Garrosh", "Johanna", "Mei", "Muradin",
        "Mal'Ganis", "Stitches", "Tyrael"
        },
    "Bruiser": {
        "Artanis", "Chen", "D.Va", "Deathwing", "Dehaka",
        "Gazlowe", "Hogger", "Imperius", "Leoric", "Malthael",
        "Ragnaros", "Rexxar", "Sonya", "Thrall", "Varian",
        "Xul", "Yrel"
        },
    "Healer": {
        "Alexstrasza", "Ana", "Anduin", "Auriel", "Brightwing",
        "Deckard", "Kharazim", "Li Li", "Lt. Morales", "Lucio",
        "Malfurion", "Rehgar", "Stukov", "Tyrande", "Uther",
        "Whitemane"
        },
    "Melee Assassin": {
        "Alarak", "Illidan", "Kerrigan", "Maiev", "Murky",
        "Qhira", "Samuro", "The Butcher", "Valeera", "Zeratul"
        },
    "Ranged Assassin": {
        "Azmodan", "Cassia", "Chromie", "Falstad", "Fenix",
        "Gall", "Genji", "Greymane", "Gul'dan", "Hanzo",
        "Jaina",  "Junkrat", "Kael'thas", "Kel'Thuzad", "Li-Ming",
        "Lunara", "Mephisto", "Nazeebo", "Nova", "Orphea",
        "Probius", "Raynor", "Sgt. Hammer", "Sylvanas", "Tassadar",
        "Tracer", "Tychus", "Valla", "Zagara", "Zul'jin"
        },
    "Support": {
        "Abathur", "Medivh", "TLV", "The Lost Vikings", "Zarya"
        }
    }

BRACKET = {
    "Quarterfinals": {
        "1": {
            "Team 1": "BCH",
            "Team 2": "MVP",
            "Best of": 3,  # Best of 3 for this round
            "Team 1 Wins": 0,  # Track wins for Team 1
            "Team 2 Wins": 0,  # Track wins for Team 2
            "Series Winner": None  # To be filled after the match
        },
        "2": {
            "Team 1": "CTZ",
            "Team 2": "TMT",
            "Best of": 3,
            "Team 1 Wins": 0,
            "Team 2 Wins": 0,
            "Series Winner": None
        },
        "3": {
            "Team 1": "DOH",
            "Team 2": "FLO",
            "Best of": 3,
            "Team 1 Wins": 0,
            "Team 2 Wins": 0,
            "Series Winner": None
        },
        "4": {
            "Team 1": "MRU",
            "Team 2": "PBR",
            "Best of": 3,
            "Team 1 Wins": 0,
            "Team 2 Wins": 0,
            "Series Winner": None
        },
    },
    "Semifinals": {
        "5": {
            "Team 1": None,  # Winner of Series 1
            "Team 2": None,  # Winner of Series 2
            "Best of": 5,  # Best of 5 starting from quarterfinals
            "Team 1 Wins": 0,
            "Team 2 Wins": 0,
            "Series Winner": None
        },
        "6": {
            "Team 1": None,  # Winner of Series 3
            "Team 2": None,  # Winner of Series 4
            "Best of": 5,
            "Team 1 Wins": 0,
            "Team 2 Wins": 0,
            "Series Winner": None
        }
    },
    "Finals": {
        "7": {
            "Team 1": None,  # Winner of Series 5
            "Team 2": None,  # Winner of Series 6
            "Best of": 5,
            "Team 1 Wins": 0,
            "Team 2 Wins": 0,
            "Series Winner": None
        }
    }
}

