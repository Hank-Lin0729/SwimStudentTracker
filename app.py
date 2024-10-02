from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import io


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用於 session 加密
app.permanent_session_lifetime = timedelta(minutes=30)  # 設置 session 過期時間為30分鐘



# 配置 MySQL 連接
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'school_system'
}

# 建立資料庫連接
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# 允許上傳的檔案格式
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 檢查檔案是否允許上傳
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 登入頁面
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 查詢用戶
        cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session.permanent = True  # 啟用永久 session，使用設置的過期時間
            session['username'] = user['username']  # 存入使用者的帳號
            session['name'] = user['name']  # 存入使用者的姓名
            
            # 根據不同的用戶導向不同的頁面
            if user['username'] == 'swim_user':
                return redirect(url_for('student_entry'))
            elif user['username'] == 'PEadmin':
                return redirect(url_for('admin_dashboard'))
        else:
            return '登入失敗，請檢查帳號或密碼', 401

    return render_template('login.html')


@app.route('/student_entry', methods=['GET', 'POST'])
def student_entry():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        person_id = request.form['student_id']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT name, class FROM Students WHERE student_id = %s", (person_id,))
        person = cursor.fetchone()

        if person:
            name = person['name']
            person_class = person['class']
            person_type = '學生'
        else:
            cursor.execute("SELECT name FROM Teachers WHERE teacher_id = %s", (person_id,))
            person = cursor.fetchone()

            if person:
                name = person['name']
                person_class = None  
                person_type = '老師'
            else:
                cursor.close()
                conn.close()
                return "未找到此學號或教師編號的資訊"

        current_time = datetime.now()

        cursor.execute("""
            SELECT * FROM EntryExitLogs 
            WHERE person_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (person_id,))
        last_log = cursor.fetchone()

        if last_log:
            last_timestamp = last_log['timestamp']
            last_entry_exit = last_log['entry_exit']
            if last_entry_exit == '出場' or last_timestamp.date() != current_time.date():
                entry_exit = '進場'
            else:
                entry_exit = '出場'
        else:
            entry_exit = '進場'

        cursor.execute("""
            INSERT INTO EntryExitLogs (person_id, name, class, timestamp, entry_exit, person_type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (person_id, name, person_class, current_time, entry_exit, person_type))

        conn.commit()
        cursor.close()
        conn.close()

        return f"{person_type} <span id='name'> {name}</span> 的紀錄已更新為 <sqan id='exit'>{entry_exit}</span>"

    return render_template('student_entry.html')

# 游泳池管理系統 - 管理介面
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'username' in session and session['username'] == 'PEadmin':
        if request.method == 'POST':
            # 匯入學生名單
            if 'import_students' in request.form:
                return redirect(url_for('import_students'))
            # 匯入教師名單
            elif 'import_teachers' in request.form:
                return redirect(url_for('import_teachers'))
            # 匯出游泳池紀錄
            elif 'export_logs' in request.form:
                return redirect(url_for('export_logs'))
            # 刪除所有游泳池進出紀錄
            elif 'delete_all_logs' in request.form:
                return redirect(url_for('delete_all_logs'))
        return render_template('admin_dashboard.html')
    return redirect(url_for('login'))



# 匯入學生名單
@app.route('/import_students', methods=['GET', 'POST'])
def import_students():
    if 'username' in session and session['username'] == 'PEadmin':
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('未選擇檔案')
                return redirect(request.url)

            file = request.files['file']

            if file.filename == '':
                flash('未選擇檔案')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # 根據文件類型選擇引擎
                if file.filename.endswith('.xls'):
                    data = pd.read_excel(file_path, engine='xlrd')
                elif file.filename.endswith('.xlsx'):
                    data = pd.read_excel(file_path, engine='openpyxl')
                else:
                    flash('無法識別的文件格式')
                    return redirect(request.url)

                # 從這裡開始處理數據
                conn = get_db_connection()
                cursor = conn.cursor()

                for index, row in data.iterrows():
                    cursor.execute(
                        "INSERT INTO Students (class, student_id, name, seat_number) VALUES (%s, %s, %s, %s)",
                        (row['班級'], row['學號'], row['姓名'], row['座號'])
                    )

                conn.commit()
                cursor.close()
                conn.close()

                flash('學生名單已匯入成功')
                return redirect(url_for('import_students'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT class, student_id, name, seat_number FROM Students ORDER BY student_id ASC")
        students = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('import_students.html', students=students)

    return redirect(url_for('login'))

# 編輯學生資料
@app.route('/edit_student/<int:student_id>', methods=['POST'])
def edit_student(student_id):
    if 'username' in session and session['username'] == 'PEadmin':
        class_name = request.form['class']
        name = request.form['name']
        seat_number = request.form['seat_number']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Students 
            SET class = %s, name = %s, seat_number = %s 
            WHERE student_id = %s
        """, (class_name, name, seat_number, student_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('學生資料已更新')
        return redirect(url_for('import_students'))
    return redirect(url_for('login'))

# 新增學生資料
@app.route('/add_student', methods=['POST'])
def add_student():
    if 'username' in session and session['username'] == 'PEadmin':
        class_name = request.form['class']
        student_id = request.form['student_id']
        name = request.form['name']
        seat_number = request.form['seat_number']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Students (class, student_id, name, seat_number) 
            VALUES (%s, %s, %s, %s)
        """, (class_name, student_id, name, seat_number))
        conn.commit()
        cursor.close()
        conn.close()

        flash('學生已成功新增')
        return redirect(url_for('import_students'))
    return redirect(url_for('login'))

# 刪除所有學生資料
@app.route('/delete_all_students', methods=['POST'])
def delete_all_students():
    if 'username' in session and session['username'] == 'PEadmin':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Students")
        conn.commit()
        cursor.close()
        conn.close()

        flash('所有學生資料已刪除')
        return redirect(url_for('import_students'))
    return redirect(url_for('login'))

# 刪除個別學生資料
@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'username' in session and session['username'] == 'PEadmin':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Students WHERE student_id = %s", (student_id,))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f'學生編號 {student_id} 的資料已刪除')
        return redirect(url_for('import_students'))
    return redirect(url_for('login'))



# 匯出游泳池進出紀錄
@app.route('/export_logs')
def export_logs():
    if 'username' not in session or session['username'] != 'PEadmin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM EntryExitLogs")
    logs = cursor.fetchall()

    df = pd.DataFrame(logs)

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    df.to_excel(writer, index=False, sheet_name='EntryExitLogs')

    worksheet = writer.sheets['EntryExitLogs']
    
    workbook = writer.book

    center_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

    worksheet.set_column('E:E', 17.29, center_format)
    worksheet.set_column(0, len(df.columns) - 1, None, center_format)  

    writer.close()
    output.seek(0)

    cursor.close()
    conn.close()

    return send_file(output, as_attachment=True, download_name="entry_exit_logs.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# 登出功能
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# 匯入教師名單
@app.route('/import_teachers', methods=['GET', 'POST'])
def import_teachers():
    if 'username' in session and session['username'] == 'PEadmin':
        if request.method == 'POST':
            if 'add_teacher' in request.form:
                teacher_id = request.form['teacher_id']
                name = request.form['name']
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Teachers (teacher_id, name) VALUES (%s, %s)", (teacher_id, name))
                conn.commit()
                cursor.close()
                conn.close()
                flash('教師已新增')
                return redirect(url_for('import_teachers'))

            if 'delete_teacher' in request.form:
                teacher_id = request.form['teacher_id']
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Teachers WHERE teacher_id = %s", (teacher_id,))
                conn.commit()
                cursor.close()
                conn.close()
                flash('教師已刪除')
                return redirect(url_for('import_teachers'))

            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)

                    data = pd.read_excel(file_path)

                    conn = get_db_connection()
                    cursor = conn.cursor()
                    for index, row in data.iterrows():
                        cursor.execute("INSERT INTO Teachers (teacher_id, name) VALUES (%s, %s)", 
                                       (row['教師編號'], row['姓名']))
                    conn.commit()
                    cursor.close()
                    conn.close()

                    flash('教師名單已匯入成功')
                    return redirect(url_for('import_teachers'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT teacher_id, name FROM Teachers ORDER BY teacher_id")
        teachers = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('import_teachers.html', teachers=teachers)

    return redirect(url_for('login'))

# 編輯教師
@app.route('/edit_teacher/<int:teacher_id>', methods=['POST'])
def edit_teacher(teacher_id):
    if 'username' in session and session['username'] == 'PEadmin':
        name = request.form['name']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Teachers SET name = %s WHERE teacher_id = %s", (name, teacher_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('教師資料已更新')
        return redirect(url_for('import_teachers'))

    return redirect(url_for('login'))

@app.route('/delete_all_logs', methods=['POST'])  # 確保只允許 POST
def delete_all_logs():
    if 'username' in session and session['username'] == 'PEadmin':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM EntryExitLogs")
        conn.commit()

        # 檢查刪除後是否還有紀錄
        cursor.execute("SELECT COUNT(*) FROM EntryExitLogs")
        remaining_logs = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        if remaining_logs == 0:
            flash('所有游泳池進出紀錄已刪除')
        else:
            flash(f'刪除失敗，仍然有 {remaining_logs} 筆紀錄')

        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(debug=True)
