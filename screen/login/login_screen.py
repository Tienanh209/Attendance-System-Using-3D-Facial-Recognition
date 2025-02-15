import os
from time import strftime
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import mysql.connector
import json
from screen.home_screen_st import FaceRecognitionSystem


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

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        imgbg_path = os.path.join(BASE_DIR, '..', '..', 'assets', 'ImageDesign', 'bg_signin.jpg')
        imgbg = Image.open(imgbg_path)
        imgbg = imgbg.resize((930, 605))
        self.imgbgtk = ImageTk.PhotoImage(imgbg)
        lbl_bg = Label(self.root, image=self.imgbgtk, bg='white', width=930, height=605)
        lbl_bg.place(x=-5, y=-5)


        # lbl_today = Label(self.root, bg="white", text=today, font=("Book Antiqua", 20, "bold"), compound=BOTTOM,
        #                   fg="#57a1f8", bd=0)
        # lbl_today.place(x=780, y=10)
        #
        # lbl_time = Label(self.root, bg="white", text="", font=("Book Antiqua", 20, "bold"), compound=BOTTOM,
        #                  fg="#57a1f8", bd=0)
        # lbl_time.place(x=800, y=40)
        # self.update_time(lbl_time)


        self.ent_user = Entry(self.root, textvariable=self.var_username, width=15, fg='black', border=0, bg='white',
                              font=('Microsoft YaHei UI Light', 20))
        self.ent_user.place(x=444, y=279)
        self.ent_user.insert(0, 'Username')

        self.ent_code = Entry(self.root, textvariable=self.var_password, width=15, fg='black', border=0, bg='white',
                              font=('Microsoft YaHei UI Light', 20), show="*")
        self.ent_code.place(x=444, y=353)
        self.ent_code.insert(0, 'Password')

        btn_login = Button(self.root, width=15, pady=7, text='Log in', bg='#57a1f8', border=0, command=self.login)
        btn_login.place(x=679, y=498)

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
            self.ent_code.delete(0, END)# Ẩn ký tự khi nhập mật khẩu


def main_login():
    root = Tk()
    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main_login()