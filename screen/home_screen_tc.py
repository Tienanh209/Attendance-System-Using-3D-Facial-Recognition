from time import strftime
from datetime import datetime
from tkinter import *
from PIL import ImageTk, Image
from screen.manage_attendance.manage_attendance_screen import attendance
from screen.train_model_screen import  traindata
from screen.student_view.student_view_screen import Student_View
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
        self.root.title('Facial Recognition Attendance System')

        today = strftime('%d-%m-%Y')

        #======= background
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(BASE_DIR, '..', 'assets', 'ImageDesign', 'bg_home_teacher.jpg')
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
        btn_logout = Button(self.root, text="Log out", command=self.logout, font=("yu gothic ui", 20, "bold"), bg="white", fg="#57a1f8", borderwidth=0)
        btn_logout.place(x=817, y=92, width=90, height=23)

        #======= body

        # ==== student

        BASE_DIR2 = os.path.dirname(os.path.abspath(__file__))  # Lấy đường dẫn tuyệt đối của file hiện tại
        img_student_path = os.path.join(BASE_DIR2, '..', 'assets', 'ImageDesign', 'list.png')

        img_student = Image.open(img_student_path)
        img_student = img_student.resize((150, 150), Image.Resampling.LANCZOS)

        self.img_studenttk = ImageTk.PhotoImage(img_student)
        btn_student = Button(self.root, text="Student List", font=("yu gothic ui", 14, "bold"), command=lambda: self.student_view(self.root),
                             image=self.img_studenttk, activebackground="white", bg="white", borderwidth=0,
                             compound="top")
        btn_student.place(x=73, y=255, width=194, height=194)

        # === recognize
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_recognize_path = os.path.join(BASE_DIR, '..', 'assets', 'ImageDesign', 'attendance.png')
        img_recognize_path = os.path.abspath(img_recognize_path)  # Chuẩn hóa thành đường dẫn tuyệt đối

        if not os.path.exists(img_recognize_path):
            print("File không tồn tại:", img_recognize_path)

        img_recognize = Image.open(img_recognize_path)
        img_recognize = img_recognize.resize((140, 140), Image.Resampling.LANCZOS)

        self.img_recognizetk = ImageTk.PhotoImage(img_recognize)
        btn_recognize = Button(self.root, text="Attendance", font=("yu gothic ui", 14, "bold"), command=self.attendance,
                               image=self.img_recognizetk, activebackground="white", bg="white", borderwidth=0,
                               compound="top")
        btn_recognize.place(x=361, y=255, width=194, height=194)

        # ==== report
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_report_path = os.path.join(BASE_DIR, '..', 'assets', 'ImageDesign', 'report.png')
        img_report_path = os.path.abspath(img_report_path)  # Chuẩn hóa thành đường dẫn tuyệt đối

        if not os.path.exists(img_report_path):
            print("File không tồn tại:", img_report_path)

        img_report = Image.open(img_report_path)
        img_report = img_report.resize((140, 140), Image.Resampling.LANCZOS)

        self.img_reporttk = ImageTk.PhotoImage(img_report)
        btn_report = Button(self.root, text="Report", font=("yu gothic ui", 14, "bold"), command="",
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
        self.app = Student_View(self.new_window)
    def attendance(self):
        self.new_window = Toplevel(self.root)
        self.app = attendance(self.new_window)
    def traindata(self):
        self.new_window = Toplevel(self.root)
        self.app = traindata(self.new_window)


    def load_teacher_id(self):
        config_file = "login/config.json"

        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                try:
                    config_data = json.load(f)
                    return config_data.get("teacher_id", "Unknown")  # Trả về teacher_id hoặc 'Unknown'
                except json.JSONDecodeError:
                    return "Unknown"
        else:
            return "Unknown"

    def get_teacher_name(self, teacher_id):
        # Kết nối đến cơ sở dữ liệu để lấy tên giáo viên
        conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys', port='3306')
        my_cursor = conn.cursor()
        my_cursor.execute("SELECT name_teacher FROM teacher WHERE id_teacher=%s", (teacher_id,))
        row = my_cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        return 'Unknown'

    def logout(self):
        # Xóa nội dung của tệp config.json mà không xóa tệp
        if os.path.exists('login/config.json'):
            with open('login/config.json', 'w') as f:
                f.write('{}')  # Ghi nội dung rỗng vào tệp
        self.root.destroy()  # Đóng cửa sổ hiện tại
        # import all  # Giả sử all.py chứa trang đăng nhập
        # all.main()  # Khởi tạo lại cửa sổ đăng nhập

def main():
    root = Tk()  # Tạo cửa sổ Tkinter
    app = HomeScreenTeacher(root)  # Khởi tạo đối tượng FaceRecognitionSystem
    root.mainloop()  # Bắt đầu vòng lặp Tkinter

if __name__ == "__main__":
    main()

