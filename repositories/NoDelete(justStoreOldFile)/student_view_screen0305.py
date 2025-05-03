import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import mysql.connector
from tkinter import messagebox
import os
import random
import json
import cv2
import time

class student_view:
    def __init__(self, root):
        self.root = root
        self.root.title("Giao Diện Xem Sinh Viên")
        self.root.geometry('1000x600+300+150')
        self.root.configure(bg='#e3f2fd')
        self.root.resizable(False, False)


        # Khung Bên Trái
        self.left_frame = tk.Frame(self.root, width=900, bg='#e3f2fd')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Khung Bên Phải
        self.right_frame = tk.Frame(self.root, width=500, bg='#e3f2fd')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Tên Giảng Viên
        self.lbl_teacher_name = tk.Label(self.left_frame, text="", font=('Arial', 14, 'bold'), bg='#e3f2fd')
        self.lbl_teacher_name.pack(pady=10)

        # Phần Tìm Kiếm
        search_frame = tk.Frame(self.left_frame, bg='#e3f2fd')
        search_frame.pack(padx=10, pady=10, fill=tk.X)

        # tk.Label(search_frame, text="Chọn lớp:", font=('Arial', 12, 'bold'), bg='#e3f2fd').grid(row=0, column=0,
        #                                                                                         padx=10, sticky='w')
        self.var_section_class = tk.StringVar()
        # self.section_class_combobox = ttk.Combobox(search_frame, textvariable=self.var_section_class, width=12,
        #                                            font=('Arial', 12))
        # self.section_class_combobox.grid(row=0, column=1, padx=10, sticky='w')

        tk.Label(search_frame, text="Nhập tên:", font=('Arial', 12, 'bold'), bg='#e3f2fd').grid(row=1, column=0,
                                                                                                padx=10, pady=(10, 0),
                                                                                                sticky='w')
        self.var_student_query = tk.StringVar()
        self.student_query_entry = tk.Entry(search_frame, textvariable=self.var_student_query, width=12,
                                            font=('Arial', 12))
        self.student_query_entry.grid(row=1, column=1, padx=10, pady=(10, 0), sticky='w')
        search_button = tk.Button(search_frame, text="Tìm", font=('Arial', 12), bg='#bbdefb',
                                  command=self.search_by_student)
        search_button.grid(row=1, column=2, padx=10, pady=(10, 0), sticky='w')  # Sửa từ sticky_Clock thành sticky

        # Bảng Danh Sách Sinh Viên
        self.tree = ttk.Treeview(self.left_frame, columns=('ID', 'Tên', 'Ngày Sinh', 'Email'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Tên', text='Tên')
        self.tree.heading('Ngày Sinh', text='Ngày Sinh')
        self.tree.heading('Email', text='Email')
        self.tree.column('ID', width=80, anchor=tk.CENTER)
        self.tree.column('Tên', width=140, anchor=tk.W)
        self.tree.column('Ngày Sinh', width=100, anchor=tk.CENTER)
        self.tree.column('Email', width=180, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Khung Bên Phải - Thông Tin Sinh Viên
        tk.Label(self.right_frame, text='Thông Tin Sinh Viên', font=('Arial', 16, 'bold'), bg='#e3f2fd').place(x=20, y=20)

        # Các Trường Nhập Liệu
        self.entry_id = tk.Entry(self.right_frame, font=('Arial', 14), width=30)
        self.entry_name = tk.Entry(self.right_frame, font=('Arial', 14), width=30)
        self.entry_birthday = tk.Entry(self.right_frame, font=('Arial', 14), width=30)
        self.entry_email = tk.Entry(self.right_frame, font=('Arial', 14), width=30)

        # Nhãn và Vị Trí
        fields = [('ID', self.entry_id), ('Tên', self.entry_name), ('Sinh', self.entry_birthday),
                  ('Email', self.entry_email)]
        y_offset = 60
        for field, entry in fields:
            tk.Label(self.right_frame, text=f"{field}:", font=('Arial', 12, 'bold'), bg='#e3f2fd').place(x=20, y=y_offset)
            entry.place(x=100, y=y_offset)
            y_offset += 40

        self.btn_back = tk.Button(self.root, text="Quay lại", font=("Arial", 10, "bold"),
                                  bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                  command=self.close_current_window)
        self.btn_back.place(x=5, y=5)

    def load_teacher_id(self):
        # Đọc teacher_id từ tệp cấu hình
        if os.path.exists('../../screen/login/config.json'):
            with open('../../screen/login/config.json', 'r') as f:
                config = json.load(f)
                return config.get('teacher_id', 'Không xác định')
        return 'Không xác định'
    def close_current_window(self):
        """Đóng cửa sổ hiện tại mà không thoát toàn bộ ứng dụng"""
        self.root.destroy()  # Đóng cửa sổ hiện tại

    def get_teacher_name(self):
        conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys', port='3306')
        my_cursor = conn.cursor()
        my_cursor.execute("SELECT name_teacher FROM teacher WHERE id_teacher = %s", (self.teacher_id,))
        result = my_cursor.fetchone()
        conn.close()
        return result[0] if result else "Giáo viên không xác định"

    def load_section_classes(self):
        conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys', port='3306')
        my_cursor = conn.cursor()
        my_cursor.execute("SELECT DISTINCT id_class_subject FROM class_subject WHERE id_teacher = %s", (self.teacher_id,))
        sections = my_cursor.fetchall()
        conn.close()

        self.section_class_combobox['values'] = [section[0] for section in sections]

    def search_by_section_class(self, event=None):
        id_class_subject = self.var_section_class.get()
        conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys', port='3306')
        my_cursor = conn.cursor()
        sql = ("SELECT std.id_student, std.name_student, std.birthday, std.email "
               "FROM student std "
               "JOIN register r ON std.id_student = r.id_student "
               "WHERE r.id_class_subject = %s")
        my_cursor.execute(sql, (id_class_subject,))
        rows = my_cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert('', tk.END, values=row)

    def search_by_student(self):
        query = self.var_student_query.get()
        id_class_subject = self.var_section_class.get()

        conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys',
                                       port='3306')
        my_cursor = conn.cursor()

        if id_class_subject:  # Nếu lớp học được chọn
            sql = ("SELECT std.id_student, std.name_student, std.birthday, std.email "
                   "FROM student std "
                   "JOIN register r ON std.id_student = r.id_student "
                   "WHERE r.id_class_subject = %s AND (std.id_student LIKE %s OR std.name_student LIKE %s)")
            like_query = f"%{query}%"
            my_cursor.execute(sql, (id_class_subject, like_query, like_query))
        else:  # Nếu không có lớp học nào được chọn, tìm toàn bộ sinh viên
            sql = ("SELECT id_student, name_student, birthday, email "
                   "FROM student "
                   "WHERE id_student LIKE %s OR name_student LIKE %s")
            like_query = f"%{query}%"
            my_cursor.execute(sql, (like_query, like_query))

        rows = my_cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert('', tk.END, values=row)

    def on_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            student_id = self.tree.item(selected_item[0], 'values')[0]

            conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys',
                                           port='3306')
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT id_student, name_student, birthday, email FROM student WHERE id_student = %s",
                              (student_id,))
            row = my_cursor.fetchone()
            conn.close()

            if row:
                # Tạm thời bật trạng thái để cập nhật các trường
                self.entry_id.config(state='normal')
                self.entry_name.config(state='normal')
                self.entry_birthday.config(state='normal')
                self.entry_email.config(state='normal')

                # Chèn giá trị
                self.entry_id.delete(0, tk.END)
                self.entry_id.insert(0, row[0])
                self.entry_name.delete(0, tk.END)
                self.entry_name.insert(0, row[1])
                self.entry_birthday.delete(0, tk.END)
                self.entry_birthday.insert(0, row[2])
                self.entry_email.delete(0, tk.END)
                self.entry_email.insert(0, row[3])

                # Đặt lại trạng thái chỉ đọc
                self.entry_id.config(state='readonly')
                self.entry_name.config(state='readonly')
                self.entry_birthday.config(state='readonly')
                self.entry_email.config(state='readonly')

    def delete_image(self):
        # Xóa ảnh từ thư mục DataProcessed
        student_id = self.entry_id.get()
        folder_path = f'trash/DataProcessed/{student_id}'
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                os.remove(os.path.join(folder_path, file))
            self.img_label.config(image='')  # Xóa hình ảnh
        messagebox.showinfo("Kết quả", "Xóa dữ liệu khuôn mặt thành công", parent=self.root)

    def capture_new_image(self):
        student_id = self.entry_id.get()

        if not student_id:
            messagebox.showerror("Lỗi!", "Vui lòng chọn sinh viên để chụp ảnh.", parent=self.root)
            return

        folder_name = f"DataProcessed/{student_id}"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        def face_cropped(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                return img[y:y + h, x:x + w]
            return None

        cap = cv2.VideoCapture(0)
        img_id = 0  # Đặt lại img_id để chụp ảnh mới
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cropped_face = face_cropped(frame)
            if cropped_face is not None:
                img_id += 1
                face_gray = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)
                fill_name_path = os.path.join(folder_name, f"user.{student_id}.{img_id}.jpg")
                cv2.imwrite(fill_name_path, face_gray)
                cv2.putText(cropped_face, str(img_id), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                cv2.imshow("Khuôn Mặt Đã Cắt", cropped_face)

                if img_id % 10 == 0:
                    time_elapsed = time.time() - start_time
                    if time_elapsed < 2:
                        time.sleep(2 - time_elapsed)
                    start_time = time.time()

            if cv2.waitKey(1) == 13 or img_id >= 50:
                break

        cap.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("Kết quả", "Tạo dữ liệu khuôn mặt thành công", parent=self.root)

    def update_student_info(self):
        student_id = self.entry_id.get()
        name = self.entry_name.get()
        birthday = self.entry_birthday.get()
        email = self.entry_email.get()

        conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys',
                                       port='3306')
        my_cursor = conn.cursor()
        sql = "UPDATE student SET name_student = %s, birthday = %s, email = %s WHERE id_student = %s"
        my_cursor.execute(sql, (name, birthday, email, student_id))
        conn.commit()
        conn.close()

        # Thêm thông báo cập nhật thành công
        messagebox.showinfo("Thông báo", "Cập nhật thành công")

    def capture_more_images(self):
        student_id = self.entry_id.get()

        if not student_id:
            messagebox.showerror("Lỗi!", "Vui lòng chọn sinh viên để chụp ảnh.", parent=self.root)
            return

        folder_name = f"DataProcessed/{student_id}"
        if not os.path.exists(folder_name):
            messagebox.showerror("Lỗi!", "Thư mục sinh viên không tồn tại. Vui lòng chụp ảnh mới.", parent=self.root)
            return

        face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        def face_cropped(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                return img[y:y + h, x:x + w]
            return None

        cap = cv2.VideoCapture(0)
        img_id = len([f for f in os.listdir(folder_name) if f.endswith('.jpg')]) + 1  # Tiếp tục từ ID ảnh cuối cùng
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cropped_face = face_cropped(frame)
            if cropped_face is not None:
                face_gray = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)
                fill_name_path = os.path.join(folder_name, f"user.{student_id}.{img_id}.jpg")
                cv2.imwrite(fill_name_path, face_gray)
                cv2.putText(cropped_face, str(img_id), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                cv2.imshow("Khuôn Mặt Đã Cắt", cropped_face)

                if img_id % 10 == 0:
                    time_elapsed = time.time() - start_time
                    if time_elapsed < 2:
                        time.sleep(2 - time_elapsed)
                    start_time = time.time()

                img_id += 1

            if cv2.waitKey(1) == 13 or img_id >= 100:
                break

        cap.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("Kết quả", "Chụp thêm ảnh thành công", parent=self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = student_view(root)
    root.mainloop()