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

class FaceRecognitionSystem:
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
        img_path = os.path.join(BASE_DIR, '..', 'assets', 'ImageDesign', 'bg-homepage.png')
        img = Image.open(img_path)
        img = img.resize((930, 605))
        self.imgtk = ImageTk.PhotoImage(img)
        lbl_bg = Label(self.root, image=self.imgtk, bg='white', width=930, height=605)
        lbl_bg.place(x=-5, y=-5)

        #========== heading
        lbl_name = Label(self.root, bg="white", text=f"Teacher:  {self.teacher_name}", font=("yu gothic ui", 20, "bold"),
                         fg="#57a1f8", bd=0)
        lbl_name.place(x=80, y=10)

        #=== timeline
        lbl_time = Label(self.root, bg="white", text="", font=("yu gothic ui", 20, "bold"),
                         fg="#57a1f8", bd=0)
        lbl_time.place(x=80, y=42)
        self.update_time(lbl_time)

        #=== logout
        btn_logout = Button(self.root, text="Log out", command=self.logout, font=("yu gothic ui", 20, "bold"), bg="white", fg="#57a1f8", borderwidth=0)
        btn_logout.place(x=797, y=40, width=90, height=23)

        #======= body

        # ==== student


        BASE_DIR2 = os.path.dirname(os.path.abspath(__file__))  # Lấy đường dẫn tuyệt đối của file hiện tại
        img_student_path = os.path.join(BASE_DIR2, '..', 'assets', 'ImageDesign', 'student1.png')

        img_student = Image.open(img_student_path)
        img_student = img_student.resize((140, 140), Image.Resampling.LANCZOS)

        self.img_studenttk = ImageTk.PhotoImage(img_student)
        btn_student = Button(self.root, text="Student", font=("yu gothic ui", 14, "bold"), command=lambda: self.student_view(self.root),
                             image=self.img_studenttk, activebackground="white", bg="white", borderwidth=0,
                             compound="top")
        btn_student.place(x=95, y=145, width=170, height=170)

        # ==== report
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Lấy đường dẫn thư mục chứa home_screen.py
        img_report_path = os.path.join(BASE_DIR, '..', 'assets', 'ImageDesign', 'atten.png')
        img_report_path = os.path.abspath(img_report_path)  # Chuẩn hóa thành đường dẫn tuyệt đối

        if not os.path.exists(img_report_path):
            print("File không tồn tại:", img_report_path)

        img_report = Image.open(img_report_path)
        img_report = img_report.resize((140, 140), Image.Resampling.LANCZOS)

        self.img_reporttk = ImageTk.PhotoImage(img_report)
        btn_report = Button(self.root, text="Report", font=("yu gothic ui", 14, "bold"), command="",
                            image=self.img_reporttk, activebackground="white", bg="white", borderwidth=0,
                            compound="top")
        btn_report.place(x=95, y=365, width=170, height=170)

        # === recognize
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Lấy thư mục chứa home_screen.py
        img_recognize_path = os.path.join(BASE_DIR, '..', 'assets', 'ImageDesign', 'face_ro.png')
        img_recognize_path = os.path.abspath(img_recognize_path)  # Chuẩn hóa thành đường dẫn tuyệt đối

        if not os.path.exists(img_recognize_path):
            print("File không tồn tại:", img_recognize_path)

        img_recognize = Image.open(img_recognize_path)
        img_recognize = img_recognize.resize((140, 140), Image.Resampling.LANCZOS)

        self.img_recognizetk = ImageTk.PhotoImage(img_recognize)
        btn_recognize = Button(self.root, text="Recognize", font=("yu gothic ui", 14, "bold"), command=self.attendance,
                               image=self.img_recognizetk, activebackground="white", bg="white", borderwidth=0,
                               compound="top")
        btn_recognize.place(x=380, y=145, width=170, height=170)

        # === roll-call
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Lấy thư mục chứa home_screen.py
        img_rollcall_path = os.path.join(BASE_DIR, '..', 'assets', 'ImageDesign', 'traindt.png')
        img_rollcall_path = os.path.abspath(img_rollcall_path)  # Chuẩn hóa thành đường dẫn tuyệt đối

        if not os.path.exists(img_rollcall_path):
            print("File không tồn tại:", img_rollcall_path)

        img_rollcall = Image.open(img_rollcall_path)
        img_rollcall = img_rollcall.resize((140, 140), Image.Resampling.LANCZOS)

        self.img_rollcalltk = ImageTk.PhotoImage(img_rollcall)
        btn_rollcall = Button(self.root, text="Train Img", font=("yu gothic ui", 14, "bold"), command=self.traindata,
                              image=self.img_rollcalltk, activebackground="white", bg="white", borderwidth=0,
                              compound="top")
        btn_rollcall.place(x=380, y=365, width=170, height=170)

        # === subject
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Lấy thư mục chứa home_screen.py
        img_subject_path = os.path.join(BASE_DIR, '..', 'assets', 'ImageDesign', 'photo.png')
        img_subject_path = os.path.abspath(img_subject_path)  # Chuẩn hóa thành đường dẫn tuyệt đối

        if not os.path.exists(img_subject_path):
            print("File không tồn tại:", img_subject_path)

        img_subject = Image.open(img_subject_path)
        img_subject = img_subject.resize((140, 140), Image.Resampling.LANCZOS)

        self.img_subjecttk = ImageTk.PhotoImage(img_subject)
        btn_subject = Button(self.root, text="Subject", font=("yu gothic ui", 14, "bold"), command="",
                             image=self.img_subjecttk, activebackground="white", bg="white", borderwidth=0,
                             compound="top")
        btn_subject.place(x=660, y=145, width=170, height=170)

        # === teacher
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Lấy thư mục chứa home_screen.py
        img_teacher_path = os.path.join(BASE_DIR, '..', 'assets', 'ImageDesign', 'dev.png')
        img_teacher_path = os.path.abspath(img_teacher_path)  # Chuẩn hóa thành đường dẫn tuyệt đối

        if not os.path.exists(img_teacher_path):
            print("File không tồn tại:", img_teacher_path)

        img_teacher = Image.open(img_teacher_path)
        img_teacher = img_teacher.resize((140, 140), Image.Resampling.LANCZOS)

        self.img_teachertk = ImageTk.PhotoImage(img_teacher)
        btn_teacher = Button(self.root, text="Teacher", font=("yu gothic ui", 14, "bold"), command="",
                             image=self.img_teachertk, activebackground="white", bg="white", borderwidth=0,
                             compound="top")
        btn_teacher.place(x=660, y=365, width=170, height=170)

    def update_time(self, lbl_time):
        current_time = datetime.now().strftime('%H:%M:%S')
        lbl_time.config(text=current_time)
        self.root.after(1000, lambda: self.update_time(lbl_time))

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
        # Đọc thông tin từ tệp cấu hình
        if os.path.exists('login/config.json'):
            with open('login/config.json', 'r') as f:
                config = json.load(f)
                return config.get('teacher_id', 'Unknown')
        return 'Unknown'

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
    app = FaceRecognitionSystem(root)  # Khởi tạo đối tượng FaceRecognitionSystem
    root.mainloop()  # Bắt đầu vòng lặp Tkinter

if __name__ == "__main__":
    main()

