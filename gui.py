# gui.py - Tkinter user interface for the Examination Management System.

import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from database import Database

APP_TITLE = 'Examination Management System'


class ExaminationManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry('1200x780')
        self.root.minsize(1000, 680)
        self.database = Database()
        self._build_interface()
        self.refresh_all()

    def _build_interface(self):
        style = ttk.Style(self.root)
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        style.configure('TFrame', background='#f4f6f8')
        style.configure('TLabel', background='#f4f6f8', foreground='#263746')
        style.configure('TLabelframe', background='#f4f6f8')
        style.configure('TLabelframe.Label', background='#f4f6f8', foreground='#183b56', font=('Segoe UI', 10, 'bold'))
        style.configure('TNotebook.Tab', padding=(12, 7), font=('Segoe UI', 10))
        style.configure('Treeview', rowheight=25, font=('Segoe UI', 9))
        style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'))

        header = tk.Frame(self.root, bg='#183b56', padx=16, pady=13)
        header.pack(fill='x')
        tk.Label(header, text=APP_TITLE, font=('Segoe UI', 21, 'bold'),
                 bg='#183b56', fg='white').pack(anchor='w')
        tk.Label(header,
                 text='Manage students, examinations, marks and results in one place',
                 font=('Segoe UI', 10), bg='#183b56', fg='#dce8f0').pack(anchor='w', pady=(3, 0))

        toolbar = ttk.Frame(self.root, padding=(12, 8))
        toolbar.pack(fill='x')
        ttk.Button(toolbar, text='Load Demo Data', command=self.load_demo_data).pack(side='left', padx=(0, 8))
        ttk.Button(toolbar, text='Refresh All', command=self.refresh_all).pack(side='left')
        ttk.Label(toolbar, text='Data is stored locally in examination_management.db',
                  foreground='#536273').pack(side='right')

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill='both', expand=True, padx=12, pady=(0, 8))
        self.students_tab = ttk.Frame(self.tabs, padding=10)
        self.exams_tab = ttk.Frame(self.tabs, padding=10)
        self.results_tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(self.students_tab, text='Students')
        self.tabs.add(self.exams_tab, text='Examination Schedule')
        self.tabs.add(self.results_tab, text='Marks & Results')

        self._build_students_tab()
        self._build_exams_tab()
        self._build_results_tab()

        self.status_var = tk.StringVar(value='Ready')
        ttk.Label(self.root, textvariable=self.status_var, relief='sunken',
                  anchor='w', padding=(8, 4)).pack(fill='x', side='bottom')

    @staticmethod
    def _make_table(parent, columns, headings, widths, height=12):
        frame = ttk.Frame(parent)
        frame.pack(fill='both', expand=True, pady=(8, 0))
        table = ttk.Treeview(frame, columns=columns, show='headings', height=height)
        centered = {'roll_no', 'semester', 'exam_code', 'exam_date', 'marks', 'max_marks', 'percentage', 'grade', 'status'}
        for column, heading, width in zip(columns, headings, widths):
            table.heading(column, text=heading)
            table.column(column, width=width, anchor=('center' if column in centered else 'w'))
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        return table

    # ---------------- STUDENTS ----------------
    def _build_students_tab(self):
        form = ttk.LabelFrame(self.students_tab, text='Add Student', padding=10)
        form.pack(fill='x')
        self.student_roll = tk.StringVar()
        self.student_name = tk.StringVar()
        self.student_branch = tk.StringVar(value='IT-A')
        self.student_semester = tk.StringVar(value='4')
        self.student_email = tk.StringVar()
        fields = [
            ('Roll Number', self.student_roll, 13),
            ('Student Name', self.student_name, 20),
            ('Branch / Division', self.student_branch, 12),
            ('Semester', self.student_semester, 7),
            ('Email (optional)', self.student_email, 22),
        ]
        for i, (label, variable, width) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=i, sticky='w', padx=5)
            ttk.Entry(form, textvariable=variable, width=width).grid(row=1, column=i, sticky='ew', padx=5, pady=(3, 8))
        ttk.Button(form, text='Add Student', command=self.add_student).grid(row=1, column=5, padx=8, pady=(3, 8))
        ttk.Button(form, text='Delete Selected', command=self.delete_student).grid(row=1, column=6, padx=5, pady=(3, 8))

        search = ttk.Frame(self.students_tab)
        search.pack(fill='x', pady=(10, 0))
        ttk.Label(search, text='Search by roll, name or branch:').pack(side='left')
        self.student_search = tk.StringVar()
        ttk.Entry(search, textvariable=self.student_search, width=28).pack(side='left', padx=8)
        ttk.Button(search, text='Search', command=self.refresh_students).pack(side='left')
        ttk.Button(search, text='Show All', command=self._clear_student_search).pack(side='left', padx=5)

        self.student_table = self._make_table(
            self.students_tab,
            ('roll_no', 'name', 'branch', 'semester', 'email'),
            ('Roll Number', 'Student Name', 'Branch / Division', 'Semester', 'Email'),
            (120, 220, 145, 90, 220)
        )

    def add_student(self):
        roll = self.student_roll.get().strip().upper()
        name = self.student_name.get().strip()
        branch = self.student_branch.get().strip().upper()
        email = self.student_email.get().strip()
        try:
            semester = int(self.student_semester.get())
            if not roll or not name or not branch:
                raise ValueError('Please enter roll number, name and branch.')
            if not 1 <= semester <= 8:
                raise ValueError('Semester must be from 1 to 8.')
            self.database.add_student(roll, name, branch, semester, email)
        except ValueError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return
        except Exception as error:
            messagebox.showerror(APP_TITLE, f'Could not add student.\n{error}')
            return
        self.student_roll.set('')
        self.student_name.set('')
        self.student_email.set('')
        self.refresh_students()
        self.refresh_results()
        self.status_var.set(f'Student {roll} added successfully.')

    def delete_student(self):
        selected = self.student_table.selection()
        if not selected:
            messagebox.showinfo(APP_TITLE, 'Select a student from the table first.')
            return
        roll = self.student_table.item(selected[0], 'values')[0]
        if not messagebox.askyesno(APP_TITLE, f'Delete student {roll}? Its results will also be deleted.'):
            return
        self.database.delete_student(roll)
        self.refresh_all()
        self.status_var.set(f'Student {roll} deleted.')

    def _clear_student_search(self):
        self.student_search.set('')
        self.refresh_students()

    def refresh_students(self):
        for item in self.student_table.get_children():
            self.student_table.delete(item)
        for row in self.database.get_students(self.student_search.get()):
            self.student_table.insert('', 'end', values=tuple(row))

    # ---------------- EXAMINATIONS ----------------
    def _build_exams_tab(self):
        form = ttk.LabelFrame(self.exams_tab, text='Create Examination', padding=10)
        form.pack(fill='x')
        self.exam_code = tk.StringVar()
        self.exam_subject = tk.StringVar()
        self.exam_semester = tk.StringVar(value='4')
        self.exam_date = tk.StringVar(value='2026-11-10')
        self.exam_max = tk.StringVar(value='100')
        fields = [
            ('Exam Code', self.exam_code, 12),
            ('Subject Name', self.exam_subject, 25),
            ('Semester', self.exam_semester, 8),
            ('Exam Date (YYYY-MM-DD)', self.exam_date, 16),
            ('Maximum Marks', self.exam_max, 12),
        ]
        for i, (label, variable, width) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=i, sticky='w', padx=5)
            ttk.Entry(form, textvariable=variable, width=width).grid(row=1, column=i, sticky='ew', padx=5, pady=(3, 8))
        ttk.Button(form, text='Add Exam', command=self.add_exam).grid(row=1, column=5, padx=7, pady=(3, 8))
        ttk.Button(form, text='Delete Selected', command=self.delete_exam).grid(row=1, column=6, padx=5, pady=(3, 8))

        search = ttk.Frame(self.exams_tab)
        search.pack(fill='x', pady=(10, 0))
        ttk.Label(search, text='Search by code or subject:').pack(side='left')
        self.exam_search = tk.StringVar()
        ttk.Entry(search, textvariable=self.exam_search, width=28).pack(side='left', padx=8)
        ttk.Button(search, text='Search', command=self.refresh_exams).pack(side='left')
        ttk.Button(search, text='Show All', command=self._clear_exam_search).pack(side='left', padx=5)

        self.exam_table = self._make_table(
            self.exams_tab,
            ('exam_code', 'subject', 'semester', 'exam_date', 'max_marks'),
            ('Exam Code', 'Subject', 'Semester', 'Date', 'Maximum Marks'),
            (130, 340, 100, 150, 140)
        )
        ttk.Label(self.exams_tab, text='Dates must use YYYY-MM-DD format (example: 2026-11-10).',
                  foreground='#536273').pack(anchor='w', pady=(7, 0))

    def add_exam(self):
        code = self.exam_code.get().strip().upper()
        subject = self.exam_subject.get().strip()
        date_text = self.exam_date.get().strip()
        try:
            semester = int(self.exam_semester.get())
            maximum = float(self.exam_max.get())
            datetime.strptime(date_text, '%Y-%m-%d')
            if not code or not subject:
                raise ValueError('Please enter exam code and subject name.')
            if not 1 <= semester <= 8:
                raise ValueError('Semester must be between 1 and 8.')
            if maximum <= 0:
                raise ValueError('Maximum marks must be greater than zero.')
            self.database.add_exam(code, subject, semester, date_text, maximum)
        except ValueError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return
        except Exception as error:
            messagebox.showerror(APP_TITLE, f'Could not add examination.\n{error}')
            return
        self.exam_code.set('')
        self.exam_subject.set('')
        self.refresh_exams()
        self.refresh_results()
        self.status_var.set(f'Examination {code} added successfully.')

    def delete_exam(self):
        selected = self.exam_table.selection()
        if not selected:
            messagebox.showinfo(APP_TITLE, 'Select an examination first.')
            return
        code = self.exam_table.item(selected[0], 'values')[0]
        if not messagebox.askyesno(APP_TITLE, f'Delete examination {code}? Its results will also be deleted.'):
            return
        self.database.delete_exam(code)
        self.refresh_all()
        self.status_var.set(f'Examination {code} deleted.')

    def _clear_exam_search(self):
        self.exam_search.set('')
        self.refresh_exams()

    def refresh_exams(self):
        for item in self.exam_table.get_children():
            self.exam_table.delete(item)
        for row in self.database.get_exams(self.exam_search.get()):
            self.exam_table.insert('', 'end', values=tuple(row))

    # ---------------- MARKS AND RESULTS ----------------
    def _build_results_tab(self):
        form = ttk.LabelFrame(self.results_tab, text='Record / Update Student Result', padding=10)
        form.pack(fill='x')
        self.result_roll = tk.StringVar()
        self.result_exam_code = tk.StringVar()
        self.result_marks = tk.StringVar()
        for column, label, variable, width in [
            (0, 'Student Roll Number', self.result_roll, 18),
            (1, 'Exam Code', self.result_exam_code, 18),
            (2, 'Marks Obtained', self.result_marks, 14),
        ]:
            ttk.Label(form, text=label).grid(row=0, column=column, padx=6, sticky='w')
            ttk.Entry(form, textvariable=variable, width=width).grid(row=1, column=column, padx=6, pady=(3, 8))
        ttk.Button(form, text='Save / Update Result', command=self.save_result).grid(row=1, column=3, padx=7, pady=(3, 8))
        ttk.Button(form, text='Delete Result', command=self.delete_result).grid(row=1, column=4, padx=5, pady=(3, 8))
        ttk.Button(form, text='Export CSV', command=self.export_results).grid(row=1, column=5, padx=5, pady=(3, 8))

        search = ttk.Frame(self.results_tab)
        search.pack(fill='x', pady=(10, 0))
        ttk.Label(search, text='Search by roll, name, exam or subject:').pack(side='left')
        self.result_search = tk.StringVar()
        ttk.Entry(search, textvariable=self.result_search, width=28).pack(side='left', padx=8)
        ttk.Button(search, text='Search', command=self.refresh_results).pack(side='left')
        ttk.Button(search, text='Show All', command=self._clear_result_search).pack(side='left', padx=5)

        self.result_table = self._make_table(
            self.results_tab,
            ('roll_no', 'name', 'branch', 'exam_code', 'subject', 'marks', 'max_marks', 'percentage', 'grade', 'status'),
            ('Roll No', 'Student', 'Branch', 'Exam Code', 'Subject', 'Marks', 'Max', '%', 'Grade', 'Result'),
            (85, 140, 85, 100, 230, 65, 65, 65, 65, 70), height=12
        )
        ttk.Label(self.results_tab,
                  text='Demo grading: A+ ≥ 90%, A ≥ 80%, B+ ≥ 70%, B ≥ 60%, C ≥ 50%, D ≥ 40%, F < 40%. Pass threshold: 40%.',
                  foreground='#536273', wraplength=1060).pack(anchor='w', pady=(7, 0))

    def save_result(self):
        roll = self.result_roll.get().strip().upper()
        code = self.result_exam_code.get().strip().upper()
        try:
            if not roll or not code:
                raise ValueError('Enter both student roll number and exam code.')
            marks = float(self.result_marks.get())
            percentage, grade, status, maximum = self.database.save_result(roll, code, marks)
        except ValueError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return
        except Exception as error:
            messagebox.showerror(APP_TITLE, f'Could not save result.\n{error}')
            return
        self.refresh_results()
        self.status_var.set(f'{roll} / {code}: {marks:g}/{maximum:g}, {percentage:.2f}%, Grade {grade}, {status}.')
        messagebox.showinfo(APP_TITLE, f'Result saved.\nPercentage: {percentage:.2f}%\nGrade: {grade}\nStatus: {status}')

    def delete_result(self):
        selected = self.result_table.selection()
        if not selected:
            messagebox.showinfo(APP_TITLE, 'Select a result row first.')
            return
        values = self.result_table.item(selected[0], 'values')
        roll, code = values[0], values[3]
        if not messagebox.askyesno(APP_TITLE, f'Delete result for {roll} in {code}?'):
            return
        self.database.delete_result(roll, code)
        self.refresh_results()
        self.status_var.set(f'Result deleted for {roll} / {code}.')

    def _clear_result_search(self):
        self.result_search.set('')
        self.refresh_results()

    def refresh_results(self):
        if not hasattr(self, 'result_table'):
            return
        for item in self.result_table.get_children():
            self.result_table.delete(item)
        for row in self.database.get_results(self.result_search.get()):
            values = (row['roll_no'], row['name'], row['branch'], row['exam_code'], row['subject'],
                      f"{row['marks']:g}", f"{row['max_marks']:g}", f"{row['percentage']:.2f}", row['grade'], row['status'])
            self.result_table.insert('', 'end', values=values)

    def export_results(self):
        rows = self.database.get_results(self.result_search.get())
        if not rows:
            messagebox.showwarning(APP_TITLE, 'There are no results to export.')
            return
        path = filedialog.asksaveasfilename(title='Export Examination Results', defaultextension='.csv',
                                            filetypes=[('CSV files', '*.csv')])
        if not path:
            return
        with open(path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Roll Number', 'Student Name', 'Branch', 'Exam Code', 'Subject',
                             'Marks Obtained', 'Maximum Marks', 'Percentage', 'Grade', 'Status'])
            for row in rows:
                writer.writerow([row['roll_no'], row['name'], row['branch'], row['exam_code'], row['subject'],
                                 row['marks'], row['max_marks'], row['percentage'], row['grade'], row['status']])
        messagebox.showinfo(APP_TITLE, f'Results exported to:\n{path}')

    # ---------------- SHARED ----------------
    def load_demo_data(self):
        try:
            self.database.load_demo_data()
            self.refresh_all()
            self.status_var.set('Demo students, exams and results loaded.')
            messagebox.showinfo(APP_TITLE, 'Demo data loaded. Existing records were kept; sample IDs are added if missing.')
        except Exception as error:
            messagebox.showerror(APP_TITLE, f'Could not load demo data.\n{error}')

    def refresh_all(self):
        if hasattr(self, 'student_table'):
            self.refresh_students()
        if hasattr(self, 'exam_table'):
            self.refresh_exams()
        if hasattr(self, 'result_table'):
            self.refresh_results()
