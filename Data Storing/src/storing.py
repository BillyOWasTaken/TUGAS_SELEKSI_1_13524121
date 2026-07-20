import json
import sys
import mariadb

try:
    conn = mariadb.connect(
        user="root",
        password="root",
        host="localhost"
    )
except mariadb.Error as e:
    print(f"Connection error: {e}")
    sys.exit(1)

cur = conn.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS rogerdodger")
cur.execute("USE rogerdodger")

#create tables

cur.execute("""
CREATE TABLE IF NOT EXISTS persona (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(67) UNIQUE NOT NULL,
    occupation VARCHAR(255),
    notes TEXT
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS episode (
    id INT UNSIGNED PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    season TINYINT UNSIGNED NOT NULL,
    episode TINYINT UNSIGNED NOT NULL,
    air_date DATE NOT NULL,
    runtime_minutes TINYINT UNSIGNED NOT NULL,
    summary TEXT NOT NULL,
    tvdb_url VARCHAR(67) NOT NULL
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS quotes (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    persona INT UNSIGNED NOT NULL,
    quote TEXT NOT NULL,
    FOREIGN KEY (persona) REFERENCES persona(id) ON DELETE CASCADE
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS appearance (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    persona INT UNSIGNED NOT NULL,
    episode INT UNSIGNED NOT NULL,
    is_intro BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (persona) REFERENCES persona(id) ON DELETE CASCADE,
    FOREIGN KEY (episode) REFERENCES episode(id) ON DELETE CASCADE,
    UNIQUE (persona, episode, is_intro)
)""")

#insertion

with open("../../Data Scraping/data/episodes.json", "r", encoding="utf-8") as file:
    episodes = json.load(file)

for ep in episodes:
    runtime = ep["runtime"]

    if isinstance(runtime, str):
        runtime = int(runtime.split()[0])

    cur.execute("INSERT INTO episode (id, title, season, episode, air_date, runtime_minutes, summary, tvdb_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
        ep["id"],
        ep["title"],
        ep["season"],
        ep["episode"],
        ep["air_date"],
        runtime,
        ep["summary"],
        ep["tvdb_url"]
    ))


with open("../../Data Scraping/data/personas.json", "r", encoding="utf-8") as file:
    personas = json.load(file)

for person in personas:

    cur.execute("INSERT INTO persona (name, occupation, notes) VALUES (?, ?, ?)", (person["name"], person["occupation"], person["notes"]))

    persona_id = cur.lastrowid

    for quote in person["quotes"]:
        cur.execute("INSERT INTO quotes (persona, quote) VALUES (?, ?)", (persona_id, quote))

    if person["first_appeared"] is not None:
        cur.execute("INSERT INTO appearance (persona, episode, is_intro) VALUES (?, ?, FALSE)", (persona_id, person["first_appeared"]))

    if person["appeared_in_intro"] is not None:
        cur.execute("INSERT INTO appearance (persona, episode, is_intro) VALUES (?, ?, TRUE)", (persona_id, person["appeared_in_intro"]))

conn.commit()
conn.close()
