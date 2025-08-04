
"""
Flask uygulaması için temel sayfaları ve kullanıcı giriş doğrulama işlevlerini içerir.
Bu dosya, admin paneline giriş yapmak için kullanıcı adı ve şifre doğrulaması sağlar.
"""
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from reservation import save_reservation, get_all_reservations
from reservation import get_db_connection
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify  
from reservation import add_workshop


app = Flask(__name__)
app.secret_key = 'secret_key'  # Session güvenliği 

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/create_workshop', methods=['POST'])
def create_workshop_post():
    """
    Workshop oluşturma formunu admin onayına göndermek için veritabanına kaydeder.
    """
    workshop_name = request.form['workshopName']
    workshop_date = request.form['workshopDate']
    workshop_location = request.form['workshopLocation']
    workshop_description = request.form['workshopDescription']

    
    # Resim dosyasını al
    file = request.files['workshopImage']
    
    # Eğer dosya uygun ise, dosya ismini güvenli hale getirip, belirli bir klasöre kaydediyoruz
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
    else:
        flash("Geçersiz dosya türü!")
        return redirect(url_for('create_workshop'))

    # Veritabanına kaydet
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO workshops (name, date, location, description, image, approved)
        VALUES (?, ?, ?, ?, ?, 0)  -- approved = 0 means not yet approved by admin
    ''', (workshop_name, workshop_date, workshop_location, workshop_description, filename))
    conn.commit()
    conn.close()

    flash("Workshop başarıyla gönderildi. Admin onayını bekliyor.")
    return redirect(url_for('create_workshop'))



@app.route('/add_workshop', methods=['POST'])
def add_workshop_route():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        add_workshop(title, description, status)  # Workshop ekleme
        return "Workshop added successfully"  # Başarılı bir mesaj döndür

@app.route('/blog')
def blog():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM workshops WHERE approved = 1')
    workshops = cursor.fetchall()
    conn.close()
    return render_template('blog.html', workshops=workshops)

@app.route('/')
def home():
    """
    Anasayfa sayfasını render eder.
    """
    return render_template('index.html')

@app.route('/about')
def about():
    """
    Hakkında sayfasını render eder.
    """
    return render_template('about.html')

@app.route('/create_workshop')
def create_workshop():
    """
    Atölye oluşturma sayfasını render eder.
    """
    return render_template('create_workshop.html')

@app.route('/login')
def login():
    """
    Kullanıcıdan giriş bilgilerini almak için giriş sayfasını render eder.
    """
    return render_template('login.html')

@app.route('/login_post', methods=['POST'])
def login_post():
    """
    Giriş bilgilerini kontrol eder ve doğrulama yapar. Başarılıysa admin paneline yönlendirir.
    """
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
        flash('Kullanıcı adı veya şifre yanlış!')
        return redirect(url_for('login'))

@app.route('/admin')
def admin():
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    workshops = conn.execute('SELECT * FROM workshops').fetchall()
    conn.close()
    return render_template('admin.html', reservations=reservations, workshops=workshops)

@app.route('/ticket', methods=['GET', 'POST'])
def ticket():
    if request.method == 'POST':
        event = request.form['event'] 
        name = request.form['name']
        email = request.form['email']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reservations WHERE event = ? AND email = ?', (event, email))
        existing_reservation = cursor.fetchone()
        
        if existing_reservation:
            flash('Bu etkinlik için daha önce rezervasyon yapılmış!', 'danger')
            return redirect(url_for('ticket'))
        
 
        save_reservation(event, name, email)
        flash('Rezervasyon isteğiniz gönderildi!', 'success')
        conn.commit()
        conn.close()
        
        return redirect(url_for('ticket'))
    
    return render_template('ticket.html')


@app.route('/admin/reservations')
def admin_reservations():
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    conn.close()
    return render_template('admin.html', reservations=reservations)

@app.route('/admin/reservations')
def show_reservations():
    reservations = get_all_reservations()  # Veritabanındaki rezervasyonları al
    return render_template('admin.html', reservations=reservations)

@app.route('/admin/reservations/approve/<int:reservation_id>', methods=['POST'])
def approve_reservation(reservation_id):
    """
    Admin, bir rezervasyonu onaylar.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE reservations
        SET status = 'Onaylı'
        WHERE id = ?
    ''', (reservation_id,))
    conn.commit()
    conn.close()

    flash("Rezervasyon onaylandı.")
    return redirect(url_for('admin'))

@app.route('/admin/reservations/delete/<int:reservation_id>', methods=['POST'])
def delete_reservation(reservation_id):
    """
    Admin, bir rezervasyonu siler.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM reservations
        WHERE id = ?
    ''', (reservation_id,))
    conn.commit()
    conn.close()

    flash("Rezervasyon silindi.")
    return redirect(url_for('admin'))

@app.route('/approve_workshop/<int:workshop_id>', methods=['POST'])
def approve_workshop(workshop_id):
    conn = get_db_connection()
    conn.execute('UPDATE workshops SET status = "Approved" WHERE id = ?', (workshop_id,))
    conn.commit()
    conn.close()
    flash("Atölye onaylandı.")
    return redirect(url_for('admin'))


@app.route('/delete_workshop/<int:workshop_id>', methods=['POST'])
def delete_workshop(workshop_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM workshops WHERE id = ?', (workshop_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/api/approved_reservations')
def approved_reservations():
    conn = sqlite3.connect('database.db')  # Veritabanına bağlan
    cursor = conn.cursor()  # Cursor'ı tanımla
    cursor.execute("SELECT name, email, date, time FROM reservations WHERE status = 'approved'")  # Sorguyu çalıştır
    reservations = cursor.fetchall()  # Verileri al
    conn.close()  # Bağlantıyı kapat
    return jsonify(reservations)  # JSON formatında veriyi döndür

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)