
"""
Flask uygulaması için temel sayfaları ve kullanıcı giriş doğrulama işlevlerini içerir.
Bu dosya, admin paneline giriş yapmak için kullanıcı adı ve şifre doğrulaması sağlar.
"""
import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from reservation import save_reservation, get_all_reservations, get_db_connection, add_workshop

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
app.debug = os.getenv('DEBUG', 'False').lower() == 'true'

# Upload klasörü ayarları
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Upload klasörünü oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    """Anasayfa sayfasını render eder."""
    return render_template('index.html')

@app.route('/about')
def about():
    """Hakkında sayfasını render eder."""
    return render_template('about.html')

@app.route('/blog')
def blog():
    """Onaylı workshop'ları listeler."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM workshops WHERE approved = 1')
    workshops = cursor.fetchall()
    conn.close()
    return render_template('blog.html', workshops=workshops)

@app.route('/create_workshop')
def create_workshop():
    """Atölye oluşturma sayfasını render eder."""
    return render_template('create_workshop.html')

@app.route('/create_workshop', methods=['POST'])
def create_workshop_post():
    """Workshop oluşturma formunu admin onayına göndermek için veritabanına kaydeder."""
    workshop_name = request.form['workshopName']
    workshop_date = request.form['workshopDate']
    workshop_location = request.form['workshopLocation']
    workshop_description = request.form['workshopDescription']
    
    # Resim dosyasını al
    file = request.files['workshopImage']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
    else:
        flash("Geçersiz dosya türü!", 'error')
        return redirect(url_for('create_workshop'))

    # Veritabanına kaydet
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO workshops (name, date, location, description, image, approved)
        VALUES (?, ?, ?, ?, ?, 0)
    ''', (workshop_name, workshop_date, workshop_location, workshop_description, filename))
    conn.commit()
    conn.close()

    flash("Workshop başarıyla gönderildi. Admin onayını bekliyor.", 'success')
    return redirect(url_for('create_workshop'))

@app.route('/ticket', methods=['GET', 'POST'])
def ticket():
    """Rezervasyon sayfası."""
    if request.method == 'POST':
        workshop_name = request.form['event'] 
        name = request.form['name']
        email = request.form['email']

        # Çift rezervasyon kontrolü
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reservations WHERE workshop_name = ? AND email = ?', (workshop_name, email))
        existing_reservation = cursor.fetchone()
        
        if existing_reservation:
            conn.close()
            flash('Bu etkinlik için daha önce rezervasyon yapılmış!', 'error')
            return redirect(url_for('ticket'))
        
        conn.close()
        save_reservation(workshop_name, name, email)
        flash('Rezervasyon isteğiniz gönderildi!', 'success')
        return redirect(url_for('ticket'))
    
    return render_template('ticket.html')

@app.route('/login')
def login():
    """Giriş sayfasını render eder."""
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    """Giriş bilgilerini kontrol eder."""
    username = request.form['username']
    password = request.form['password']

    # Veritabanından kullanıcı doğrulama
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admin WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return redirect(url_for('admin'))
    else:
        flash('Kullanıcı adı veya şifre yanlış!', 'error')
        return redirect(url_for('login'))

@app.route('/admin')
def admin():
    """Admin paneli."""
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    workshops = conn.execute('SELECT * FROM workshops').fetchall()
    conn.close()
    return render_template('admin.html', reservations=reservations, workshops=workshops)

@app.route('/admin/reservations/approve/<int:reservation_id>', methods=['POST'])
def approve_reservation(reservation_id):
    """Rezervasyonu onaylar."""
    conn = get_db_connection()
    conn.execute('UPDATE reservations SET approved = 1 WHERE id = ?', (reservation_id,))
    conn.commit()
    conn.close()
    flash("Rezervasyon onaylandı.", 'success')
    return redirect(url_for('admin'))

@app.route('/admin/reservations/delete/<int:reservation_id>', methods=['POST'])
def delete_reservation(reservation_id):
    """Rezervasyonu siler."""
    conn = get_db_connection()
    conn.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
    conn.commit()
    conn.close()
    flash("Rezervasyon silindi.", 'success')
    return redirect(url_for('admin'))

@app.route('/approve_workshop/<int:workshop_id>', methods=['POST'])
def approve_workshop(workshop_id):
    """Workshop'u onaylar."""
    conn = get_db_connection()
    conn.execute('UPDATE workshops SET approved = 1 WHERE id = ?', (workshop_id,))
    conn.commit()
    conn.close()
    flash("Atölye onaylandı.", 'success')
    return redirect(url_for('admin'))

@app.route('/delete_workshop/<int:workshop_id>', methods=['POST'])
def delete_workshop(workshop_id):
    """Workshop'u siler."""
    conn = get_db_connection()
    conn.execute('DELETE FROM workshops WHERE id = ?', (workshop_id,))
    conn.commit()
    conn.close()
    flash("Atölye silindi.", 'success')
    return redirect(url_for('admin'))

@app.route('/api/approved_reservations')
def approved_reservations():
    """Onaylı rezervasyonları JSON olarak döndürür."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM reservations WHERE approved = 1")
    reservations = cursor.fetchall()
    conn.close()
    return jsonify(reservations)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
