# app.py
from flask import Flask, render_template, redirect, url_for, request
from config import Config
from extensions import db, login_manager
from flask_login import login_user, login_required, logout_user, current_user
from models import User, Student, Course, Enrollment, Attendance, Grade
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# STUDENT management
@app.route('/students', methods=['GET', 'POST'])
@login_required
def manage_students():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        grade = float(request.form['grade'])
        student = Student(name=name, age=age, grade=grade)
        db.session.add(student)
        db.session.commit()
    students = Student.query.all()
    return render_template('students.html', students=students)

@app.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('manage_students'))

# COURSE management
@app.route('/courses', methods=['GET', 'POST'])
@login_required
def manage_courses():
    if request.method == 'POST':
        title = request.form['title']
        code = request.form['code']
        course = Course(title=title, code=code)
        db.session.add(course)
        db.session.commit()
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('manage_courses'))

# ENROLLMENTS
@app.route('/enrollments', methods=['GET', 'POST'])
@login_required
def manage_enrollments():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
    students = Student.query.all()
    courses = Course.query.all()
    enrollments = Enrollment.query.all()
    return render_template('enrollments.html', enrollments=enrollments, students=students, courses=courses)

# ATTENDANCE
@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def manage_attendance():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        status = request.form['status']
        attendance = Attendance(student_id=student_id, course_id=course_id, status=status)
        db.session.add(attendance)
        db.session.commit()
    students = Student.query.all()
    courses = Course.query.all()
    attendance_records = Attendance.query.join(Attendance.student).join(Attendance.course).all()
    for a in attendance_records:
        if a and a.student and a.course:
            print(a.student.name, a.course.title)
    return render_template('attendance.html', attendance=attendance_records, students=students, courses=courses)

# GRADES
@app.route('/grades', methods=['GET', 'POST'])
@login_required
def manage_grades():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        score = float(request.form['score'])
        grade = Grade(student_id=student_id, course_id=course_id, score=score)
        db.session.add(grade)
        db.session.commit()
    students = Student.query.all()
    courses = Course.query.all()
    grades = Grade.query.all()
    return render_template('grades.html', grades=grades, students=students, courses=courses)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # 👤 Create a test admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')  # Password: admin123
            db.session.add(admin)
            db.session.commit()
            print("✔ Created default admin user: username='admin', password='admin123'")
app.run(debug=True)
