from flask import Flask, render_template, request
import sqlite3
import qrcode
import os

app = Flask(__name__)

# Create database
def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  phone TEXT,
                  email TEXT,
                  address TEXT)''')
    conn.close()

init_db()

# Home page (form)
@app.route('/')
def index():
    return render_template('index.html')

# Save data and generate QR
@app.route('/generate', methods=['POST'])
def generate():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    address = request.form['address']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, phone, email, address) VALUES (?, ?, ?, ?)",
                   (name, phone, email, address))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Generate QR
    url = f"http://127.0.0.1:5000/profile/{user_id}"
    img = qrcode.make(url)

    if not os.path.exists('static'):
        os.makedirs('static')

    img_path = f"static/qr_{user_id}.png"
    img.save(img_path)

    return render_template('qr.html', img_path=img_path)

# Profile display
@app.route('/profile/<int:user_id>')
def profile(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
