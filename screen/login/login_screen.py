import os
from time import strftime
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import mysql.connector
import json
from screen.home_screen import FaceRecognitionSystem


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('Login')
        self.root.geometry('925x600+300+200')
        self.root.configure(bg='#fff')
        self.root.resizable(False, False)
        today = strftime('%d-%m-%Y')

        self.var_username = StringVar()
        self.var_password = StringVar()


        lbl_today = Label(self.root, bg="white", text=today, font=("Book Antiqua", 20, "bold"), compound=BOTTOM,
                          fg="#57a1f8", bd=0)
        lbl_today.place(x=780, y=10)

        lbl_time = Label(self.root, bg="white", text="", font=("Book Antiqua", 20, "bold"), compound=BOTTOM,
                         fg="#57a1f8", bd=0)
        lbl_time.place(x=800, y=40)
        self.update_time(lbl_time)

        # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        #
        # # Tạo đường dẫn tuyệt đối đến tệp hình ảnh logo-ctu.png
        # img_path = os.path.join(BASE_DIR, '..', 'assets', 'ImageDesign', 'logo-ctu.png')
        # img_path = os.path.abspath(img_path)  # Chuẩn hóa đường dẫn thành tuyệt đối
        # img = Image.open(img_path)
        # img = img.resize((400, 400))
        # self.imgtk = ImageTk.PhotoImage(img)

        BASE_DIR2 = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(BASE_DIR2,'..', '..', 'assets', 'ImageDesign', 'logo-ctu.png')
        img = Image.open(img_path)
        img = img.resize((400, 400))
        self.imgtk = ImageTk.PhotoImage(img)

        logo_label = Label(self.root, image=self.imgtk, bg='white', width=400, height=400)
        logo_label.place(x=50, y=80)

        frame = Frame(self.root, width=350, height=350, bg='white')
        frame.place(x=480, y=100)

        lbl_heading = Label(frame, text='SIGN IN', fg='#57a1f8', bg='white',
                            font=('Microsoft YaHei UI Light', 23, 'bold'))
        lbl_heading.place(x=130, y=5)

        self.ent_user = Entry(frame, textvariable=self.var_username, width=25, fg='black', border=0, bg='white',
                              font=('Microsoft YaHei UI Light', 11))
        self.ent_user.place(x=40, y=80)
        self.ent_user.insert(0, 'Username')
        Frame(frame, width=295, height=2, bg='black').place(x=35, y=107)

        self.ent_code = Entry(frame, textvariable=self.var_password, width=25, fg='black', border=0, bg='white',
                              font=('Microsoft YaHei UI Light', 11), show="*")
        self.ent_code.place(x=40, y=150)
        self.ent_code.insert(0, 'Password')
        Frame(frame, width=295, height=2, bg='black').place(x=35, y=177)

        btn_login = Button(frame, width=30, pady=7, text='Log in', bg='#57a1f8', border=0, command=self.login)
        btn_login.place(x=40, y=254)

        self.ent_user.bind("<FocusIn>", self.clear_username)
        self.ent_code.bind("<FocusIn>", self.clear_password)

    def update_time(self, lbl_time):
        current_time = datetime.now().strftime('%H:%M:%S')
        lbl_time.config(text=current_time)
        self.root.after(1000, lambda: self.update_time(lbl_time))

    def save_teacher_id(self, teacher_id):
        with open('config.json', 'w') as f:
            json.dump({'teacher_id': teacher_id}, f)

    def login(self):
        if self.ent_user.get() == "" or self.ent_code.get() == "":
            messagebox.showerror("Error !!", "Vui lòng nhập đầy đủ thông tin")
        else:
            conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys',
                                           port='3306')
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT id_teacher, name_teacher FROM teacher WHERE id_teacher=%s AND pwd=%s", (
                self.var_username.get(),
                self.var_password.get()
            ))
            row = my_cursor.fetchone()
            if row is None:
                messagebox.showerror("Lỗi", "Sai tên đăng nhập, mật khẩu hoặc quyền đăng nhập")
            else:
                self.teacher_id = row[0]  # Lưu ID giáo viên
                self.teacher_name = row[1]  # Lưu tên giáo viên
                self.save_teacher_id(self.teacher_id)  # Lưu ID giáo viên vào file cấu hình
                messagebox.showinfo("Thông báo",
                                    f"Bạn đã đăng nhập thành công với quyền Admin. Xin chào, {self.teacher_name}!")

                # Khởi tạo và hiển thị cửa sổ FaceRecognitionSystem không cần tham số
                self.new_window = Toplevel(self.root)
                self.app = FaceRecognitionSystem(self.new_window)
                self.root.withdraw()  # Ẩn cửa sổ đăng nhập

            conn.commit()
            conn.close()

    def clear_username(self, event):
        if self.ent_user.get() == 'Username':
            self.ent_user.delete(0, END)

    def clear_password(self, event):
        if self.ent_code.get() == 'Password':
            self.ent_code.delete(0, END)
            self.ent_code.config(show="*")  # Ẩn ký tự khi nhập mật khẩu


def main_login():
    root = Tk()  # Tạo cửa sổ Tkinter
    app = LoginWindow(root)  # Khởi tạo đối tượng
    root.mainloop()  # Bắt đầu vòng lặp Tkinter

if __name__ == "__main__":
    main_login()  # Gọi hàm main để chạy ứng dụng