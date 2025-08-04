import sqlite3

# Veritabanı bağlantısını kur
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Rezervasyonlar tablosunu oluştur
def create_reservations_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def save_reservation(event, name, email):
    """
    Yeni bir rezervasyonu veritabanına kaydeder.
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reservations (event, name, email)
        VALUES (?, ?, ?)
    ''', (event, name, email))
    conn.commit()
    conn.close()

    print("Rezervasyon kaydedildi:", event, name, email)  # Debug: Rezervasyon kaydedildiğini kontrol et


def get_all_reservations():
    conn = get_db_connection()  # Veritabanı bağlantısını aç
    cursor = conn.cursor()  # Veritabanı cursor'ını oluştur

    cursor.execute("SELECT * FROM reservations")  # 'reservations' tablosundaki tüm verileri al
    reservations = cursor.fetchall()  # Verileri liste olarak al

    conn.close()  # Bağlantıyı kapat
    return reservations


def add_workshop(title, description, status):
    connection, cursor = get_db_connection()  # Bağlantıyı ve cursor'u al
    cursor.execute("INSERT INTO workshops (title, description, status) VALUES (?, ?, ?)", (title, description, status))
    connection.commit()  # Değişiklikleri kaydet
    connection.close()  # Bağlantıyı kapat

create_reservations_table()
