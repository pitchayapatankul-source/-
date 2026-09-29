"""
TableChain Database Manager & Seeder
Uses SQLite to store Users, Restaurants, Tables, and Reservations.
Provides conflict-detection to prevent double bookings.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "tablechain.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        wallet_address TEXT UNIQUE
    )
    """)

    # 2. Restaurants Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        location TEXT NOT NULL,
        cuisine TEXT NOT NULL,
        rating REAL DEFAULT 4.8,
        average_price TEXT,
        booking_fee REAL NOT NULL, -- in ETH
        wallet_address TEXT NOT NULL,
        image_url TEXT,
        gallery TEXT, -- JSON array of image URLs
        opening_hours TEXT,
        facilities TEXT, -- JSON array of facilities
        menu TEXT, -- JSON array of menu items
        cancellation_policy TEXT
    )
    """)

    # 3. Tables Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER NOT NULL,
        table_number TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        status TEXT DEFAULT 'Available', -- Available, Reserved, Occupied, Cleaning, Unavailable
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (id),
        UNIQUE(restaurant_id, table_number)
    )
    """)

    # 4. Reservations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT UNIQUE NOT NULL,
        restaurant_id INTEGER NOT NULL,
        user_id INTEGER,
        customer_name TEXT,
        customer_email TEXT,
        customer_phone TEXT,
        table_id INTEGER NOT NULL,
        reservation_date TEXT NOT NULL, -- YYYY-MM-DD
        reservation_time TEXT NOT NULL, -- HH:MM
        guest_count INTEGER NOT NULL,
        booking_fee REAL NOT NULL, -- in ETH
        wallet_address TEXT NOT NULL,
        transaction_hash TEXT,
        payment_status TEXT NOT NULL, -- 'Pending Payment', 'Payment Processing', 'Confirmed', 'Refunded'
        booking_status TEXT NOT NULL, -- 'Pending Payment', 'Payment Processing', 'Confirmed', 'Completed', 'Cancelled', 'No-show'
        special_requests TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (id),
        FOREIGN KEY (table_id) REFERENCES tables (id)
    )
    """)

    conn.commit()
    conn.close()

def seed_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Check if restaurants already exist
    cursor.execute("SELECT COUNT(*) as cnt FROM restaurants")
    count = cursor.fetchone()["cnt"]
    if count > 0:
        conn.close()
        return

    # Seed Restaurants
    restaurants_data = [
        (
            1,
            "Maison Grill",
            "An intimate and distinguished steakhouse nestled in Chiang Mai's historic quarter. Specializing in dry-aged Wagyu, charcoal fire gastronomy, and an award-winning cellar of Old World vintages. Experience unmatched culinary precision in an elegant dark timber atmosphere.",
            "Chiang Mai, Old City",
            "Steakhouse & Grill",
            4.8,
            "800 THB/person",
            0.002,
            "0x91F5B46271Ce26dB8d3F6b429a6beB671a5c9e41",
            "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=1200&auto=format&fit=crop",
            '["https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=800&auto=format&fit=crop", "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?q=80&w=800&auto=format&fit=crop", "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=800&auto=format&fit=crop", "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?q=80&w=800&auto=format&fit=crop"]',
            "17:00 - 23:00 (Tue - Sun)",
            '["Valet Parking", "Dry-Aging Room Display", "Sommelier Service", "Private Dining Salon", "Outdoor Terrace", "Cocktail Lounge"]',
            '[{"name": "45-Day Dry-Aged Australian Tomahawk", "price": "3,400 THB", "desc": "Charcoal grilled over lychee wood, smoked bone marrow butter"}, {"name": "A5 Miyazaki Wagyu Ribeye (250g)", "price": "2,850 THB", "desc": "Truffle potato mousseline, red wine reduction, fleur de sel"}, {"name": "Hokkaido Scallop Carpaccio", "price": "680 THB", "desc": "Finger lime, oscietra caviar, white truffle oil"}, {"name": "Smoked Dark Chocolate Fondant", "price": "420 THB", "desc": "Madagascan vanilla bean gelato, smoked sea salt caramel"}]',
            "Full refund of booking fee if cancelled at least 4 hours before reservation time. No refund for no-shows or cancellations within 4 hours."
        ),
        (
            2,
            "Nara Dining",
            "Contemporary Northern Thai haute cuisine reimagined with modern culinary craftsmanship. Nara Dining sources hyper-seasonal botanicals and heirloom ingredients directly from Royal Project farms in the Chiang Mai highlands.",
            "Chiang Mai, Nimman",
            "Thai Contemporary",
            4.7,
            "600 THB/person",
            0.0015,
            "0x52E824F18c0C460D7b0D92Fa71302A0Fa09d6637",
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1200&auto=format&fit=crop",
            '["https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=800&auto=format&fit=crop", "https://images.unsplash.com/photo-1552566626-52f8b828add9?q=80&w=800&auto=format&fit=crop", "https://images.unsplash.com/photo-1508424757105-b6d5ad9329d0?q=80&w=800&auto=format&fit=crop", "https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=800&auto=format&fit=crop"]',
            "17:30 - 22:30 (Daily)",
            '["Garden Pavilion", "Organic Highland Ingredients", "Tea Pairing Experience", "Cocktail Bar", "Valet Parking", "Vegan Options"]',
            '[{"name": "Khao Soi Deconstructed Tortellini", "price": "520 THB", "desc": "Crispy noodles, braised wagyu cheek, coconut-curry emulsion"}, {"name": "Northern Herbs Cured Salmon Tartare", "price": "480 THB", "desc": "Wild makwaen pepper, betel leaf crisps, kalamansi gel"}, {"name": "Smoked Duck Breast Gaeng Hang Lay", "price": "650 THB", "desc": "Ginger confit, pickled garlic pearls, jasmine rice blossom"}, {"name": "Smoked Coconut & Mango Parfait", "price": "350 THB", "desc": "Pandan crisp, toasted mung beans, coconut cream granite"}]',
            "Free cancellation up to 6 hours before dining time. Booking fee is securely returned via smart contract verification."
        ),
        (
            3,
            "Sakura House",
            "Traditional Kaiseki and Edomae Sushi atelier featuring seafood flown in thrice weekly from Toyosu Market, Tokyo. Immerse yourself in authentic Japanese omotenashi hospitality with bespoke Hinoki wood counter dining.",
            "Chiang Mai, Riverside",
            "Japanese Kaiseki & Sushi",
            4.9,
            "1,000 THB/person",
            0.0025,
            "0x3B887C6C23d3FdA9eA3B3F13a3c7A8b699d8b92E",
            "https://images.unsplash.com/photo-1579027989536-b7b1f875659b?q=80&w=1200&auto=format&fit=crop",
            '["https://images.unsplash.com/photo-1579027989536-b7b1f875659b?q=80&w=800&auto=format&fit=crop", "https://images.unsplash.com/photo-1611143669185-af224c5e3252?q=80&w=800&auto=format&fit=crop", "https://images.unsplash.com/photo-1563245372-f21724e3856d?q=80&w=800&auto=format&fit=crop", "https://images.unsplash.com/photo-1617196034796-73dfa7b1fd56?q=80&w=800&auto=format&fit=crop"]',
            "18:00 - 22:30 (Wed - Mon)",
            '["Sushi Hinoki Counter", "Sake Sommelier", "Private Tatami Rooms", "Riverside Courtyard", "Live Tea Ceremony"]',
            '[{"name": "Edomae Nigiri Omakase (10 pcs)", "price": "2,800 THB", "desc": "Otoro, Uni, Akami, Shima Aji, Botan Ebi, Binchotan charred"}, {"name": "A5 Wagyu & Foie Gras Sukiyaki", "price": "1,600 THB", "desc": "Onsen quail egg, maitake mushrooms, sweet dashi broth"}, {"name": "Tsubugai Clam & Awabi Tempura", "price": "890 THB", "desc": "Matcha sea salt, grated daikon, tentsuyu dipping sauce"}, {"name": "Uji Matcha Ceremonial Mousse", "price": "390 THB", "desc": "Yuzu jelly, azuki red bean compote, 24k gold leaf"}]',
            "Booking fee applies toward your dining bill. Cancellations accepted up to 12 hours prior to scheduled seating."
        ),
        (
            4,
            "L'Atelier Gourmet",
            "Contemporary French haute cuisine set in a sunlit colonial conservatory along the Ping River. Chef-driven seasonal tasting menus celebrating French classical technique with locally harvested tropical flora.",
            "Chiang Mai, Wat Ket",
            "French Contemporary",
            4.8,
            "1,200 THB/person",
            0.003,
            "0x7890Aa1b2C3d4E5f6a7b8C9D0E1F2a3b4C5d6E7f",
            "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?q=80&w=1200&auto=format&fit=crop",
            '["https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?q=80&w=800&auto=format&fit=crop", "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=800&auto=format&fit=crop", "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=800&auto=format&fit=crop"]',
            "18:00 - 23:00 (Tue - Sun)",
            '["Bordeaux Wine Cellar", "Chef Counter", "Riverfront Garden", "Valet Service", "Live Acoustic Piano"]',
            '[{"name": "Pan-Seared Brittany Sea Bass", "price": "1,450 THB", "desc": "Beurre blanc, fennel confit, Kristal caviar"}, {"name": "Roasted Pigeon with Truffle Jus", "price": "1,650 THB", "desc": "Jerusalem artichoke puree, caramelized shallots"}, {"name": "Artisanal French Fromage Platter", "price": "750 THB", "desc": "Selection of 5 AOC cheeses, honeycomb, sourdough crisps"}]',
            "Guaranteed table placement upon on-chain booking fee receipt. Free cancellation up to 6 hours before."
        )
    ]

    cursor.executemany("""
    INSERT INTO restaurants (id, name, description, location, cuisine, rating, average_price, booking_fee, wallet_address, image_url, gallery, opening_hours, facilities, menu, cancellation_policy)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, restaurants_data)

    # Seed Tables for each restaurant
    tables_data = [
        # Maison Grill (Rest 1)
        (1, "Table T01", 2, "Available"),
        (1, "Table T02", 4, "Available"),
        (1, "Table T03", 4, "Reserved"),
        (1, "Table T04", 6, "Available"),
        (1, "Table T05", 2, "Occupied"),
        (1, "VIP Suite 01", 8, "Available"),

        # Nara Dining (Rest 2)
        (2, "Table T01", 2, "Available"),
        (2, "Table T02", 4, "Available"),
        (2, "Table T03", 4, "Available"),
        (2, "Table T04", 6, "Reserved"),
        (2, "Garden Pavilion", 6, "Available"),

        # Sakura House (Rest 3)
        (3, "Counter C01", 2, "Available"),
        (3, "Counter C02", 2, "Occupied"),
        (3, "Table T01", 4, "Available"),
        (3, "Tatami Room 01", 6, "Available"),
        (3, "Tatami Room 02", 6, "Reserved"),

        # L'Atelier (Rest 4)
        (4, "Table T01", 2, "Available"),
        (4, "Table T02", 4, "Available"),
        (4, "Riverview VIP", 6, "Available")
    ]

    cursor.executemany("""
    INSERT INTO tables (restaurant_id, table_number, capacity, status)
    VALUES (?, ?, ?, ?)
    """, tables_data)

    # Seed Sample Users
    cursor.execute("""
    INSERT INTO users (id, name, email, phone, wallet_address)
    VALUES 
    (1, 'Alex Mercer', 'alex.mercer@gmail.com', '+66 81 234 5678', '0x71c4cFf2B9D6f8C380482B768b1812aA9c27a89F'),
    (2, 'Sarah Jenkins', 's.jenkins@web3ventures.io', '+66 89 876 5432', '0x9965507D1a55bcC2695c58bA16Fb37d819b0a4df'),
    (3, 'Nattawut Somchai', 'nattawut.s@techinnovate.th', '+66 82 555 1212', '0x3C44CDDdB6A900fa2B585dD299e03D12Fa4293Bc')
    """)

    # Seed Sample Reservations (including confirmed ones with Sepolia Tx hashes)
    today = date.today()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)

    reservations_data = [
        (
            "TC-20261010-00125",
            1, # Maison Grill
            1,
            "Alex Mercer",
            "alex.mercer@gmail.com",
            "+66 81 234 5678",
            3, # Table T03
            today.strftime("%Y-%m-%d"),
            "19:00",
            4,
            0.002,
            "0x71c4cFf2B9D6f8C380482B768b1812aA9c27a89F",
            "0x89f7c32e92cbb4356ef24a1879ec19ef6d78ef86483562bb608ffb08bb901e3b",
            "Confirmed",
            "Confirmed",
            "Anniversary celebration. Quiet table requested.",
            datetime.now().isoformat()
        ),
        (
            "TC-20261011-00142",
            2, # Nara Dining
            2,
            "Sarah Jenkins",
            "s.jenkins@web3ventures.io",
            "+66 89 876 5432",
            10, # Table T04
            tomorrow.strftime("%Y-%m-%d"),
            "18:30",
            6,
            0.0015,
            "0x9965507D1a55bcC2695c58bA16Fb37d819b0a4df",
            "0x42f88a9c80d461715fbc705a61a498b2ef82b681816f08e49d63259a4192b0c1",
            "Confirmed",
            "Confirmed",
            "Vegan options for two guests.",
            datetime.now().isoformat()
        ),
        (
            "TC-20261009-00098",
            3, # Sakura House
            3,
            "Nattawut Somchai",
            "nattawut.s@techinnovate.th",
            "+66 82 555 1212",
            16, # Tatami Room 02
            yesterday.strftime("%Y-%m-%d"),
            "19:30",
            4,
            0.0025,
            "0x3C44CDDdB6A900fa2B585dD299e03D12Fa4293Bc",
            "0x15b76c8c4a169828456209ef78da9142ec0176884638a2e1d71953267926b482",
            "Confirmed",
            "Completed",
            "Chef recommendation omakase.",
            (datetime.now() - timedelta(days=1)).isoformat()
        )
    ]

    cursor.executemany("""
    INSERT INTO reservations (
        booking_id, restaurant_id, user_id, customer_name, customer_email, customer_phone,
        table_id, reservation_date, reservation_time, guest_count, booking_fee,
        wallet_address, transaction_hash, payment_status, booking_status, special_requests, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, reservations_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_db()
    print("TableChain database initialized and seeded successfully.")
