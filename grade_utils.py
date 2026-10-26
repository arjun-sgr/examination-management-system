# grade_utils.py - reusable grade calculation helper.

def calculate_grade(marks, maximum):
    if maximum <= 0:
        raise ValueError('Maximum marks must be greater than zero.')
    if marks < 0 or marks > maximum:
        raise ValueError('Marks must be between zero and maximum marks.')
    percentage = round(marks / maximum * 100, 2)
    if percentage >= 90: grade = 'A+'
    elif percentage >= 80: grade = 'A'
    elif percentage >= 70: grade = 'B+'
    elif percentage >= 60: grade = 'B'
    elif percentage >= 50: grade = 'C'
    elif percentage >= 40: grade = 'D'
    else: grade = 'F'
    return percentage, grade, ('PASS' if percentage >= 40 else 'FAIL')
