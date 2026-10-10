"""Brands and models sold in India, for the add-vehicle pickers.

Only a starting list: the pickers still accept anything typed, so a missing or
new model never blocks the admin. Edit freely.
"""

CATALOG = [
    ("Cars & SUVs", {
        "Maruti Suzuki": ["Alto K10", "S-Presso", "Celerio", "Wagon R", "Swift", "Dzire", "Baleno", "Ignis", "Fronx",
                          "Brezza", "Ertiga", "XL6", "Ciaz", "Grand Vitara", "Victoris", "Jimny", "Invicto", "e Vitara", "Eeco",
                          "Glanza", "Alto", "Alto 800", "Ritz", "Vitara Brezza", "S-Cross", "Swift Dzire", "Omni", "Gypsy"],
        "Hyundai": ["Grand i10 Nios", "i20", "i20 N Line", "Aura", "Exter", "Venue", "Venue N Line", "Verna", "Creta",
                    "Creta N Line", "Creta Electric", "Alcazar", "Tucson", "Ioniq 5"],
        "Tata": ["Tiago", "Tiago EV", "Tigor", "Tigor EV", "Altroz", "Punch", "Punch EV", "Nexon", "Nexon EV", "Curvv",
                 "Curvv EV", "Harrier", "Harrier EV", "Safari", "Sierra"],
        "Mahindra": ["Bolero", "Bolero Neo", "Thar", "Thar Roxx", "XUV 3XO", "XUV700", "Scorpio Classic", "Scorpio N",
                     "Marazzo", "BE 6", "XEV 9e"],
        "Toyota": ["Glanza", "Urban Cruiser Taisor", "Rumion", "Urban Cruiser Hyryder", "Innova Crysta", "Innova Hycross",
                   "Fortuner", "Fortuner Legender", "Hilux", "Camry", "Vellfire", "Land Cruiser 300"],
        "Honda": ["Amaze", "City", "City e:HEV", "Elevate"],
        "Kia": ["Sonet", "Syros", "Seltos", "Carens", "Carens Clavis", "Carnival", "EV6", "EV9"],
        "MG": ["Comet EV", "Windsor EV", "Astor", "Hector", "Hector Plus", "ZS EV", "Gloster", "M9", "Cyberster"],
        "Skoda": ["Kylaq", "Kushaq", "Slavia", "Kodiaq", "Superb", "Octavia RS"],
        "Volkswagen": ["Virtus", "Taigun", "Tiguan R-Line", "Golf GTI"],
        "Renault": ["Kwid", "Triber", "Kiger", "Duster"],
        "Nissan": ["Magnite", "X-Trail"],
        "Citroen": ["C3", "eC3", "C3 Aircross", "Basalt", "C5 Aircross"],
        "Jeep": ["Compass", "Meridian", "Wrangler", "Grand Cherokee"],
        "Force Motors": ["Gurkha"],
        "Isuzu": ["D-Max V-Cross", "MU-X"],
        "BYD": ["Atto 3", "Seal", "Sealion 7", "eMax 7"],
        "Mercedes-Benz": ["A-Class Limousine", "C-Class", "E-Class", "S-Class", "Maybach S-Class", "GLA", "GLC", "GLE",
                          "GLS", "Maybach GLS", "G-Class", "EQB", "EQE SUV", "EQS", "AMG GT"],
        "BMW": ["2 Series Gran Coupe", "3 Series Gran Limousine", "M340i", "5 Series", "7 Series", "X1", "X3", "X5",
                "X7", "iX1", "i4", "i5", "i7", "iX", "Z4"],
        "Audi": ["A4", "A6", "Q3", "Q3 Sportback", "Q5", "Q7", "Q8", "e-tron GT", "RS Q8"],
        "Volvo": ["EX30", "EX40", "EC40", "XC60", "XC90", "S90"],
        "Lexus": ["ES", "NX", "RX", "LM", "LX"],
        "Land Rover": ["Defender", "Discovery Sport", "Range Rover Evoque", "Range Rover Velar", "Range Rover Sport",
                       "Range Rover"],
        "Jaguar": ["F-Pace"],
        "Mini": ["Cooper", "Countryman"],
        "Porsche": ["Macan", "Cayenne", "Panamera", "Taycan", "911"],
        "Rolls-Royce": ["Ghost", "Phantom", "Cullinan", "Spectre"],
        "Bentley": ["Flying Spur", "Continental GT", "Bentayga"],
        "Lamborghini": ["Urus", "Temerario", "Revuelto"],
        "Ferrari": ["Roma", "296 GTB", "Purosangue"],
        "Hindustan Motors": ["Ambassador", "Contessa"],
        "Premier": ["Padmini"],
    }),
    ("Bikes & scooters", {
        "Royal Enfield": ["Classic 350", "Bullet 350", "Hunter 350", "Meteor 350", "Goan Classic 350", "Himalayan 450",
                          "Scram 440", "Guerrilla 450", "Interceptor 650", "Continental GT 650", "Super Meteor 650",
                          "Shotgun 650", "Bear 650"],
        "Honda": ["Activa", "Activa 125", "Dio", "Shine 100", "Shine 125", "SP 125", "Unicorn", "Hornet 2.0",
                  "CB350", "H'ness CB350", "CB350RS"],
        "Hero": ["Splendor Plus", "HF Deluxe", "Passion Plus", "Glamour", "Xtreme 125R", "Xtreme 160R",
                 "Xpulse 200 4V", "Mavrick 440", "Destini 125", "Xoom 110", "Pleasure+"],
        "TVS": ["Jupiter", "Jupiter 125", "Ntorq 125", "XL100", "Star City+", "Radeon", "Raider 125",
                "Apache RTR 160", "Apache RTR 200 4V", "Apache RR 310", "Ronin", "iQube"],
        "Bajaj": ["Platina 110", "CT 110X", "Pulsar 150", "Pulsar N160", "Pulsar NS200", "Pulsar N250",
                  "Avenger 220", "Dominar 400", "Freedom 125", "Chetak"],
        "Yamaha": ["Fascino 125", "RayZR 125", "Aerox 155", "FZ-S Fi", "FZ-X", "MT-15", "R15 V4"],
        "Suzuki": ["Access 125", "Burgman Street", "Avenis", "Gixxer", "Gixxer SF", "V-Strom SX"],
        "KTM": ["200 Duke", "250 Duke", "390 Duke", "RC 390", "390 Adventure"],
        "Ather": ["Rizta", "450S", "450X"],
        "Ola Electric": ["S1 X", "S1 Air", "S1 Pro", "Roadster"],
        "Jawa": ["42", "350", "Perak"],
        "Yezdi": ["Roadster", "Scrambler", "Adventure"],
        "Harley-Davidson": ["X440", "Nightster", "Fat Boy"],
        "Triumph": ["Speed 400", "Scrambler 400 X", "Street Triple"],
        "Kawasaki": ["Ninja 300", "Ninja 650", "Z900", "Versys 650"],
        "BMW Motorrad": ["G 310 R", "G 310 GS", "R 1300 GS"],
    }),
    ("Vans, buses & commercial", {
        "Force Motors": ["Traveller (Tempo Traveller)", "Urbania", "Trax Cruiser"],
        "Tata": ["Winger", "Magic", "Ace", "Intra", "Yodha", "Starbus"],
        "Mahindra": ["Supro", "Bolero Pik-Up", "Bolero Camper", "Jeeto", "Treo"],
        "Maruti Suzuki": ["Eeco Cargo", "Super Carry"],
        "Toyota": ["Commuter"],
        "Ashok Leyland": ["Dost", "Bada Dost", "Partner", "Viking"],
        "Eicher": ["Skyline Pro"],
        "Bajaj": ["RE (auto rickshaw)", "Maxima"],
        "Piaggio": ["Ape City", "Ape Xtra"],
    }),
]

COLORS = [
    ("White", "#ffffff"), ("Pearl White", "#f4f1ea"), ("Silver", "#c0c4c8"), ("Grey", "#7b8086"),
    ("Black", "#1b1c1e"), ("Red", "#c21f2a"), ("Maroon", "#6d1d27"), ("Blue", "#1f4fa3"),
    ("Brown", "#6b4a35"), ("Beige", "#d9c7a7"), ("Green", "#2f6b47"), ("Orange", "#e0702a"),
    ("Yellow", "#e9c23a"), ("Bronze", "#9a6a3c"), ("Gold", "#c9a44c"),
]


def as_json():
    """Shape used by the template: [{"group", "brands": [{"name", "models"}]}]."""
    return [
        {"group": group, "brands": [{"name": name, "models": models} for name, models in brands.items()]}
        for group, brands in CATALOG
    ]
