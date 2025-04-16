import json
from time import strftime
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import mysql.connector
import os
import numpy as np
import pyrealsense2 as rs
import cv2
from insightface.app import FaceAnalysis
from concurrent.futures import ThreadPoolExecutor
import time
import math
import warnings
import dlib

warnings.simplefilter("ignore", category=FutureWarning)

class attendance:
    def __init__(self, root):
        self.id_teacher = self.load_id_teacher()
        self.teacher_name = self.get_teacher_name(self.id_teacher)
        self.camera_name = 1
        self.root = root
        self.root.geometry("1530x1000+0+0")
        self.root.title("Attendance")
        self.isClickedClose = False
        self.recognition_start_time = {}
        self.var_section_class = StringVar()
        self.start_time = ['7:00', '7:50', '8:50', '9:50', '10:40', '13:30', '14:20', '15:20', '16:10']
        self.end_time = ['7:50', '8:40', '9:40', '10:40', '11:30', '14:20', '15:10', '16:10', '17:00']
        self.id_session = StringVar()

        # Khởi tạo RealSense
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.align = rs.align(rs.stream.color)
        self.pipeline.start(self.config)

        # Khởi tạo InsightFace
        self.app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

        # Khởi tạo FaceAntiSpoofing
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.nose_tip_index = 33
        self.left_eye_indices = list(range(36, 42))
        self.right_eye_indices = list(range(42, 48))
        self.jaw_indices = list(range(0, 17))
        self.tolerance = 20  # Dung sai cho so sánh chiều sâu (mm)
        self.std_dev_threshold = 15  # Ngưỡng độ lệch chuẩn cho vùng khuôn mặt

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'assets', 'ImageDesign', 'img.png'))
        if os.path.exists(img):
            img = Image.open(img).resize((1530, 1000))
            self.imgtk = ImageTk.PhotoImage(img)
            lbl_bg = Label(self.root, image=self.imgtk, bg='white')
            lbl_bg.place(x=0, y=0)
        else:
            print("Background image not found:", img)

        heading = Label(self.root, text="Hệ thống điểm danh khuôn mặt", font=("yu gothic ui", 15, "bold"),
                       bg="white", fg="#57a1f8", bd=0)
        heading.place(x=400, y=30, width=650, height=30)

        self.left_frame = LabelFrame(self.root, bd=2, bg="white", relief=RIDGE, text="Camera",
                                    font=("times new roman", 12, "bold"))
        self.left_frame.place(x=30, y=90, width=820, height=680)
        self.panel = Label(self.left_frame, borderwidth=2, relief="groove")
        self.panel.place(x=8, y=20, width=800, height=480)

        btn_open = Button(self.left_frame, text="Open", bg="#57a1f8", fg="black", command=self.open_camera)
        btn_open.place(x=100, y=580, width=180, height=50)
        btn_close = Button(self.left_frame, text="Close", bg="#57a1f8", fg="black", command=self.is_clicked)
        btn_close.place(x=500, y=580, width=180, height=50)

        search_frame = LabelFrame(self.root, bd=2, bg="white", relief=RIDGE, text="Find section class",
                                 font=("times new roman", 12, "bold"))
        search_frame.place(x=10, y=800, width=250, height=80)
        self.cbb_section_class = ttk.Combobox(search_frame, textvariable=self.var_section_class, state='readonly')
        self.cbb_section_class.place(x=5, y=15, width=190, height=30)

        img_search = Image.open(os.path.join(BASE_DIR, '..', '..', 'assets', 'ImageDesign', 'search_icon.png')).resize((27, 27))
        self.img_searchtk = ImageTk.PhotoImage(img_search)
        Button(search_frame, command=self.search, image=self.img_searchtk, borderwidth=0).place(x=200, y=15)

        self.load_class_subjects()
        self.lbl_time_session = Label(self.left_frame, text="", fg='black', bg='white',
                                    font=('Microsoft YaHei UI Light', 14))
        self.lbl_time_session.place(x=350, y=532)

        self.Right_frame = LabelFrame(self.root, bd=2, bg="white", relief=RIDGE,
                                     text="List of students", font=("times new roman", 12, "bold"))
        self.Right_frame.place(x=880, y=90, width=630, height=850)

        self.tree = ttk.Treeview(self.Right_frame,
                                columns=("ID", "Name", "Birth", "Time", "Date", "Section", "Status"),
                                show="headings", height=50)
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

        self.export_btn = Button(self.root, text="Export to Statistic", command=self.export_excel,
                               font=("times new roman", 12), bg="lightblue")
        self.export_btn.place(x=1100, y=930, width=180, height=40)

    def load_id_teacher(self):
        if os.path.exists('../login/config.json'):
            with open('../login/config.json', 'r') as f:
                return json.load(f).get('id_teacher', 'Unknown')
        return 'Unknown'

    def get_teacher_name(self, id_teacher):
        conn = mysql.connector.connect(host='localhost', user='root', password='',
                                     database='face_recognition_sys', port='3306')
        my_cursor = conn.cursor()
        my_cursor.execute("SELECT name_teacher FROM teacher WHERE id_teacher=%s", (id_teacher,))
        row = my_cursor.fetchone()
        conn.close()
        return row[0] if row else 'Unknown'

    def load_class_subjects(self):
        try:
            with open("../login/config.json", "r") as config_file:
                config_data = json.load(config_file)
                id_teacher = config_data['id_teacher']
            conn = mysql.connector.connect(host='localhost', user='root', password='',
                                         database='face_recognition_sys', port='3306')
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT id_class_subject FROM class_subject WHERE id_teacher = %s", (id_teacher,))
            subjects = my_cursor.fetchall()
            self.cbb_section_class['values'] = [subject[0] for subject in subjects]
        except Exception as e:
            messagebox.showerror("Error", f"Could not load class subjects: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                my_cursor.close()
                conn.close()

    def add_session(self):
        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='',
                                         database='face_recognition_sys', port='3306')
            my_cursor = conn.cursor()
            sql = ("INSERT INTO session (id_class_subject, date, start_time, end_time) VALUES (%s, %s, %s, %s)")
            id_class_subject = self.var_section_class.get()
            today = strftime('%Y-%m-%d')
            index1 = int(self.cbb_from.get()) - 1
            time_start = self.start_time[index1]
            if index1 in [4, 8]:
                time_end = self.end_time[index1]
            else:
                index2 = int(self.cbb_to.get()) - 1
                time_end = self.end_time[index2]
            val = (id_class_subject, today, time_start, time_end)
            my_cursor.execute(sql, val)
            conn.commit()
            my_cursor.execute("SELECT id_session FROM session WHERE id_class_subject = %s AND date = %s "
                            "AND start_time = %s AND end_time = %s", val)
            self.id_session.set(str(my_cursor.fetchone()[0]))
            messagebox.showinfo("Success", "Added session")
        finally:
            if 'conn' in locals() and conn.is_connected():
                my_cursor.close()
                conn.close()

    def choose_session(self, event):
        selected_item = self.cbb_session.get()
        self.cbb_from['values'] = ('1', '2', '3', '4', '5') if selected_item == "Morning" else ('6', '7', '8', '9')

    def choose_from(self, event):
        index = int(self.cbb_from.get()) - 1
        if index in [4, 8]:
            self.lbl_time_session['text'] = f"{self.start_time[index]} - {self.end_time[index]}"
        else:
            options = [ ('2', '3', '4', '5'), ('3', '4', '5'), ('4', '5'), ('5'), (),
                       ('7', '8', '9'), ('8', '9'), ('9'), () ]
            self.cbb_to['values'] = options[index]

    def choose_to(self, event):
        from_item = self.cbb_from.get()
        to_item = self.cbb_to.get()
        time_start = self.start_time[int(from_item)-1]
        time_end = self.end_time[int(to_item)-1]
        self.lbl_time_session['text'] = f"{time_start} - {time_end}"

    def search(self):
        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='',
                                         database='face_recognition_sys', port='3306')
            my_cursor = conn.cursor()
            sql = ("SELECT std.id_student, std.name_student, std.birthday "
                  "FROM student std JOIN register r ON std.id_student = r.id_student "
                  "WHERE r.id_class_subject = %s")
            my_cursor.execute(sql, (self.var_section_class.get(),))
            myresult = my_cursor.fetchall()
            self.tree.delete(*self.tree.get_children())
            for record in myresult:
                self.tree.insert("", END,
                                values=(record[0], record[1], record[2], "", "", self.var_section_class.get(), "Not yet"))
            self.detail_subject((self.var_section_class.get(),))
        finally:
            if 'conn' in locals() and conn.is_connected():
                my_cursor.close()
                conn.close()

    def detail_subject(self, id_class_subject):
        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='',
                                         database='face_recognition_sys', port='3306')
            my_cursor = conn.cursor()
            sql = ("SELECT tc.name_teacher, c.id_subject, s.name_subject, s.credit, c.gr "
                  "FROM class_subject c JOIN teacher tc ON tc.id_teacher = c.id_teacher "
                  "JOIN subject s ON s.id_subject = c.id_subject WHERE c.id_class_subject = %s")
            my_cursor.execute(sql, id_class_subject)
            name_teacher, id_subject, name_subject, credit, group = my_cursor.fetchone()
            frame_details = LabelFrame(self.root, text="Details of section", bg="white")
            frame_details.place(x=400, y=800, width=300, height=150)
            Label(frame_details, text=f"ID Subject: {id_subject}", font=("yu gothic ui", 14),
                 fg="black", bg="white").place(x=5, y=5)
            Label(frame_details, text=f"Credit: {credit}", font=("yu gothic ui", 14),
                 fg="black", bg="white").place(x=200, y=5)
            Label(frame_details, text=f"{name_subject}", font=("yu gothic ui", 14),
                 fg="black", bg="white").place(x=5, y=35)
            Label(frame_details, text=f"Group: {group}", font=("yu gothic ui", 14),
                 fg="black", bg="white").place(x=5, y=65)
            Label(frame_details, text=f"Lecturer: {name_teacher}", font=("yu gothic ui", 14),
                 fg="black", bg="white").place(x=5, y=95)
        finally:
            if 'conn' in locals() and conn.is_connected():
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
                                            "Present"))
                self.tree.item(item, tags=("highlight",))
                self.tree.tag_configure("highlight", background="lightgreen")
                break

    def export_excel(self):
        import pandas as pd
        today = datetime.now().strftime("%d/%m")
        attendance_data = []
        for index, item in enumerate(self.tree.get_children(), start=1):
            values = self.tree.item(item, "values")
            student_id = values[0]
            student_name = values[1]
            birthday = values[2]
            status = values[6]
            attendance_data.append([index, student_id, student_name, birthday, status])
        df_new = pd.DataFrame(attendance_data, columns=["STT", "Mã", "Họ và tên", "Birth", today])
        class_folder = self.var_section_class.get()
        output_path = f"{class_folder}/attendance.xlsx"
        try:
            os.makedirs(class_folder, exist_ok=True)
            if os.path.exists(output_path):
                df_old = pd.read_excel(output_path)
                if "Số lần vắng" in df_old.columns:
                    df_old = df_old.drop(columns=["Số lần vắng"])
                if today in df_old.columns:
                    df_old.drop(columns=[today], inplace=True)
                df_old = df_old.merge(df_new, on=["STT", "Mã", "Họ và tên", "Birth"], how="left")
            else:
                df_old = df_new
            df_old["Số lần vắng"] = df_old.iloc[:, 4:].apply(lambda row: (row == "").sum(), axis=1)
            df_old.to_excel(output_path, index=False)
            messagebox.showinfo("Export Success", f"Attendance updated and exported to {output_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

    def is_clicked(self):
        self.isClickedClose = True
        if hasattr(self, 'pipeline'):
            self.pipeline.stop()
        cv2.destroyAllWindows()

    def open_camera(self):
        self.isClickedClose = False
        self.attendance_2d()

    def calculate_face_angle(self, face):
        landmarks = face.kps
        left_eye = landmarks[0]
        right_eye = landmarks[1]
        delta_x = right_eye[0] - left_eye[0]
        delta_y = right_eye[1] - left_eye[1]
        angle = math.degrees(math.atan2(delta_y, delta_x))
        return abs(angle)

    def recognize_face(self, face_embedding, known_faces, threshold=1.0):
        best_student_id = "Unknown"
        best_dist = float('inf')

        def compute_distance(db_embedding):
            return np.linalg.norm(face_embedding - db_embedding)

        for student_id, embeddings in known_faces.items():
            with ThreadPoolExecutor() as executor:
                distances = list(executor.map(compute_distance, embeddings))
            min_dist = min(distances)
            if min_dist < best_dist:
                best_dist = min_dist
                best_student_id = student_id

        if best_dist < threshold:
            print(f"Recognized {best_student_id} with distance {best_dist:.2f}")
            return best_student_id, best_dist
        else:
            print(f"No match found (best distance {best_dist:.2f} >= threshold {threshold})")
            return "Unknown", None

    def detect_faces_3d(self, color_image, depth_image, faces):
        results = []
        for face in faces:
            # Convert InsightFace bbox to dlib rectangle
            box = face.bbox.astype(int)
            dlib_rect = dlib.rectangle(left=box[0], top=box[1], right=box[2], bottom=box[3])

            # Lấy điểm mốc
            landmarks = self.landmark_predictor(color_image, dlib_rect)

            # Trích xuất tọa độ điểm mốc
            landmark_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(68)]

            # Lấy giá trị chiều sâu cho các điểm mốc
            landmark_depths = []
            for x, y in landmark_points:
                if 0 <= x < depth_image.shape[1] and 0 <= y < depth_image.shape[0]:
                    depth = depth_image[y, x]
                    landmark_depths.append(depth)
                else:
                    landmark_depths.append(0)

            # Kiểm tra dữ liệu chiều sâu thô
            valid_depths = [d for d in landmark_depths if d > 0]
            if len(valid_depths) < 0.5 * len(landmark_depths):
                print("Dữ liệu chiều sâu không hợp lệ")
                continue

            nose_depth = landmark_depths[self.nose_tip_index]
            mean_left_eye_depth = np.mean([landmark_depths[i] for i in self.left_eye_indices if landmark_depths[i] > 0])
            mean_right_eye_depth = np.mean([landmark_depths[i] for i in self.right_eye_indices if landmark_depths[i] > 0])
            #mean_jaw_depth = np.mean([landmark_depths[i] for i in self.jaw_indices if landmark_depths[i] > 0])

            # Tính độ lệch chuẩn của vùng khuôn mặt
            face_region_depth = depth_image[box[1]:box[3], box[0]:box[2]]
            std_dev = np.std(face_region_depth)

            # Kiểm tra cấu trúc chiều sâu (mũi gần hơn trung bình mắt)
            avg_eye_depth = (mean_left_eye_depth + mean_right_eye_depth) / 2 if (mean_left_eye_depth and mean_right_eye_depth) else 0
            is_nose_closer = nose_depth < avg_eye_depth - self.tolerance

            # Quyết định dựa trên độ lệch chuẩn và cấu trúc
            is_real = std_dev > self.std_dev_threshold and is_nose_closer

            results.append({
                'face': face,
                'is_real': is_real,
                'nose_depth': nose_depth,
                'std_dev': std_dev
            })

        return results

    def attendance_2d(self):
        # Load database from subdirectories
        face_db = {}
        embedding_dir = '../../assets/DataEmbeddings/'
        for student_dir in os.listdir(embedding_dir):
            student_path = os.path.join(embedding_dir, student_dir)
            if os.path.isdir(student_path):
                student_id = student_dir
                embeddings = []
                for file in os.listdir(student_path):
                    if file.endswith('.npy'):
                        embedding_path = os.path.join(student_path, file)
                        embedding = np.load(embedding_path)
                        embeddings.append(embedding)
                if embeddings:
                    face_db[student_id] = embeddings

        if not face_db:
            messagebox.showwarning("Warning", "No embeddings found in DataEmbeddings directory!")
            return

        valid_distance_start = 0
        capture_delay = 2  # seconds
        depth_min = 300  # mm
        depth_max = 1500  # mm
        threshold = 1.0

        while not self.isClickedClose:
            frames = self.pipeline.wait_for_frames()
            aligned_frames = self.align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            if not color_frame or not depth_frame:
                continue

            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())
            faces = self.app.get(color_image)

            detected_ids = []
            face_results = self.detect_faces_3d(color_image, depth_image, faces)

            for result in face_results:
                face = result['face']
                is_real = result['is_real']
                box = face.bbox.astype(int)
                center_x = (box[0] + box[2]) // 2
                center_y = (box[1] + box[3]) // 2
                depth_value = depth_frame.get_distance(center_x, center_y) * 1000  # mm
                angle = self.calculate_face_angle(face)

                # Kiểm tra khoảng cách và góc mặt
                if not (depth_min < depth_value < depth_max) or angle > 15 or not is_real:
                    cv2.rectangle(color_image, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
                    cv2.putText(color_image, "Invalid" if not is_real else "Out of Range", (box[0], box[1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    continue

                embedding = face.normed_embedding
                student_id, dist = self.recognize_face(embedding, face_db, threshold)
                detected_ids.append(student_id)

                cv2.rectangle(color_image, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
                cv2.putText(color_image, f"{student_id} ({dist:.2f})" if dist else student_id,
                           (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(color_image, f"Depth: {depth_value:.0f}mm", (box[0], box[3] + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                cv2.putText(color_image, "Real", (box[0], box[3] + 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                current_time = time.time()
                if student_id != "Unknown":
                    if student_id in self.recognition_start_time:
                        if (current_time - self.recognition_start_time[student_id]) >= capture_delay:
                            self.update_attendance(student_id)
                            self.recognition_start_time.pop(student_id)
                    else:
                        self.recognition_start_time[student_id] = current_time

            if not hasattr(self, 'recognized_students'):
                self.recognized_students = []
            self.recognized_students.extend([id for id in detected_ids if id != "Unknown"])
            self.recognized_students = list(set(self.recognized_students))

            rgb_frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            rgb_frame = cv2.resize(rgb_frame, (800, 480))
            tk_frame = ImageTk.PhotoImage(Image.fromarray(rgb_frame))
            self.panel['image'] = tk_frame
            self.panel.image = tk_frame
            self.panel.update()

            self.root.update()

        self.pipeline.stop()

if __name__ == "__main__":
    root = Tk()
    obj = attendance(root)
    root.mainloop()