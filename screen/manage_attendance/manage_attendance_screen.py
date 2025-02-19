# attendance
import json
from time import strftime
from datetime import *
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image
import mysql.connector
import os
import numpy as np
import pyrealsense2 as rs
import cv2
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
import logging
import time

class attendance:
    def __init__(self, root):
        # Đọc thông tin từ config.json
        self.teacher_id = self.load_teacher_id()
        self.teacher_name = self.get_teacher_name(self.teacher_id)
        self.camera_name = 1
        self.root = root
        self.root.geometry("1530x790+0+0")
        self.root.title("Attendance")
        self.isClickedClose = False
        self.recognition_start_time = {}
        self.var_section_class = StringVar()
        self.start_time = ['7:00', '7:50', '8:50', '9:50', '10:40', '13:30', '14:20', '15:20', '16:10']
        self.end_time =['7:50', '8:40', '9:40', '10:40', '11:30', '14:20', '15:10', '16:10', '17:00']
        self.id_session = StringVar()
        self.embeddings_dir = '../../assets/DataEmbeddings/'
        self.depth_min = 300
        self.depth_max = 1500
        self.similarity_threshold = 0.5
        self.frame_width = 640
        self.frame_height = 480


        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img = os.path.join(BASE_DIR,'..', '..', 'assets', 'ImageDesign', 'img.png')
        img = os.path.abspath(img)

        if not os.path.exists(img):
            print("File không tồn tại:", img)

        img = Image.open(img)
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

        # self.cbb_session = ttk.Combobox(self.left_frame, values=["Morning", "Afternoon"])
        # self.cbb_session.place(x=20, y=530, width=120)
        # self.cbb_session.bind("<<ComboboxSelected>>", self.choose_session)
        #
        # self.cbb_from = ttk.Combobox(self.left_frame, values=[])
        # self.cbb_from.place(x=200, y=530, width=40)
        # self.cbb_from.bind("<<ComboboxSelected>>", self.choose_from)
        #
        # self.cbb_to = ttk.Combobox(self.left_frame, values=[])
        # self.cbb_to.place(x=295, y=530, width=40)
        # self.cbb_to.bind("<<ComboboxSelected>>", self.choose_to)

        # Label(self.left_frame, text="From: ", fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 14)).place(x=150, y=532)
        # Label(self.left_frame, text="To: ", fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 14)).place(x=260, y=532)
        #
        # btn_add = Button(self.left_frame, text="Add", bg="#57a1f8", fg="black", command=self.add_session)
        # btn_add.place(x=500, y=530, width=50, height=25)

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

        img_search = Image.open('../../assets/ImageDesign/search_icon.png')
        img_search = img_search.resize((27, 27), Image.Resampling.LANCZOS)
        self.img_searchtk = ImageTk.PhotoImage(img_search)
        btn_report = Button(search_frame, command=self.search, image=self.img_searchtk, borderwidth=0)
        btn_report.place(x=200, y=15)

        self.load_class_subjects()  # Load subjects AFTER creating the Combobox

        self.lbl_time_session = Label(self.left_frame, text="", fg='black', border=0, bg='white',font=('Microsoft YaHei UI Light', 14))
        self.lbl_time_session.place(x=350, y=532)

        # # ========== heading
        # lbl_name = Label(self.root, bg="white", text=f"Teacher:  {self.teacher_name}",
        #                  font=("yu gothic ui", 15, "bold"), bd=0)
        # lbl_name.place(x=1000, y=50)





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
            with open("../login/config.json", "r") as config_file:
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
        from datetime import datetime
        import os

        today = datetime.now().strftime("%d/%m")  # Lấy ngày hiện tại

        # Lấy dữ liệu từ TreeView
        attendance_data = []
        for index, item in enumerate(self.tree.get_children(), start=1):
            values = self.tree.item(item, "values")
            student_id = values[0]
            student_name = values[1]
            class_name = values[2]
            status = values[3] if len(values) > 3 else ""

            attendance_data.append([index, student_id, student_name, class_name, status])

        # Chuyển thành DataFrame
        df_new = pd.DataFrame(attendance_data, columns=["STT", "Mã", "Họ và tên", "Birth", today])

        # Đường dẫn file Excel
        class_folder = self.var_section_class.get()
        output_path = f"{class_folder}/attendance.xlsx"

        try:
            os.makedirs(class_folder, exist_ok=True)

            if os.path.exists(output_path):
                df_old = pd.read_excel(output_path)

                # Xóa cột "Số lần vắng" cũ nếu có
                if "Số lần vắng" in df_old.columns:
                    df_old = df_old.drop(columns=["Số lần vắng"])

                if today in df_old.columns:
                    # Nếu ngày đã tồn tại -> Cập nhật lại dữ liệu
                    df_old.drop(columns=[today], inplace=True)

                # Ghép dữ liệu mới vào bên phải
                df_old = df_old.merge(df_new, on=["STT", "Mã", "Họ và tên", "Birth"], how="left")
            else:
                df_old = df_new

            # Tính lại số lần vắng
            df_old["Số lần vắng"] = df_old.iloc[:, 4:].apply(lambda row: (row == "").sum(), axis=1)

            # Thống kê số sinh viên đi học
            total_students = len(df_old)
            attended_count = df_old[today].apply(lambda x: 1 if x != "" else 0).sum()
            attendance_summary = f"{attended_count}/{total_students}"

            # Cập nhật dòng tổng kết ở cuối (nếu đã có thì sửa lại)
            if (df_old.iloc[-1, 1] == ""):  # Kiểm tra nếu hàng cuối là thống kê
                df_old.iloc[-1, 4] = attendance_summary
            else:
                summary_row = [""] * 4 + [attendance_summary] + [""] * (df_old.shape[1] - 5)
                df_old.loc[len(df_old)] = summary_row

            # Ghi file Excel
            df_old.to_excel(output_path, index=False)
            messagebox.showinfo("Export Success", f"Attendance updated and exported to {output_path}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

    def is_clicked(self):
        try:
            self.isClickedClose = False
            print("Close button clicked")
            # Thêm các lệnh để dừng camera
            if hasattr(self, 'pipeline'):
                self.pipeline.stop()
            cv2.destroyAllWindows()

        except Exception as e:
            print(f"Error in is_clicked: {e}")

    def open_camera(self):
        self.isClickedClose = True
        self.realtime_face_recognition()

    def load_teacher_id(self):
        # Đọc thông tin từ tệp cấu hình
        if os.path.exists('../login/config.json'):
            with open('../login/config.json', 'r') as f:
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

    img = "DataProcessed/.jpg"

    def realtime_face_recognition(self):
        self.run_face_recognition_3d(
            embeddings_dir=self.embeddings_dir,
            depth_min=self.depth_min,
            depth_max=self.depth_max,
            similarity_threshold=self.similarity_threshold,
            frame_width=self.frame_width,
            frame_height=self.frame_height
        )
# 300,1500
    def run_face_recognition_3d(self, embeddings_dir='../../assets/DataEmbeddings/', depth_min=0, depth_max=15000000,
                                similarity_threshold=0.5, frame_width=640, frame_height=480):

        # Kiểm tra xem thư mục có tồn tại không
        if not os.path.exists(embeddings_dir):
            raise ValueError(f"Directory does not exist: {embeddings_dir}")
        print(f"Embeddings directory: {embeddings_dir}")
        # Cấu hình logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)


        def _load_database():
            database = {}
            try:
                for file in os.listdir(embeddings_dir):
                    if file.endswith("_embedding.npy"):
                        #person_id = os.path.splitext(file)[0]
                        person_id = file.split('_embedding.npy')[0]
                        database[person_id] = np.load(os.path.join(embeddings_dir, file))
                logger.info(f"Đã tải thành công {len(database)} embeddings")
                return database
            except Exception as e:
                logger.error(f"Lỗi khi tải database: {str(e)}")
                raise

        def _setup_realsense():
            pipeline = rs.pipeline()
            config = rs.config()
            # Lấy thông tin thiết bị
            context = rs.context()
            devices = context.query_devices()
            for device in devices:
                logger.info(f"Thiết bị được kết nối: {device.get_info(rs.camera_info.name)}")
                logger.info(f"Serial number: {device.get_info(rs.camera_info.serial_number)}")
                logger.info(f"Firmware version: {device.get_info(rs.camera_info.firmware_version)}")
            # Thêm bộ lọc để cải thiện chất lượng depth
            config.enable_stream(rs.stream.color, frame_width, frame_height, rs.format.bgr8, 15)
            config.enable_stream(rs.stream.depth, frame_width, frame_height, rs.format.z16, 15)

            # Align depth với color frame
            align = rs.align(rs.stream.color)

            try:
                pipeline.start(config)
                logger.info("Đã khởi tạo RealSense camera thành công")
                return pipeline, align
            except Exception as e:
                logger.error(f"Lỗi khởi tạo camera: {str(e)}")
                raise

        def _setup_face_analyzer():
            app = FaceAnalysis(providers=['CPUExecutionProvider'])
            app.prepare(ctx_id=-1)
            return app

        def _find_best_match(embedding, database):
            if not database:
                return "No database loaded", 0

            similarities = {k: cosine_similarity([embedding], [v])[0][0]
                            for k, v in database.items()}
            best_match = max(similarities, key=similarities.get)
            confidence = similarities[best_match]

            return (best_match, confidence) if confidence > similarity_threshold else ("Unknown", confidence)

        def _process_face(face, depth_image, depth_frame, database):

            box = face.bbox.astype(int)
            embedding = face.embedding

            # Lấy vùng depth của khuôn mặt
            center_x = min(max((box[0] + box[2]) // 2, 0), depth_image.shape[1] - 1)
            center_y = min(max((box[1] + box[3]) // 2, 0), depth_image.shape[0] - 1)

            depth_value = depth_frame.get_distance(center_x, center_y) * 1000  # Đổi sang mm

            # Kiểm tra liveness
            if not (depth_min < depth_value < depth_max):
                return box, "Don't Know", depth_value, 0  # Chỉ nếu depth thực sự không hợp lệ

            person_id, confidence = _find_best_match(embedding, database)

            if person_id == "No database loaded" or person_id == "Unknown":
                return box, "Unknown", depth_value, confidence  # Người lạ, không phải Don't Know

            return box, person_id, depth_value, confidence

        # Tải cơ sở dữ liệu
        database = _load_database()

        # Khởi tạo RealSense
        pipeline, align = _setup_realsense()

        # Khởi tạo FaceAnalyzer
        face_analyzer = _setup_face_analyzer()

        # Khởi tạo ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=2)
        try:
            last_fps_time = time.time()
            frame_count = 0
            fps = 0  # Khởi tạo fps với giá trị mặc định

            while True:
                if self.isClickedClose == False:
                    break
                # Lấy và xử lý frame
                frames = pipeline.wait_for_frames()
                aligned_frames = align.process(frames)

                color_frame = aligned_frames.get_color_frame()
                depth_frame = aligned_frames.get_depth_frame()

                if not color_frame or not depth_frame:
                    continue

                color_image = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(depth_frame.get_data())

                # Tính FPS
                frame_count += 1
                current_time = time.time()
                if current_time - last_fps_time > 1:
                    fps = frame_count
                    frame_count = 0
                    last_fps_time = current_time

                # Nhận diện khuôn mặt
                faces = face_analyzer.get(color_image)

                # Xử lý song song các khuôn mặt
                face_futures = [
                    executor.submit(_process_face, face, depth_image, depth_frame, database)
                    for face in faces
                ]

                detected_ids = []  # Khởi tạo list để lưu các ID đã nhận diện

                # Hiển thị kết quả
                for future in face_futures:
                    box, person_id, depth_value, confidence = future.result()

                    # Chỉ nhận diện nếu confidence lớn hơn ngưỡng
                    if confidence > self.similarity_threshold and person_id != "Unknown":
                        detected_ids.append(person_id)  # Thêm ID vào danh sách đã nhận diện

                        # Cập nhật trạng thái điểm danh
                        current_time = datetime.now()
                        for person_id in detected_ids:
                            if person_id in self.recognition_start_time:
                                if (current_time - self.recognition_start_time[person_id]).total_seconds() >= 1:
                                    self.update_attendance(person_id)
                                    self.recognition_start_time.pop(person_id)
                            else:
                                self.recognition_start_time[person_id] = current_time
                # Cập nhật điểm danh ngay khi nhận diện

                    # Vẽ khung và thông tin trên ảnh màu
                    color = (0, 255, 0) if person_id != "Don't Know" else (0, 0, 255)
                    cv2.rectangle(color_image, (box[0], box[1]), (box[2], box[3]), color, 2)

                    label = f"{person_id} ({confidence:.2f})" if person_id != "Don't Know" else person_id
                    cv2.putText(color_image, label, (box[0], box[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    cv2.putText(color_image, f"Depth: {depth_value:.0f}mm",
                                (box[0], box[3] + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                print("DETECT ne " + ', '.join(detected_ids))
                # Cập nhật danh sách recognized_students
                if not hasattr(self, 'recognized_students'):
                    self.recognized_students = []
                self.recognized_students.extend(detected_ids)
                self.recognized_students = list(set(self.recognized_students))  # Loại bỏ trùng lặp

                # Hiển thị FPS
                cv2.putText(color_image, f"FPS: {fps}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Hiển thị ảnh màu
                #cv2.imshow("3D Face Recognition", color_image)
                rgb_frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
                rgb_frame = Image.fromarray(rgb_frame)
                tk_frame = ImageTk.PhotoImage(rgb_frame)
                self.panel['image'] = tk_frame
                self.panel.update()
                # Thoát nếu nhấn phím 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


        except Exception as e:
            logger.error(f"Lỗi trong quá trình xử lý: {str(e)}")
        finally:
            logger.info("Đang dọn dẹp tài nguyên...")
            pipeline.stop()
            executor.shutdown()
            cv2.destroyAllWindows()

if __name__=="__main__":
    root=Tk()
    obj=attendance(root)

    root.mainloop()
