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

# Workshops tablosunu oluştur
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

# Reservations tablosunu oluştur (DÜZELTME: workshop_name kolonu eklendi)
cursor.execute('''
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workshop_id INTEGER,
    workshop_name TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    approved INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workshop_id) REFERENCES workshops (id)
)
''')

# Eğer reservations tablosu zaten varsa ve workshop_name kolonu yoksa, ekle
try:
    cursor.execute('ALTER TABLE reservations ADD COLUMN workshop_name TEXT')
    print("workshop_name kolonu eklendi")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("workshop_name kolonu zaten mevcut")
    else:
        print(f"Kolon ekleme hatası: {e}")

# Tüm değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()
conn.close()
print("Database created successfully!")
print("Veritabanı hazırlandı ve admin kullanıcısı oluşturuldu!")
