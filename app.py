import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "edu_pro.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "jiangyue-secure-2026"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


# --- 数据库模型 (保持不变) ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="admin")


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    major = db.Column(db.String(50))
    class_name = db.Column(db.String(50))
    is_deleted = db.Column(db.Boolean, default=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- 路由逻辑 ---


@app.route("/")
@login_required
def dashboard():
    """概览看板"""
    total_stu = Student.query.filter_by(is_deleted=False).count()
    # 聚合图表数据
    m_data = (
        db.session.query(Student.major, func.count(Student.id))
        .filter_by(is_deleted=False)
        .group_by(Student.major)
        .all()
    )
    g_data = (
        db.session.query(Student.gender, func.count(Student.id))
        .filter_by(is_deleted=False)
        .group_by(Student.gender)
        .all()
    )
    return render_template(
        "dashboard.html",
        stats={"total": total_stu, "avg_score": 79.7},
        m_labels=[x[0] for x in m_data],
        m_values=[x[1] for x in m_data],
        g_labels=[x[0] for x in g_data],
        g_values=[x[1] for x in g_data],
    )


@app.route("/students")
@login_required
def student_list():
    """学生管理"""
    page = request.args.get("page", 1, type=int)
    query = Student.query.filter_by(is_deleted=False)
    pagination = query.paginate(page=page, per_page=10)
    return render_template(
        "student/list.html", students=pagination.items, pagination=pagination
    )


@app.route("/grades")  # 修复点：确保与 base.html 链接一致
@login_required
def grade_center():
    """成绩中心：修复页面加载失败"""
    # 逻辑：获取所有未删除学生的成绩（此处可根据需求扩展 Grade 表查询）
    students = Student.query.filter_by(is_deleted=False).all()
    return render_template("grades.html", students=students)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password_hash, request.form["password"]):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("账号或密码错误")
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
