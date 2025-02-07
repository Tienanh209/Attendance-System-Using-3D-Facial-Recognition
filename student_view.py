import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import mysql.connector
from tkinter import messagebox  # Import ở đầu file
import os
import random
import json
import cv2
import time

class Student_View:
    def __init__(self, root):
        self.root = root
        self.teacher_id = self.load_teacher_id()  # Load teacher_id from config
        self.root.title("Student View")
        self.root.geometry('925x600+300+200')
        self.root.configure(bg='#f0f0f0')  # Set background color to light gray
        self.root.resizable(False, False)

        # Create frames
        self.left_frame = tk.Frame(self.root, width=300, bg='#e3f2fd')  # Set a light blue background color
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = tk.Frame(self.root, width=625, bg='#ffffff')  # Set a white background color
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.right_frame.pack_forget()  # Hide the right_frame initially

        # Display teacher name
        self.lbl_teacher_name = tk.Label(self.left_frame, text=f"Lecturer: {self.get_teacher_name()}", font=('Arial', 14, 'bold'), bg='#e3f2fd')
        self.lbl_teacher_name.pack(pady=10)

        # Create search widgets for section class and student
        search_frame = tk.Frame(self.left_frame, bg='#f0f0f0', pady=10)
        search_frame.pack(padx=10, pady=10, fill=tk.X)

        # Search by section class
        search_label_section = tk.Label(search_frame, text="Select course:", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        search_label_section.grid(row=0, column=0, padx=10, sticky='w')

        self.var_section_class = tk.StringVar()
        self.section_class_combobox = ttk.Combobox(search_frame, textvariable=self.var_section_class, width=20,
                                                   font=('Arial', 12))
        self.section_class_combobox.grid(row=0, column=1, padx=10, sticky='w')
        self.section_class_combobox.bind('<<ComboboxSelected>>', self.search_by_section_class)

        # search_button_section = tk.Button(search_frame, text="Search", command=self.search_by_section_class,
        #                                   font=('Arial', 12), bg='#fff9c4')
        # search_button_section.grid(row=0, column=2, padx=10, sticky='w')

        # Search by student ID or Name
        search_label_student = tk.Label(search_frame, text="Find students:", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        search_label_student.grid(row=1, column=0, padx=10, pady=(10, 0), sticky='w')

        self.var_student_query = tk.StringVar()
        self.student_query_entry = tk.Entry(search_frame, textvariable=self.var_student_query, width=22,
                                            font=('Arial', 12))
        self.student_query_entry.grid(row=1, column=1, padx=10, pady=(10, 0), sticky='w')

        search_button_student = tk.Button(search_frame, text="Search", command=self.search_by_student,
                                          font=('Arial', 12), bg='#fff9c4')
        search_button_student.grid(row=1, column=2, padx=10, pady=(10, 0), sticky='w')

        # Create treeview for student list on left frame
        self.tree = ttk.Treeview(self.left_frame, columns=('ID', 'Name', 'Birthday', 'Email'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Birthday', text='Birthday')
        self.tree.heading('Email', text='Email')

        # Set column widths
        self.tree.column('ID', width=100, anchor=tk.CENTER)
        self.tree.column('Name', width=150, anchor=tk.W)
        self.tree.column('Birthday', width=100, anchor=tk.CENTER)
        self.tree.column('Email', width=200, anchor=tk.W)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Create labels and image display for student details on right frame
        self.lbl_title = tk.Label(self.right_frame, text='Student information', font=('Arial', 16, 'bold'), bg='#ffffff')
        self.lbl_title.place(x=20, y=20)
        # Nhãn cho các trường thông tin sinh viên
        lbl_id = tk.Label(self.right_frame, text="ID:", font=('Arial', 12), bg='#ffffff')
        lbl_id.place(x=20, y=60)

        lbl_name = tk.Label(self.right_frame, text="Name:", font=('Arial', 12), bg='#ffffff')
        lbl_name.place(x=20, y=90)

        lbl_birthday = tk.Label(self.right_frame, text="Birthday:", font=('Arial', 12), bg='#ffffff')
        lbl_birthday.place(x=20, y=120)

        lbl_email = tk.Label(self.right_frame, text="Email:", font=('Arial', 12), bg='#ffffff')
        lbl_email.place(x=20, y=150)
        btn_update_student = tk.Button(self.right_frame, text='Update', font=('Arial', 12),
                                       bg='#90caf9', fg='#ffffff',  # Thay đổi màu nền và chữ
                                       command=self.update_student_info)
        btn_update_student.place(x=260, y=25)

        # Thay thế các Label thành Entry
        self.entry_id = tk.Entry(self.right_frame, font=('Arial', 14), bg='#ffffff')
        self.entry_id.place(x=85, y=60, width=200)
        self.entry_name = tk.Entry(self.right_frame, font=('Arial', 14), bg='#ffffff')
        self.entry_name.place(x=85, y=90, width=200)
        self.entry_birthday = tk.Entry(self.right_frame, font=('Arial', 14), bg='#ffffff')
        self.entry_birthday.place(x=85, y=120, width=200)
        self.entry_email = tk.Entry(self.right_frame, font=('Arial', 14), bg='#ffffff')
        self.entry_email.place(x=85, y=150, width=500)

        self.img_label = tk.Label(self.right_frame, bg='#ffffff')
        self.img_label.place(x=20, y=200)

        # Nút xóa ảnh
        btn_delete_image = tk.Button(self.right_frame, text='Delete images', font=('Arial', 12), command=self.delete_image)
        btn_delete_image.place(x=20, y=420)

        # # Nút chụp ảnh mới
        # btn_capture_image = tk.Button(self.right_frame, text='Capture new images', font=('Arial', 12),
        #                               command=self.capture_new_image)
        # btn_capture_image.place(x=80, y=450)

        # Nút chụp thêm ảnh
        btn_capture_more_images = tk.Button(self.right_frame, text='Capture more images', font=('Arial', 12),
                                            command=self.capture_more_images)
        btn_capture_more_images.place(x=150, y=420)

        # Load student data and section classes from database
        self.load_section_classes()

    def load_teacher_id(self):
        # Read teacher_id from config file
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                return config.get('teacher_id', 'Unknown')
        return 'Unknown'

    def get_teacher_name(self):
        conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys', port='3306')
        my_cursor = conn.cursor()
        my_cursor.execute("SELECT name_teacher FROM teacher WHERE id_teacher = %s", (self.teacher_id,))
        result = my_cursor.fetchone()
        conn.close()
        return result[0] if result else "Unknown Teacher"

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

        if id_class_subject:  # Nếu học phần được chọn
            sql = ("SELECT std.id_student, std.name_student, std.birthday, std.email "
                   "FROM student std "
                   "JOIN register r ON std.id_student = r.id_student "
                   "WHERE r.id_class_subject = %s AND (std.id_student LIKE %s OR std.name_student LIKE %s)")
            like_query = f"%{query}%"
            my_cursor.execute(sql, (id_class_subject, like_query, like_query))
        else:  # Nếu không có học phần nào được chọn, tìm toàn bộ sinh viên
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
            self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            student_id = self.tree.item(selected_item[0], 'values')[0]

            conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys',
                                           port='3306')
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT id_student, name_student, birthday, email FROM student WHERE id_student = %s",
                              (student_id,))
            row = my_cursor.fetchone()
            conn.close()

            if row:
                # Hiển thị dữ liệu sinh viên vào Entry
                self.entry_id.delete(0, tk.END)
                self.entry_id.insert(0, row[0])
                # self.entry_id.config(state='readonly')  # Sau khi cập nhật xong chuyển lại thành 'disabled'
                self.entry_name.delete(0, tk.END)
                self.entry_name.insert(0, row[1])

                self.entry_birthday.delete(0, tk.END)
                self.entry_birthday.insert(0, row[2])

                self.entry_email.delete(0, tk.END)
                self.entry_email.insert(0, row[3])

                # Tiếp tục phần xử lý hình ảnh như trước đây
                folder_path = f'trash/DataProcessed/{student_id}'
                if os.path.isdir(folder_path):
                    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                    if image_files:
                        random_image_file = random.choice(image_files)
                        img_path = os.path.join(folder_path, random_image_file)
                        img = Image.open(img_path)
                        img = img.resize((200, 200))  # Resize image as needed
                        imgtk = ImageTk.PhotoImage(img)
                        self.img_label.config(image=imgtk)
                        self.img_label.image = imgtk  # Keep a reference to avoid garbage collection
                    else:
                        self.img_label.config(image='')  # Clear image if no images found
                else:
                    self.img_label.config(image='')  # Clear image if folder not found

    def delete_image(self):
        # Xóa ảnh từ thư mục DataProcessed
        student_id = self.entry_id.get()
        folder_path = f'trash/DataProcessed/{student_id}'
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                os.remove(os.path.join(folder_path, file))
            self.img_label.config(image='')  # Clear the image
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
        img_id = 0  # Reset img_id for new image capturing
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
                cv2.imshow("Cropped Face", cropped_face)

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
        img_id = len([f for f in os.listdir(folder_name) if f.endswith('.jpg')]) + 1  # Continue from last image ID
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
                cv2.imshow("Cropped Face", cropped_face)

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
    app = Student_View(root)
    root.mainloop()

