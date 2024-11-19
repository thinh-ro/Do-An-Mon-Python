from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from psycopg2._psycopg import  *

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

def ket_noi_csdl():
    try:
        ket_noi = psycopg2.connect(
            dbname="nguoidung",
            user="postgres",
            password="123321",
            host="localhost",
            port="5432"
        )
        return ket_noi
    except Exception as e:
        print(f"Không thể kết nối cơ sở dữ liệu: {e}")
        return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        ket_noi = ket_noi_csdl()
        con_tro = ket_noi.cursor()
        con_tro.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = con_tro.fetchone()
        ket_noi.close()
        
        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        ket_noi = ket_noi_csdl()
        con_tro = ket_noi.cursor()
        con_tro.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        ket_noi.commit()
        ket_noi.close()
        
        flash("Tài khoản đã được tạo thành công!")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    ket_noi = ket_noi_csdl()
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT * FROM students")
    students = con_tro.fetchall()
    ket_noi.close()

    return render_template('dashboard.html', students=students)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/add_student', methods=['POST'])
def add_student():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    major = request.form['major']

    ket_noi = ket_noi_csdl()
    con_tro = ket_noi.cursor()
    con_tro.execute("INSERT INTO students (name, age, gender, major) VALUES (%s, %s, %s, %s) RETURNING id", (name, age, gender, major))
    student_id = con_tro.fetchone()[0]
    ket_noi.commit()
    ket_noi.close()

    # Trả về dữ liệu sinh viên mới dưới dạng JSON
    return jsonify({"id": student_id, "name": name, "age": age, "gender": gender, "major": major})

@app.route('/delete_student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    ket_noi = ket_noi_csdl()
    con_tro = ket_noi.cursor()
    try:
        con_tro.execute("DELETE FROM students WHERE id = %s", (student_id,))
        ket_noi.commit()
        ket_noi.close()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Lỗi khi xóa sinh viên: {e}")
        ket_noi.close()
        return jsonify({"success": False, "message": "Lỗi khi xóa sinh viên"}), 500
    
@app.route('/update_student/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    major = request.form['major']

    ket_noi = ket_noi_csdl()
    con_tro = ket_noi.cursor()
    try:
        con_tro.execute("""
            UPDATE students
            SET name = %s, age = %s, gender = %s, major = %s
            WHERE id = %s
        """, (name, age, gender, major, student_id))
        ket_noi.commit()
        ket_noi.close()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Lỗi khi cập nhật sinh viên: {e}")
        ket_noi.close()
        return jsonify({"success": False, "message": "Lỗi khi cập nhật sinh viên"}), 500



if __name__ == '__main__':
    app.run(debug=True)
    

import psycopg2

def ket_noi_csdl():
    try:
        ket_noi = psycopg2.connect(
            dbname="nguoidung",
            user="postgres",
            password="123321",
            host="localhost",
            port="5432"
        )
        print("Kết nối cơ sở dữ liệu thành công!")
        ket_noi.close()
    except Exception as e:
        print(f"Không thể kết nối cơ sở dữ liệu: {e}")

ket_noi_csdl()
