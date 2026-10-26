# main.py - program entry point.
import tkinter as tk
from gui import ExaminationManagementApp

if __name__ == '__main__':
    root = tk.Tk()
    app = ExaminationManagementApp(root)
    root.mainloop()
