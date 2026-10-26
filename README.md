# Examination Management System

A beginner-friendly Python mini-project built with Tkinter and SQLite.

## Features
- Add, search and delete student records.
- Add and delete examination schedules.
- Record or update a student's marks for an exam.
- Automatically calculate percentage, grade and Pass/Fail status.
- Search result records and export results to CSV.
- Keep records in a local SQLite database between program runs.
- Load sample records for a quick demonstration.

## Files
- `main.py` - starts the program.
- `gui.py` - buttons, forms, tables and interface actions.
- `database.py` - database tables and storage functions.
- `grade_utils.py` - simple grade calculation function.

## Requirements
Python 3.x with Tkinter and SQLite support. These are included in a typical Python installation; no pip packages are required.

## Run on Windows
1. Extract the project ZIP.
2. Open the `source` folder in VS Code.
3. Open Terminal and run:

```bash
python main.py
```

The database file `examination_management.db` is created next to `database.py` automatically.

## First demo
1. Run `main.py`.
2. Click `Load Demo Data`.
3. Check Students, Examination Schedule, and Marks & Results tabs.
4. Add a student, add an exam, or save marks for a valid roll number and exam code.
5. Search results and export the list to CSV.

## Demo grade scheme
A+ >= 90%, A >= 80%, B+ >= 70%, B >= 60%, C >= 50%, D >= 40%, F < 40%. Pass threshold: 40%.

These are illustrative project rules and may not match the official university grading policy. Replace them with the approved rules if required.

## Database tables
- `students(roll_no, name, branch, semester, email)`
- `exams(exam_code, subject, semester, exam_date, max_marks)`
- `results(roll_no, exam_code, marks, percentage, grade, status)`

Each student/exam combination can have one result. Saving the same combination again updates the existing result.

## Limitations
The application is designed as a local, single-user mini-project. It does not include login roles, online exam delivery, cloud synchronization or question-paper generation.
