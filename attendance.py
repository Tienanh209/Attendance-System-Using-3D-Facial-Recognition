# attendance
import json
from time import strftime
from datetime import *
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image
import mysql.connector
import cv2
import numpy as np
from insightface.app import FaceAnalysis
import os


class attendance:
    def __init__(self, root):
        # Đọc thông tin từ config.json
        self.teacher_id = self.load_teacher_id()
        self.teacher_name = self.get_teacher_name(self.teacher_id)
        self.camera_name = 1
        self.root = root
        self.root.geometry("1530x790+0+0")
        self.root.title("Attendance")
        self.isClicked = False
        self.recognition_start_time = {}
        self.var_section_class = StringVar()
        self.start_time = ['7:00', '7:50', '8:50', '9:50', '10:40', '13:30', '14:20', '15:20', '16:10']
        self.end_time =['7:50', '8:40', '9:40', '10:40', '11:30', '14:20', '15:10', '16:10', '17:00']
        self.id_session = StringVar()

        # ======= background
        img = Image.open('./ImageDesign/img.png')


        img = img.resize((1530, 790))

        self.imgtk = ImageTk.PhotoImage(img)

        lbl_bg = Label(self.root, image=self.imgtk, bg='white', width=1530, height=790)
        lbl_bg.place(x=0, y=0)

        heading = Label(self.root, text="Hệ thống điểm danh khuôn mặt", font=("yu gothic ui", 20, "bold"), bg="white",
                           fg="#57a1f8", bd=0, relief=FLAT)
        heading.place(x=400, y=20, width=650, height=40)

        # LEFT FRAME
        self.left_frame = LabelFrame(self.root, bd=2, bg="white", relief=RIDGE, text="Camera",
                                font=("times new roman", 12, "bold"))
        self.left_frame.place(x=30, y=70, width=820, height=680)

        self.panel = Label(self.left_frame, borderwidth=2, relief="groove")

        self.panel.place(x=8, y=20, width=800, height=480)

        self.cbb_session = ttk.Combobox(self.left_frame, values=["Morning", "Afternoon"])
        self.cbb_session.place(x=20, y=530, width=120)
        self.cbb_session.bind("<<ComboboxSelected>>", self.choose_session)

        self.cbb_from = ttk.Combobox(self.left_frame, values=[])
        self.cbb_from.place(x=200, y=530, width=40)
        self.cbb_from.bind("<<ComboboxSelected>>", self.choose_from)

        self.cbb_to = ttk.Combobox(self.left_frame, values=[])
        self.cbb_to.place(x=295, y=530, width=40)
        self.cbb_to.bind("<<ComboboxSelected>>", self.choose_to)

        Label(self.left_frame, text="From: ", fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 14)).place(x=150, y=532)
        Label(self.left_frame, text="To: ", fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 14)).place(x=260, y=532)

        btn_add = Button(self.left_frame, text="Add", bg="#57a1f8", fg="black", command=self.add_session)
        btn_add.place(x=500, y=530, width=50, height=25)

        btn_open = Button(self.left_frame, text="Open", bg="#57a1f8", fg="black", command=self.open_camera)
        btn_open.place(x=100, y=580, width=180, height=50)

        btn_close = Button(self.left_frame, text="Close", bg="#57a1f8", fg="black", command=self.is_clicked)
        btn_close.place(x=500, y=580, width=180, height=50)



        # Find section
        # Find section - Use ONLY the Combobox
        search_frame = LabelFrame(self.root, bd=2, bg="white", relief=RIDGE, text="Find section class",
                                  font=("times new roman", 12, "bold"))
        search_frame.place(x=910, y=90, width=250, height=80)

        self.var_section_class = StringVar()  # Keep this for the Combobox's value
        self.cbb_section_class = ttk.Combobox(search_frame, textvariable=self.var_section_class, state='readonly')
        self.cbb_section_class.place(x=5, y=15, width=190, height=30)
        # REMOVE the Entry widget:
        # self.ent_section_class = Entry(search_frame, textvariable=self.var_section_class, fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 14))
        # self.ent_section_class.place(x=5, y=15, width=190, height=30)  # REMOVE THIS LINE

        img_search = Image.open('./ImageDesign/search_icon.png')
        img_search = img_search.resize((27, 27), Image.Resampling.LANCZOS)
        self.img_searchtk = ImageTk.PhotoImage(img_search)
        btn_report = Button(search_frame, command=self.search, image=self.img_searchtk, borderwidth=0)
        btn_report.place(x=200, y=15)

        self.load_class_subjects()  # Load subjects AFTER creating the Combobox

        self.lbl_time_session = Label(self.left_frame, text="", fg='black', border=0, bg='white',font=('Microsoft YaHei UI Light', 14))
        self.lbl_time_session.place(x=350, y=532)

        # ========== heading
        lbl_name = Label(self.root, bg="white", text=f"Teacher:  {self.teacher_name}",
                         font=("yu gothic ui", 15, "bold"), bd=0)
        lbl_name.place(x=1000, y=50)



        #========= print details
        # frame_details = LabelFrame(self.root, text="Details of section", bg="white")
        # frame_details.place(x=1200, y=60, width=300, height=150)
        #
        # lbl_id_subject = Label(frame_details, text=f"ID Subject: ", font=("yu gothic ui", 14), fg="black", bg="white")
        # lbl_id_subject.place(x=5, y=5)
        #
        # lbl_credit = Label(frame_details, text=f"Credit: ", font=("yu gothic ui", 14), fg="black", bg="white")
        # lbl_credit.place(x=200, y=5)
        #
        # lbl_name_subject = Label(frame_details, text=f"Name of Subject", font=("yu gothic ui", 14), fg="black", bg="white")
        # lbl_name_subject.place(x=5, y=35)
        #
        # lbl_group = Label(frame_details, text=f"Group: ", font=("yu gothic ui", 14), fg="black", bg="white")
        # lbl_group.place(x=5, y=65)
        #
        # lbl_nametc = Label(frame_details, text=f"Lecturer: ", font=("yu gothic ui", 14), fg="black", bg="white")
        # lbl_nametc.place(x=5, y=95)


        # RIGHT FRAME
        self.Right_frame = LabelFrame(self.root, bd=2, bg="white", relief=RIDGE,
                                         text="List of students", font=("times new roman", 12, "bold"))
        self.Right_frame.place(x=880, y=220, width=630, height=470)

        # Tạo Treeview và Scrollbar
        self.tree = ttk.Treeview(self.Right_frame,
                                 columns=("ID", "Name", "Birth", "Time", "Date", "Section", "Status"),
                                 show="headings", height=15)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Birth", text="Birth")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Section", text="Section")
        self.tree.heading("Status", text="Status")

        self.tree.column("ID", width=60, anchor=CENTER)
        self.tree.column("Name", width=150)
        self.tree.column("Birth", width=80)
        self.tree.column("Time", width=40)
        self.tree.column("Date", width=80)
        self.tree.column("Section", width=40)
        self.tree.column("Status", width=50)

        v_scrollbar = Scrollbar(self.Right_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        v_scrollbar.pack(side=RIGHT, fill=Y)

        h_scrollbar = Scrollbar(self.Right_frame, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side=BOTTOM, fill=X)

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        self.finish_btn = Button(self.root, text="Finish", command=self.finish_session,
                                 font=("times new roman", 12), bg="lightblue")
        self.finish_btn.place(x=950, y=720, width=180, height=40)

        self.export_btn = Button(self.root, text="Xuất Excel", command=self.export_excel,
                                    font=("times new roman", 12), bg="lightblue")
        self.export_btn.place(x=1270, y=720, width=180, height=40)

    import json

    def load_class_subjects(self):
        try:
            with open("config.json", "r") as config_file:
                config_data = json.load(config_file)  # Use json.load directly
                teacher_id = config_data['teacher_id']

            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='face_recognition_sys',
                port='3306'
            )
            if conn.is_connected():
                my_cursor = conn.cursor()
                my_cursor.execute("SELECT id_class_subject FROM class_subject WHERE id_teacher = %s", (teacher_id,))
                subjects = my_cursor.fetchall()
                self.cbb_section_class['values'] = [subject[0] for subject in subjects]  # Populate Combobox

        except (FileNotFoundError, json.JSONDecodeError, mysql.connector.Error) as e:  # Handle potential errors
            print(f"Error loading subjects: {e}")
            messagebox.showerror("Error", f"Could not load class subjects: {e}") # Show a user-friendly error message
            self.cbb_section_class['values'] = [] # Set to empty list to avoid errors later

        finally:
            if conn and conn.is_connected():  # Check if connection exists before closing
                my_cursor.close()
                conn.close()

    import mysql.connector
    from mysql.connector import Error
    def add_session(self):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='face_recognition_sys',
                port='3306'
            )
            if conn.is_connected():
                my_cursor = conn.cursor()

                sql1 = ("INSERT INTO session (id_class_subject, date, start_time, end_time) VALUES (%s, %s, %s, %s)")
                id_class_subject = self.var_section_class.get()
                today = strftime('%Y-%m-%d')
                index1 = int(self.cbb_from.get())-1
                time_start = self.start_time[index1]
                if index1 == 4 or index1 == 8:
                    time_end = self.end_time[index1]
                else:
                    index2 = int(self.cbb_to.get()) - 1
                    time_end = self.end_time[index2]
                val = (id_class_subject, today, time_start, time_end)
                # print(id_class_subject, today, time_start, time_end)
                my_cursor.execute(sql1, val)
                conn.commit()

                sql2 = ("SELECT id_session FROM session WHERE "
                        "id_class_subject = %s AND date = %s "
                        "AND start_time = %s AND end_time = %s")
                my_cursor.execute(sql2, val)
                myresult = my_cursor.fetchall()
                self.id_session, = myresult[0]
                messagebox.showinfo("Success", "Added session")
                # print(self.id_session)


        finally:
            if conn.is_connected():
                my_cursor.close()
                conn.close()
    def choose_session(self, event):
        selected_item = self.cbb_session.get()
        if selected_item=="Morning" :
            self.cbb_from['values'] = ('1', '2', '3', '4', '5')
        else:
            self.cbb_from['values'] = ('6', '7', '8', '9')

    def choose_from(self, event):
        from_item = self.cbb_from.get()
        index = int(from_item) - 1
        if index==4 or index==8:
            time_start = self.start_time[index]
            time_end = self.end_time[index]
            self.lbl_time_session['text']=f"{time_start} - {time_end}"
        else :
            options = [
                ('2', '3', '4', '5'),
                ('3', '4', '5'),
                ('4', '5'),
                ('5'),
                (),
                ('7', '8', '9'),
                ('8', '9'),
                ('9'),
                ()
            ]
            self.cbb_to['values'] = options[index]

    def finish_session(self):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='face_recognition_sys',
                port='3306'
            )
            if conn.is_connected():
                my_cursor = conn.cursor()
                for item in self.tree.get_children():
                    sql = "INSERT INTO attendance(id_student, id_session, attendance_time, status) VALUES (%s, %s, %s, %s)"
                    id_student =  self.tree.item(item, 'values')[0]
                    id_session = self.id_session
                    if self.tree.item(item, 'values')[6]=="Not yet" :
                        status  = "Absent"
                        attendance_time = "00:00:00"
                    else:
                        status = self.tree.item(item, 'values')[6]
                        attendance_time = self.tree.item(item, 'values')[3]
                    # print(id_student, id_session, attendance_time, status)
                    val = (id_student, id_session, attendance_time, status)
                    my_cursor.execute(sql, val)
                    conn.commit()
                messagebox.showinfo("Success", "Finish session")
                self.tree.delete(*self.tree.get_children())

        finally:
            if conn.is_connected():
                my_cursor.close()
                conn.close()
    def choose_to(self, event):
        from_item = self.cbb_from.get()
        to_item = self.cbb_to.get()
        time_start = self.start_time[int(from_item)-1]
        time_end = self.end_time[int(to_item)-1]
        self.lbl_time_session['text'] = f"{time_start} - {time_end}"
    def search(self):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='face_recognition_sys',
                port='3306'
            )
            if conn.is_connected():
                my_cursor = conn.cursor()

                sql = ("SELECT std.id_student, std.name_student, std.birthday "
                       "FROM student std "
                       "JOIN register r ON std.id_student = r.id_student "
                       "WHERE r.id_class_subject = %s")

                id_class_subject = (self.var_section_class.get(),)

                my_cursor.execute(sql, id_class_subject)

                myresult = my_cursor.fetchall()
                self.tree.delete(*self.tree.get_children())

                for record in myresult:
                    id_student, name_student, birthday = record
                    check_time = ""
                    date = ""
                    status = "Not yet"
                    self.tree.insert("", END,
                                     values=(id_student, name_student, birthday, check_time, date, id_class_subject, status))
                self.detail_subject(id_class_subject)
        # except Error as e:
        #     print(f"Error: {e}")
        finally:
            if conn.is_connected():
                my_cursor.close()
                conn.close()
    def detail_subject(self, id_class_subject):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='face_recognition_sys',
                port='3306'
            )
            if conn.is_connected():
                my_cursor = conn.cursor()
                sql = ( "SELECT tc.name_teacher, c.id_subject, s.name_subject, s.credit, c.gr "
                       "FROM class_subject c "
                       "JOIN teacher tc ON tc.id_teacher = c.id_teacher "
                       "JOIN subject s ON s.id_subject = c.id_subject "
                       "WHERE c.id_class_subject = %s")
                my_cursor.execute(sql, id_class_subject)
                myresult = my_cursor.fetchall()
                name_teacher, id_subject, name_subject, credit, group = myresult[0]

                #==== print details
                frame_details = LabelFrame(self.root, text="Details of section", bg="white")
                frame_details.place(x=1200, y=60, width=300, height=150)

                lbl_id_subject = Label(frame_details, text=f"ID Subject: {id_subject}", font=("yu gothic ui", 14), fg="black",
                                       bg="white")
                lbl_id_subject.place(x=5, y=5)

                lbl_credit = Label(frame_details, text=f"Credit: {credit}", font=("yu gothic ui", 14), fg="black", bg="white")
                lbl_credit.place(x=200, y=5)

                lbl_name_subject = Label(frame_details, text=f"{name_subject}", font=("yu gothic ui", 14), fg="black",
                                         bg="white")
                lbl_name_subject.place(x=5, y=35)

                lbl_group = Label(frame_details, text=f"Group: {group}", font=("yu gothic ui", 14), fg="black", bg="white")
                lbl_group.place(x=5, y=65)

                lbl_nametc = Label(frame_details, text=f"Lecturer: {name_teacher}", font=("yu gothic ui", 14), fg="black", bg="white")
                lbl_nametc.place(x=5, y=95)

        finally:
            if conn.is_connected():
                my_cursor.close()
                conn.close()

    def update_attendance(self, id_student):
        for item in self.tree.get_children():
            if self.tree.item(item, 'values')[0] == id_student:
                attendance_time = datetime.now().strftime('%H:%M')
                current_date = datetime.now().strftime('%Y/%m/%d')
                self.tree.item(item, values=(id_student,
                                             self.tree.item(item, 'values')[1],
                                             self.tree.item(item, 'values')[2],
                                             attendance_time,
                                             current_date,
                                             self.tree.item(item, 'values')[5],
                                             "Present"
                                             ))
                self.tree.item(item, tags=("highlight",))
                self.tree.tag_configure("highlight", background="lightgreen")
                break

    def export_excel(self):
        import pandas as pd
        from tkinter import messagebox

        # Kiểm tra danh sách nhận diện
        if hasattr(self, 'recognized_students') and self.recognized_students:
            data = {"Student ID": self.recognized_students}
            df = pd.DataFrame(data)
            output_path = "SinhVienDaDiemDanh.xlsx"  # Đường dẫn file xuất

            try:
                df.to_excel(output_path, index=False)
                # Hiện thông báo thành công
                messagebox.showinfo("Export Success", f"Exported successfully to {output_path}")
            except Exception as e:
                # Hiện thông báo lỗi nếu xảy ra
                messagebox.showerror("Export Error", f"Failed to export: {e}")
        else:
            # Hiện thông báo không có dữ liệu để xuất
            messagebox.showwarning("No Data", "No recognized students to export.")

    def is_clicked(self):
        self.isClicked = True

    def open_camera(self):
        self.realtime_face_recognition()

    def load_teacher_id(self):
        # Đọc thông tin từ tệp cấu hình
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = self.json.load(f)
                return config.get('teacher_id', 'Unknown')
        return 'Unknown'

    def get_teacher_name(self, teacher_id):
        # Kết nối đến cơ sở dữ liệu để lấy tên giáo viên
        conn = mysql.connector.connect(host='localhost', user='root', password='', database='face_recognition_sys',
                                       port='3306')
        my_cursor = conn.cursor()
        my_cursor.execute("SELECT name_teacher FROM teacher WHERE id_teacher=%s", (teacher_id,))
        row = my_cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        return 'Unknown'

    backends = [
        'opencv',
        'ssd',
        'dlib',
        'mtcnn',
        'fastmtcnn',
        'retinaface',
        'mediapipe',
        'yolov8',
        'yunet',
        'centerface',
    ]
    alignment_modes = [True, False]
    models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib", "SFace"]
    metrics = ["cosine", "euclidean", "euclidean_l2"]
    img = "DataProcessed/.jpg"
    # ham nhan dien quan trong
    def realtime_face_recognition(self):
        def recognize_face(face_embedding, known_faces, threshold=1.0):
            for student_id, db_embedding in known_faces.items():
                dist = np.linalg.norm(face_embedding - db_embedding)
                if dist < threshold:
                    return student_id, dist
            return "Unknown", None

        frame_count = 0
        N = 5
        face_db = {}
        embedding_dir = 'DataEmbeddings/'
        for file in os.listdir(embedding_dir):
            if file.endswith('_embedding.npy'):
                student_id = file.split('_embedding.npy')[0]
                face_db[student_id] = np.load(os.path.join(embedding_dir, file))

        app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
        app.prepare(ctx_id=0, det_size=(640, 640))

        cap = cv2.VideoCapture(self.camera_name)
        while True:
            ret, frame = cap.read()

            faces = app.get(frame)
            # Vẽ các ô nhận diện lên hình ảnh
            # frame_with_faces = frame
            frame_with_faces = app.draw_on(frame, faces)
            if not ret:
                break
            frame = cv2.resize(frame, (800, 500))
            frame2D = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_3c = cv2.cvtColor(frame2D, cv2.COLOR_GRAY2BGR)
            frame_count += 1
            if frame_count % N == 0:
                detected_ids = []
                for face in faces:
                    face_embedding = face.normed_embedding
                    face.bbox = face.bbox.astype(int)
                    student_id, dist = recognize_face(face_embedding, face_db)
                    detected_ids.append(student_id)
                    if face.bbox is not None and len(face.bbox) >= 4:
                        x1, y1, x2, y2 = map(int, face.bbox)

                        cv2.putText(frame_with_faces, f'{student_id}', (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.rectangle(frame_with_faces, (x1, y1), (x2, y2), (255, 0, 0), 2)
                # xuat ra excel
                    # Lưu các ID đã nhận diện vào self.recognized_students
                    if not hasattr(self, 'recognized_students'):
                        self.recognized_students = []

                    self.recognized_students.extend(detected_ids)
                    self.recognized_students = list(set(self.recognized_students))  # Loại bỏ trùng lặp
                # check file ben phai
                current_time = datetime.now()
                for student_id in detected_ids:
                    if student_id in self.recognition_start_time:
                        if (current_time - self.recognition_start_time[student_id]).total_seconds() >= 2:
                            self.update_attendance(student_id)
                            self.recognition_start_time.pop(student_id)
                    else:
                        self.recognition_start_time[student_id] = current_time

                # cv2.imshow('Camera', frame_with_faces)
                rgb_frame = cv2.cvtColor(frame_with_faces, cv2.COLOR_BGR2RGB)
                rgb_frame = Image.fromarray(rgb_frame)
                tk_frame = ImageTk.PhotoImage(rgb_frame)

                self.panel['image'] = tk_frame
                self.panel.update()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if self.isClicked:
                break

        cap.release()
        cv2.destroyAllWindows()
if __name__=="__main__":
    root=Tk()
    obj=attendance(root)
    root.mainloop()
