from database.database import open_connection
from services.auth import AuthService
import sqlite3

# SQL príkazy pre Futbalový projekt (bez DROP TABLE)
# Používame IF NOT EXISTS, aby sme neprepisovali existujúce tabuľky
DDL_CREATE = """
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL, -- 'admin', 'coach', 'player'
    first_name TEXT,
    last_name TEXT,
    position TEXT,
    birth_date DATE,
    team_id INTEGER,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATETIME NOT NULL,
    opponent TEXT NOT NULL,
    location TEXT NOT NULL,
    home_score INTEGER DEFAULT NULL CHECK (home_score IS NULL OR home_score >= 0),
    away_score INTEGER DEFAULT NULL CHECK (away_score IS NULL OR away_score >= 0),
    team_id INTEGER,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

CREATE TABLE IF NOT EXISTS trainings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATETIME NOT NULL,
    location TEXT NOT NULL,
    description TEXT,
    team_id INTEGER,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    match_id INTEGER,
    training_id INTEGER,
    present BOOLEAN DEFAULT 0,
    confirmed BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (training_id) REFERENCES trainings(id)
);

CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    coach_id INTEGER,
    rating REAL,
    comment TEXT,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (player_id) REFERENCES users(id),
    FOREIGN KEY (coach_id) REFERENCES users(id)
);
"""

# Príkaz na vymazanie (len ak ho explicitne chceme)
DDL_DROP = """
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS evaluations;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS trainings;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS items;
"""

if __name__ == "__main__":
    print("Spúšťam inicializáciu databázy...")

    # Otázka pre používateľa, aby si omylom nezmazal dáta
    choice = input("Chceš VYMAZAŤ existujúce dáta a začať nanovo? (ano/nie) [nie]: ").lower().strip()

    with open_connection() as conn:
        if choice in ('ano', 'y', 'yes'):
            print("Vymazávam staré tabuľky...")
            conn.executescript(DDL_DROP)
            print("Vytváram nové tabuľky...")
            conn.executescript(DDL_CREATE)

            # Seedovanie dát (len pri resete)
            print("Vkladám základné dáta (Admin, Tréner, Hráč)...")
            auth_service = AuthService(conn)
            admin_pass = auth_service.hash_password("admin123")
            coach_pass = auth_service.hash_password("trener123")
            player_pass = auth_service.hash_password("hrac123")

            # Oprava: Použijeme explicitný kurzor pre získanie lastrowid
            cur = conn.cursor()
            cur.execute("INSERT INTO teams (name, description) VALUES (?, ?)", ("FK Lokomotíva", "Hlavný tím A"))
            team_id = cur.lastrowid

            # Vloženie používateľov (tu už lastrowid nepotrebujeme, môžeme použiť execute priamo, alebo cez cur)
            cur.execute("INSERT INTO users(username, password_hash, role, first_name, last_name) VALUES (?, ?, ?, ?, ?)", ("admin", admin_pass, "admin", "Hlavný", "Admin"))
            cur.execute("INSERT INTO users(username, password_hash, role, first_name, last_name, team_id) VALUES (?, ?, ?, ?, ?, ?)", ("trener", coach_pass, "coach", "Jozef", "Mourinho", team_id))
            cur.execute("INSERT INTO users(username, password_hash, role, first_name, last_name, position, team_id) VALUES (?, ?, ?, ?, ?, ?, ?)", ("hrac", player_pass, "player", "Marek", "Hamšík", "Záložník", team_id))

            print("Hotovo! Databáza bola resetovaná.")

        else:
            print("Aktualizujem štruktúru tabuliek (bez straty dát)...")
            conn.executescript(DDL_CREATE)

            # Kontrola, či existuje admin, ak nie, vytvoríme ho (pre istotu)
            try:
                cur = conn.cursor()
                existing_admin = cur.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
                if not existing_admin:
                    print("Admin neexistuje, vytváram ho...")
                    auth_service = AuthService(conn)
                    admin_pass = auth_service.hash_password("admin123")
                    cur.execute("INSERT INTO users(username, password_hash, role, first_name, last_name) VALUES (?, ?, ?, ?, ?)", ("admin", admin_pass, "admin", "Hlavný", "Admin"))
            except sqlite3.OperationalError:
                pass # Tabuľka users možno ešte neexistovala pred DDL_CREATE

            print("Hotovo! Databáza je pripravená na použitie.")

        conn.commit()