import sqlite3
import os

# Environment variable'lardan admin bilgilerini al
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'default_admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'default_pass')

# Veritabanını oluştur veya bağlan
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Admin tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Environment variable'dan gelen admin bilgilerini kullan
cursor.execute('''
INSERT OR IGNORE INTO admin (username, password)
VALUES (?, ?)
''', (ADMIN_USERNAME, ADMIN_PASSWORD))

print("Database created successfully!")

cursor.execute('''
    ALTER TABLE reservations ADD COLUMN approved INTEGER DEFAULT 0;
''')

# workshops tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS workshops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    image TEXT NOT NULL,
    approved INTEGER DEFAULT 0
)
''')

conn.commit()
conn.close()

print("Veritabanı hazırlandı ve admin kullanıcısı oluşturuldu!")
