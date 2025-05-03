import os
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import mysql.connector
import json
from screen.home.home_student_screen import HomeScreenStudent
from screen.home.home_teacher_screen import HomeScreenTeacher



class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # Xóa tất cả hình ảnh còn tồn đọng trước khi tạo mới
        for name in root.tk.call('image', 'names'):
            root.tk.call('image', 'delete', name)
        self.root.title('Đăng nhập')
        self.root.geometry('925x600+300+200')
        self.root.configure(bg='#fff')
        self.root.resizable(False, False)

        self.var_username = StringVar()
        self.var_password = StringVar()

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        imgbg_path = os.path.join(BASE_DIR, '..', '..', 'assets', 'ImageDesign', 'bg_signin.jpg')
        imgbg = Image.open(imgbg_path)
        imgbg = imgbg.resize((930, 605))
        self.imgbgtk = ImageTk.PhotoImage(imgbg)
        lbl_bg = Label(self.root, image=self.imgbgtk, bg='white', width=930, height=605)
        lbl_bg.place(x=-5, y=-5)

        # Sửa phần tạo Entry như sau:
        self.ent_user = Entry(self.root, textvariable=self.var_username, width=15,
                              fg='black', border=0, bg='white',
                              font=('Microsoft YaHei UI Light', 20),
                              selectbackground='white',  # Màu nền khi chọn
                              selectforeground='black',  # Màu chữ khi chọn
                              insertbackground='black')  # Màu con trỏ nhập
        self.ent_user.place(x=444, y=279)
        self.ent_user.insert(0, 'Tài khoản')

        self.ent_code = Entry(self.root, textvariable=self.var_password, width=15,
                              fg='black', border=0, bg='white',
                              font=('Microsoft YaHei UI Light', 20), show="*",
                              selectbackground='white',  # Màu nền khi chọn
                              selectforeground='black',  # Màu chữ khi chọn
                              insertbackground='black')  # Màu con trỏ nhập
        self.ent_code.place(x=444, y=353)
        self.ent_code.insert(0, 'Mật khẩu')

        # Sửa phần bind sự kiện FocusIn
        self.ent_user.bind("<FocusIn>", lambda e: self.on_entry_click(self.ent_user, 'Tài khoản'))
        self.ent_code.bind("<FocusIn>", lambda e: self.on_entry_click(self.ent_code, 'Mật khẩu'))
        btn_login = Button(self.root, width=15, pady=7, text='Đăng nhập', bg='#57a1f8', border=0, command=self.login)
        btn_login.place(x=679, y=498)

    def on_entry_click(self, entry, default_text):
        """Xử lý khi click vào ô nhập liệu"""
        if entry.get() == default_text:
            entry.delete(0, END)
            if default_text == 'Mật khẩu':
                entry.config(show="*")

        # Đặt vị trí con trỏ ở cuối text
        entry.icursor(END)
    def save_teacher_id(self, teacher_id):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
        config_path = os.path.join(BASE_DIR, 'config.json')
        config_data = {"id_teacher": teacher_id}

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)

    def save_student_id(self, student_id):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
        config_path = os.path.join(BASE_DIR, 'config.json')
        config_data = {"student_id": student_id}

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)

    def login(self):
        if self.ent_user.get() == "" or self.ent_code.get() == "":
            messagebox.showerror("Error !!", "Vui lòng nhập đầy đủ thông tin")
        else:
            conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys',
                                           port='3306')
            my_cursor = conn.cursor()

            # Kiểm tra nếu là giáo viên
            my_cursor.execute("SELECT id_teacher, name_teacher FROM teacher WHERE id_teacher=%s AND pwd=%s", (
                self.var_username.get(),
                self.var_password.get()
            ))
            row = my_cursor.fetchone()

            if row:
                self.teacher_id = row[0]
                self.teacher_name = row[1]
                self.save_teacher_id(self.teacher_id)
                messagebox.showinfo("Thông báo",
                                    f"Bạn đã đăng nhập thành công với quyền Giảng Viên. Xin chào, {self.teacher_name}!")

                # Chuyển sang giao diện giáo viên
                self.new_window = Toplevel(self.root)
                self.app = HomeScreenTeacher(self.new_window)
                self.root.withdraw()

            else:
                # Kiểm tra nếu là sinh viên
                my_cursor.execute("SELECT id_student, name_student FROM student WHERE id_student=%s AND pwd=%s", (
                    self.var_username.get(),
                    self.var_password.get()
                ))
                row = my_cursor.fetchone()

                if row:
                    self.student_id = row[0]
                    self.student_name = row[1]
                    self.save_student_id(self.student_id)
                    messagebox.showinfo("Thông báo",
                                        f"Bạn đã đăng nhập thành công với quyền Sinh Viên. Xin chào, {self.student_name}!")

                    # Chuyển sang giao diện sinh viên
                    self.new_window = Toplevel(self.root)
                    self.app = HomeScreenStudent(self.new_window)
                    self.root.withdraw()

                else:
                    messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")

            conn.commit()
            conn.close()
    def clear_username(self, event):
        if self.ent_user.get() == 'Username':
            self.ent_user.delete(0, END)

    def clear_password(self, event):
        if self.ent_code.get() == 'Password':
            self.ent_code.delete(0, END)

    def on_close(self):
        self.root.destroy()


def main_login():
    root = Tk()
    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main_login()