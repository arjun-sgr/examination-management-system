# database.py - SQLite operations used by the examination system.
import sqlite3
from pathlib import Path
from grade_utils import calculate_grade

DB_FILE = Path(__file__).with_name("examination_management.db")

class Database:
    def __init__(self, db_path=DB_FILE):
        self.db_path = str(db_path)
        self.create_tables()

    def connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def create_tables(self):
        with self.connect() as con:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS students (
                    roll_no TEXT PRIMARY KEY, name TEXT NOT NULL,
                    branch TEXT NOT NULL, semester INTEGER NOT NULL,
                    email TEXT DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS exams (
                    exam_code TEXT PRIMARY KEY, subject TEXT NOT NULL,
                    semester INTEGER NOT NULL, exam_date TEXT NOT NULL,
                    max_marks REAL NOT NULL CHECK(max_marks > 0)
                );
                CREATE TABLE IF NOT EXISTS results (
                    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_no TEXT NOT NULL, exam_code TEXT NOT NULL,
                    marks REAL NOT NULL CHECK(marks >= 0),
                    percentage REAL NOT NULL, grade TEXT NOT NULL,
                    status TEXT NOT NULL, UNIQUE(roll_no, exam_code),
                    FOREIGN KEY(roll_no) REFERENCES students(roll_no) ON DELETE CASCADE,
                    FOREIGN KEY(exam_code) REFERENCES exams(exam_code) ON DELETE CASCADE
                );
            """)

    # Student operations
    def add_student(self, roll_no, name, branch, semester, email=''):
        with self.connect() as con:
            con.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)",
                        (roll_no, name, branch, semester, email))

    def get_students(self, search=''):
        pattern = f"%{search.strip()}%"
        with self.connect() as con:
            return con.execute("""SELECT roll_no, name, branch, semester, email
                FROM students WHERE roll_no LIKE ? OR name LIKE ? OR branch LIKE ?
                ORDER BY roll_no""", (pattern, pattern, pattern)).fetchall()

    def delete_student(self, roll_no):
        with self.connect() as con:
            cur = con.execute("DELETE FROM students WHERE roll_no=?", (roll_no,))
            return cur.rowcount > 0

    # Examination operations
    def add_exam(self, exam_code, subject, semester, exam_date, max_marks):
        with self.connect() as con:
            con.execute("INSERT INTO exams VALUES (?, ?, ?, ?, ?)",
                        (exam_code, subject, semester, exam_date, max_marks))

    def get_exams(self, search=''):
        pattern = f"%{search.strip()}%"
        with self.connect() as con:
            return con.execute("""SELECT exam_code, subject, semester, exam_date, max_marks
                FROM exams WHERE exam_code LIKE ? OR subject LIKE ?
                ORDER BY exam_date, exam_code""", (pattern, pattern)).fetchall()

    def delete_exam(self, exam_code):
        with self.connect() as con:
            cur = con.execute("DELETE FROM exams WHERE exam_code=?", (exam_code,))
            return cur.rowcount > 0

    # Result operations
    @staticmethod
    def calculate_result(marks, maximum):
        return calculate_grade(marks, maximum)

    def save_result(self, roll_no, exam_code, marks):
        with self.connect() as con:
            student = con.execute("SELECT roll_no FROM students WHERE roll_no=?", (roll_no,)).fetchone()
            if student is None:
                raise ValueError('Student roll number was not found.')
            exam = con.execute("SELECT max_marks FROM exams WHERE exam_code=?", (exam_code,)).fetchone()
            if exam is None:
                raise ValueError('Exam code was not found.')
            maximum = float(exam['max_marks'])
            if marks < 0 or marks > maximum:
                raise ValueError(f'Marks must be between 0 and {maximum:g}.')
            percentage, grade, status = self.calculate_result(marks, maximum)
            con.execute("""INSERT INTO results (roll_no, exam_code, marks, percentage, grade, status)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(roll_no, exam_code) DO UPDATE SET
                marks=excluded.marks, percentage=excluded.percentage,
                grade=excluded.grade, status=excluded.status""",
                (roll_no, exam_code, marks, percentage, grade, status))
            return percentage, grade, status, maximum

    def get_results(self, search=''):
        pattern = f"%{search.strip()}%"
        with self.connect() as con:
            return con.execute("""SELECT r.roll_no, s.name, s.branch, r.exam_code, e.subject,
                r.marks, e.max_marks, r.percentage, r.grade, r.status
                FROM results r JOIN students s ON s.roll_no=r.roll_no
                JOIN exams e ON e.exam_code=r.exam_code
                WHERE r.roll_no LIKE ? OR s.name LIKE ? OR r.exam_code LIKE ? OR e.subject LIKE ?
                ORDER BY r.exam_code, r.roll_no""",
                (pattern, pattern, pattern, pattern)).fetchall()

    def delete_result(self, roll_no, exam_code):
        with self.connect() as con:
            cur = con.execute("DELETE FROM results WHERE roll_no=? AND exam_code=?",
                              (roll_no, exam_code))
            return cur.rowcount > 0

    def load_demo_data(self):
        students = [
            ('IT001','Aarav Patel','IT-A',4,'aarav@example.com'),
            ('IT002','Diya Shah','IT-A',4,'diya@example.com'),
            ('IT003','Vivaan Desai','IT-B',4,'vivaan@example.com'),
            ('IT004','Anaya Mehta','IT-B',4,'anaya@example.com'),
            ('IT005','Arjun Joshi','IT-A',4,'arjun@example.com'),
            ('IT006','Ishita Rao','IT-B',4,'ishita@example.com'),
        ]
        exams = [
            ('DAA401','Design and Analysis of Algorithms',4,'2026-11-10',100),
            ('PY402','Python Programming',4,'2026-11-12',100),
            ('DB403','Database Management Systems',4,'2026-11-15',100),
        ]
        with self.connect() as con:
            con.executemany("INSERT OR IGNORE INTO students VALUES (?, ?, ?, ?, ?)", students)
            con.executemany("INSERT OR IGNORE INTO exams VALUES (?, ?, ?, ?, ?)", exams)
        results = [('IT001','DAA401',86),('IT002','DAA401',74),('IT003','DAA401',39),
                   ('IT004','DAA401',91),('IT005','PY402',78),('IT006','PY402',64),
                   ('IT001','DB403',88),('IT003','DB403',52)]
        for roll, code, marks in results:
            self.save_result(roll, code, marks)
