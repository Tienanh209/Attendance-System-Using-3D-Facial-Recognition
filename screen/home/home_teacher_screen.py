from time import strftime
from datetime import datetime
from tkinter import *
from PIL import ImageTk, Image
from screen.student_view.student_view_screen import student_view
from screen.manage_attendance.manage_attendance_screen1_3d_drawYellow import attendance
from screen.manage_attendance.statistic_screen import statisticExcel
from screen.train_model.train_model_from_images_screen import traindata
import os
import json
import mysql.connector

class HomeScreenTeacher:
    def __init__(self, root):
        self.root = root

        # Đọc thông tin từ config.json
        self.teacher_id = self.load_teacher_id()
        self.teacher_name = self.get_teacher_name(self.teacher_id)

        self.root.geometry('925x600')
        self.root.title('Hệ thống điểm danh nhận dạng khuôn mặt 3D')

        #======= background
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(BASE_DIR, '..', '..', 'assets', 'ImageDesign', 'bg_home_teacher.jpg')
        img = Image.open(img_path)
        img = img.resize((930, 605))
        self.imgtk = ImageTk.PhotoImage(img)
        lbl_bg = Label(self.root, image=self.imgtk, bg='white', width=930, height=605)
        lbl_bg.place(x=-5, y=-5)

        #========== heading
        lbl_name = Label(self.root, bg="white", text=self.teacher_name, font=("yu gothic ui", 20, "bold"),
                         fg="#57a1f8", bd=0)
        lbl_name.place(x=110, y=137)

        #=== timeline
        lbl_time = Label(self.root, bg="white", text="", font=("yu gothic ui", 20, "bold"),
                         fg="#57a1f8", bd=0)
        lbl_time.place(x=154, y=502)
        self.update_time(lbl_time)

        lbl_date = Label(self.root, bg="white", text="", font=("yu gothic ui", 20, "bold"),
                         fg="#57a1f8", bd=0)
        lbl_date.place(x=138, y=532)
        self.update_date(lbl_date)

        #=== logout
        btn_logout = Button(self.root, text="Thoát", command=self.logout, font=("yu gothic ui", 20, "bold"), bg="white", fg="#57a1f8", borderwidth=0)
        btn_logout.place(x=817, y=92, width=90, height=23)

        #======= body
        # ==== student
        BASE_DIR2 = os.path.dirname(os.path.abspath(__file__))
        img_student_path = os.path.join(BASE_DIR2, '..', '..', 'assets', 'ImageDesign', 'list.png')
        img_student = Image.open(img_student_path)
        img_student = img_student.resize((150, 150), Image.Resampling.LANCZOS)
        self.img_studenttk = ImageTk.PhotoImage(img_student)
        btn_student = Button(self.root, text="Danh sách sinh viên", font=("yu gothic ui", 14, "bold"), command=lambda: self.student_view(self.root),
                             image=self.img_studenttk, activebackground="white", bg="white", borderwidth=0,
                             compound="top")
        btn_student.place(x=73, y=255, width=194, height=194)

        # === recognize
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_recognize_path = os.path.join(BASE_DIR, '..', '..', 'assets', 'ImageDesign', 'attendance.png')
        img_recognize = Image.open(img_recognize_path)
        img_recognize = img_recognize.resize((140, 140), Image.Resampling.LANCZOS)
        self.img_recognizetk = ImageTk.PhotoImage(img_recognize)
        btn_recognize = Button(self.root, text="Điểm danh", font=("yu gothic ui", 14, "bold"), command=self.attendance,
                               image=self.img_recognizetk, activebackground="white", bg="white", borderwidth=0,
                               compound="top")
        btn_recognize.place(x=361, y=255, width=194, height=194)

        # ==== report
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_report_path = os.path.join(BASE_DIR, '..', '..', 'assets', 'ImageDesign', 'report.png')
        img_report = Image.open(img_report_path)
        img_report = img_report.resize((140, 140), Image.Resampling.LANCZOS)
        self.img_reporttk = ImageTk.PhotoImage(img_report)
        btn_report = Button(self.root, text="Thống kê", font=("yu gothic ui", 14, "bold"), command=self.open_statistic_window,
                            image=self.img_reporttk, activebackground="white", bg="white", borderwidth=0,
                            compound="top")
        btn_report.place(x=649, y=255, width=194, height=194)

    def update_time(self, lbl_time):
        current_time = datetime.now().strftime('%H:%M:%S')
        lbl_time.config(text=current_time)
        self.root.after(1000, lambda: self.update_time(lbl_time))

    def update_date(self, lbl_date):
        current_date = datetime.now().strftime('%Y-%m-%d')
        lbl_date.config(text=current_date)

    def student_view(self, root):
        self.new_window = Toplevel(root)
        self.app = student_view(self.new_window)

    def attendance(self):
        self.new_window = Toplevel(self.root)
        self.app = attendance(self.new_window)

    def traindata(self):
        self.new_window = Toplevel(self.root)
        self.app = traindata(self.new_window)

    def load_teacher_id(self):
        config_file = "../login/config.json"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                try:
                    config_data = json.load(f)
                    teacher_id = config_data.get("id_teacher", "Unknown")  # Sửa "teacher_id" thành "id_teacher" để khớp với config.json
                    print(f"Teacher ID from config: {teacher_id}")  # Debug
                    return teacher_id
                except json.JSONDecodeError:
                    print("Error decoding JSON")
                    return "Unknown"
        else:
            print("Config file not found")
            return "Unknown"

    def get_teacher_name(self, teacher_id):
        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys', port='3306')
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT name_teacher FROM teacher WHERE id_teacher=%s", (teacher_id,))
            row = my_cursor.fetchone()
            conn.close()
            if row and row[0] is not None:
                print(f"Teacher name found: {row[0]}")  # Debug
                return row[0]
            print("Teacher name not found or is NULL")
            return 'Unknown'
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            return 'Unknown'

    def logout(self):
        if os.path.exists('../login/config.json'):
            with open('../login/config.json', 'w') as f:
                f.write('{}')
        self.root.destroy()

    def open_statistic_window(self):
        new_window = Toplevel(self.root)
        app = statisticExcel(new_window)

def main():
    root = Tk()
    app = HomeScreenTeacher(root)
    root.mainloop()

if __name__ == "__main__":
    main()