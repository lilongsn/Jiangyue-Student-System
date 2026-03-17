import random
from app import app, db, Student, User
from werkzeug.security import generate_password_hash


def seed():
    with app.app_context():
        print("正在清理旧数据库...")
        db.drop_all()
        db.create_all()

        # 1. 创建管理员
        admin = User(username="admin", password_hash=generate_password_hash("123456"))
        db.session.add(admin)

        # 2. 生成 100 条数据
        MAJORS = ["计算机科学", "人工智能", "软件工程"]
        SURNAMES = ["王", "李", "张", "刘", "陈"]
        print("正在注入 100 条测试档案...")

        for i in range(100):
            stu = Student(
                student_id=f"2026{str(i+1).zfill(4)}",
                name=random.choice(SURNAMES) + random.choice(["伟", "芳", "杰", "敏"]),
                gender=random.choice(["男", "女"]),
                major=random.choice(MAJORS),
                class_name=f"260{random.randint(1,4)}班",
                is_deleted=False,
            )
            db.session.add(stu)

        db.session.commit()
        print("✅ 数据注入成功！账号 admin 密码 123456")


if __name__ == "__main__":
    seed()
