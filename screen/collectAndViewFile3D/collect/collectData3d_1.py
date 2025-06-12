
import numpy as np
import cv2
from insightface.app import FaceAnalysis
import dlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont  # Thêm ImageDraw, ImageFont
import threading
from queue import Queue
import pyrealsense2 as rs
import traceback

model_path = "../../manage_attendance/shape_predictor_68_face_landmarks.dat"
# --- Configuration ---
DLIB_LANDMARK_MODEL = "../../manage_attendance/shape_predictor_68_face_landmarks.dat"
DEBUG_MODE = True
# Đường dẫn đến file font .ttf hỗ trợ tiếng Việt.
# Thay đổi nếu cần thiết, ví dụ: "/usr/share/fonts/truetype/msttcorefonts/arial.ttf" trên Linux
# hoặc "C:/Windows/Fonts/arial.ttf" trên Windows.
VIETNAMESE_FONT_PATH = "arial.ttf"  # Đảm bảo font này tồn tại và hỗ trợ tiếng Việt

# Important landmark indices
NOSE_TIP_INDEX = 33
LEFT_EYE_INDICES = list(range(36, 42))
RIGHT_EYE_INDICES = list(range(42, 48))

# Landmark group definitions
LANDMARK_GROUPS = {
    "jaw": list(range(0, 17)),
    "eyebrows": list(range(17, 27)),
    "nose": list(range(27, 36)),
    "left_eye": list(range(36, 42)),
    "right_eye": list(range(42, 48)),
    "mouth_outer": list(range(48, 60)),
    "mouth_inner": list(range(60, 68))
}

# Colors for landmark groups (BGR format for OpenCV)
LANDMARK_COLORS = {
    "jaw": (255, 0, 0),
    "eyebrows": (0, 255, 0),
    "nose": (0, 255, 255),
    "left_eye": (255, 0, 255),
    "right_eye": (255, 128, 0),
    "mouth_outer": (0, 0, 255),
    "mouth_inner": (0, 128, 255)
}

# UI Colors (Light Theme)
REAL_COLOR = "#28a745"
SPOOF_COLOR = "#dc3545"
NEUTRAL_COLOR = "#6c757d"
ACTIVE_COLOR = "#007bff"
BG_COLOR = "#f8f9fa"
PANEL_COLOR = "#e9ecef"
TEXT_COLOR = "#212529"
ACCENT_COLOR = "#495057"


# Hàm tiện ích để vẽ văn bản tiếng Việt lên ảnh (sử dụng PIL)
def draw_text_vietnamese(image_cv, text, position, font_path, font_size, color_bgr, outline_color_bgr=None,
                         outline_thickness=1):
    try:
        # Chuyển đổi màu từ BGR (OpenCV) sang RGB (PIL)
        color_rgb = (color_bgr[2], color_bgr[1], color_bgr[0])

        # Chuyển đổi ảnh OpenCV (BGR) sang ảnh PIL (RGB)
        image_pil = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))

        # Tải font
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"LỖI: Không thể tải font từ '{font_path}'. Sử dụng font mặc định của PIL.")
            font = ImageFont.load_default()  # Fallback to default PIL font

        draw = ImageDraw.Draw(image_pil)

        # Vẽ viền (nếu có)
        if outline_color_bgr:
            outline_color_rgb = (outline_color_bgr[2], outline_color_bgr[1], outline_color_bgr[0])
            x, y = position
            for i in range(-outline_thickness, outline_thickness + 1):
                for j in range(-outline_thickness, outline_thickness + 1):
                    if i == 0 and j == 0:
                        continue
                    draw.text((x + i, y + j), text, font=font, fill=outline_color_rgb)

        # Vẽ văn bản chính
        draw.text(position, text, font=font, fill=color_rgb)

        # Chuyển đổi ảnh PIL (RGB) trở lại ảnh OpenCV (BGR)
        image_cv_out = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        return image_cv_out
    except Exception as e:
        if DEBUG_MODE: print(f"Lỗi khi vẽ văn bản Tiếng Việt: {e}")
        # Nếu lỗi, vẽ bằng cv2.putText với text không dấu để tránh crash
        cv2.putText(image_cv, "Loi font", position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_bgr, 1)
        return image_cv


class FaceDepthAnalyzerGUI:
    def __init__(self):
        self.collected_data = []
        self.is_running = False
        self.selected_label = None
        self.pipeline = None
        self.align = None
        self.app = None
        self.landmark_predictor = None
        self.frame_queue = Queue(maxsize=5)
        self.camera_thread = None
        self.photo_image = None
        self.setup_gui()

    def setup_gui(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("🎭 Hệ Thống Phân Tích Độ Sâu Khuôn Mặt")
        self.root.geometry("1200x800")
        self.root.configure(fg_color=BG_COLOR)
        self.root.resizable(True, True)

        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.setup_left_panel()
        self.setup_right_panel()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_left_panel(self):
        left_frame = ctk.CTkFrame(self.root, fg_color=BG_COLOR, corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        left_frame.grid_rowconfigure(0, weight=4)
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        camera_frame = ctk.CTkFrame(left_frame, fg_color=PANEL_COLOR, corner_radius=10)
        camera_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        camera_frame.grid_rowconfigure(0, weight=1)
        camera_frame.grid_columnconfigure(0, weight=1)

        self.canvas = ctk.CTkCanvas(camera_frame, width=640, height=480,
                                    bg=ACCENT_COLOR,
                                    highlightthickness=1, highlightbackground=NEUTRAL_COLOR)
        self.canvas.grid(row=0, column=0, padx=5, pady=5, sticky="")

        metrics_frame = ctk.CTkFrame(left_frame, fg_color=PANEL_COLOR, corner_radius=10)
        metrics_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.depth_var = ctk.StringVar(value="Độ lệch chuẩn độ sâu: -- mm")
        self.nose_eye_var = ctk.StringVar(value="Chênh lệch Mũi-Mắt: -- mm")

        depth_label = ctk.CTkLabel(metrics_frame, textvariable=self.depth_var,
                                   font=("Arial", 16, "bold"), text_color=TEXT_COLOR)
        depth_label.pack(pady=8, padx=10, fill="x")

        nose_eye_label = ctk.CTkLabel(metrics_frame, textvariable=self.nose_eye_var,
                                      font=("Arial", 16, "bold"), text_color=TEXT_COLOR)
        nose_eye_label.pack(pady=8, padx=10, fill="x")

    def setup_right_panel(self):
        right_frame = ctk.CTkFrame(self.root, fg_color=BG_COLOR, corner_radius=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        status_frame = ctk.CTkFrame(right_frame, fg_color=PANEL_COLOR, corner_radius=10)
        status_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        status_title = ctk.CTkLabel(status_frame, text="📱 Trạng Thái",
                                    font=("Arial", 16, "bold"), text_color=TEXT_COLOR)
        status_title.pack(pady=(10, 5))

        self.status_var = ctk.StringVar(value="Sẵn sàng để bắt đầu")
        status_label = ctk.CTkLabel(status_frame, textvariable=self.status_var,
                                    font=("Arial", 14), text_color=ACCENT_COLOR,
                                    wraplength=220, justify="left")
        status_label.pack(pady=5, padx=10, fill="x")

        label_frame = ctk.CTkFrame(right_frame, fg_color=PANEL_COLOR, corner_radius=10)
        label_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        label_title = ctk.CTkLabel(label_frame, text="🏷️ Chọn Nhãn",
                                   font=("Arial", 16, "bold"), text_color=TEXT_COLOR)
        label_title.pack(pady=(10, 5))

        self.real_btn = ctk.CTkButton(label_frame, text="✅ THẬT",
                                      font=("Arial", 14, "bold"),
                                      fg_color=REAL_COLOR, hover_color="#218838",
                                      width=140, height=45,
                                      command=lambda: self.select_label('real'))
        self.real_btn.pack(pady=8)

        self.spoof_btn = ctk.CTkButton(label_frame, text="❌ GIẢ MẠO",
                                       font=("Arial", 14, "bold"),
                                       fg_color=SPOOF_COLOR, hover_color="#c82333",
                                       width=140, height=45,
                                       command=lambda: self.select_label('spoof'))
        self.spoof_btn.pack(pady=8)

        self.selection_var = ctk.StringVar(value="Chưa chọn")
        selection_label = ctk.CTkLabel(label_frame, textvariable=self.selection_var,
                                       font=("Arial", 17, "bold"), text_color="#FFC107")
        selection_label.pack(pady=5)

        display_frame = ctk.CTkFrame(right_frame, fg_color=PANEL_COLOR, corner_radius=10)
        display_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        display_title = ctk.CTkLabel(display_frame, text="🖼️ Tùy Chọn Hiển Thị",
                                     font=("Arial", 16, "bold"), text_color=TEXT_COLOR)
        display_title.pack(pady=(10, 5))
        self.landmark_var = ctk.BooleanVar(value=True)
        landmark_checkbox = ctk.CTkCheckBox(display_frame, text="Hiển Thị Điểm Mốc",
                                            variable=self.landmark_var,
                                            font=("Arial", 10),
                                            command=self.toggle_landmarks)
        landmark_checkbox.pack(pady=8, padx=10, anchor="w")

        collection_frame = ctk.CTkFrame(right_frame, fg_color=PANEL_COLOR, corner_radius=10)
        collection_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        collection_title = ctk.CTkLabel(collection_frame, text="💾 Thu Thập Dữ Liệu",
                                        font=("Arial", 16, "bold"), text_color=TEXT_COLOR)
        collection_title.pack(pady=(10, 5))

        self.capture_btn = ctk.CTkButton(collection_frame, text="📸 GHI NHẬN",
                                         font=("Arial", 14, "bold"),
                                         fg_color="#28a745", hover_color="#218838",
                                         width=160, height=45,
                                         command=self.capture_sample)
        self.capture_btn.pack(pady=8)

        self.save_btn = ctk.CTkButton(collection_frame, text="💾 LƯU DỮ LIỆU",
                                      font=("Arial", 14, "bold"),
                                      fg_color="#17a2b8", hover_color="#138496",
                                      width=160, height=45,
                                      command=self.save_data)
        self.save_btn.pack(pady=8)

        self.sample_count_var = ctk.StringVar(value="Số mẫu: 0")
        sample_count_label = ctk.CTkLabel(collection_frame, textvariable=self.sample_count_var,
                                          font=("Arial", 12), text_color=ACCENT_COLOR)
        sample_count_label.pack(pady=5)

        control_frame = ctk.CTkFrame(right_frame, fg_color=PANEL_COLOR, corner_radius=10)
        control_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        control_title = ctk.CTkLabel(control_frame, text="⚙️ Điều Khiển Hệ Thống",
                                     font=("Arial", 16, "bold"), text_color=TEXT_COLOR)
        control_title.pack(pady=(10, 5))

        self.start_btn = ctk.CTkButton(control_frame, text="🎥 BẮT ĐẦU CAMERA",
                                       font=("Arial", 14, "bold"),
                                       fg_color="#28a745", hover_color="#218838",
                                       width=180, height=45,
                                       command=self.toggle_camera)
        self.start_btn.pack(pady=8)

        exit_btn = ctk.CTkButton(control_frame, text="🚪 THOÁT ỨNG DỤNG",
                                 font=("Arial", 14, "bold"),
                                 fg_color="#dc3545", hover_color="#c82333",
                                 width=180, height=45,
                                 command=self.on_closing)
        exit_btn.pack(pady=8)

    def toggle_landmarks(self):
        if DEBUG_MODE:
            print(f"Hiển thị điểm mốc đã chuyển: {self.landmark_var.get()}")

    def show_message(self, title_key, message, icon_type="info"):
        title_map = {
            "Error": "Lỗi",
            "Warning": "Cảnh Báo",
            "Info": "Thông Tin"
        }
        display_title = title_map.get(title_key, title_key)

        top = ctk.CTkToplevel(self.root)
        top.geometry("350x180")
        top.title(display_title)
        top.transient(self.root)
        top.grab_set()

        icon_text = ""
        if icon_type == "error":
            icon_text = "❌ "
        elif icon_type == "warning":
            icon_text = "⚠️ "
        elif icon_type == "info":
            icon_text = "ℹ️ "

        label = ctk.CTkLabel(top, text=icon_text + message, font=("Arial", 14), wraplength=300)
        label.pack(pady=20, padx=15, expand=True, fill="both")

        button = ctk.CTkButton(top, text="OK", command=top.destroy, width=100)
        button.pack(pady=15)
        top.update_idletasks()
        root_x, root_y = self.root.winfo_x(), self.root.winfo_y()
        root_width, root_height = self.root.winfo_width(), self.root.winfo_height()
        top_width, top_height = top.winfo_width(), top.winfo_height()
        x = root_x + (root_width - top_width) // 2
        y = root_y + (root_height - top_height) // 2
        top.geometry(f"+{x}+{y}")

    def select_label(self, label_value):
        self.selected_label = label_value
        if label_value == 'real':
            self.real_btn.configure(fg_color="#1e7e34")
            self.spoof_btn.configure(fg_color=SPOOF_COLOR)
            self.selection_var.set("✅ Đã chọn: THẬT")
        else:
            self.spoof_btn.configure(fg_color="#bd2130")
            self.real_btn.configure(fg_color=REAL_COLOR)
            self.selection_var.set("❌ Đã chọn: GIẢ MẠO")

    def toggle_camera(self):
        if not self.is_running:
            self.start_system()
        else:
            self.stop_system()

    def start_system(self):
        self.status_var.set("Đang khởi tạo hệ thống...")
        self.root.update_idletasks()

        if not self.initialize_camera():
            self.show_message("Error", "Không thể khởi tạo camera RealSense. Kiểm tra kết nối và trình điều khiển.",
                              "error")
            self.status_var.set("Lỗi: Camera RealSense thất bại.")
            return
        if not self.initialize_face_detection():
            self.show_message("Error",
                              "Không thể khởi tạo nhận diện khuôn mặt (InsightFace). Kiểm tra tệp mô hình và các thư viện phụ thuộc.",
                              "error")
            self.status_var.set("Lỗi: Nhận diện khuôn mặt thất bại.")
            return
        if not self.initialize_landmarks():
            self.show_message("Error",
                              f"Không thể khởi tạo bộ dự đoán điểm mốc Dlib. Đảm bảo '{DLIB_LANDMARK_MODEL}' tồn tại.",
                              "error")
            self.status_var.set("Lỗi: Dự đoán điểm mốc thất bại.")
            return

        self.is_running = True
        self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
        self.camera_thread.start()
        self.update_display()
        self.start_btn.configure(text="🛑 DỪNG CAMERA", fg_color=SPOOF_COLOR, hover_color="#c82333")
        self.status_var.set("Hệ thống đang chạy - Sẵn sàng ghi nhận")

    def stop_system(self):
        self.is_running = False
        if self.camera_thread and self.camera_thread.is_alive():
            if DEBUG_MODE: print("Đang chờ luồng camera kết thúc...")
            self.camera_thread.join(timeout=2.0)
            if self.camera_thread.is_alive():
                if DEBUG_MODE: print("Luồng camera không kết thúc kịp thời gian.")
        if self.pipeline:
            try:
                self.pipeline.stop()
                if DEBUG_MODE: print("Luồng RealSense đã dừng.")
            except Exception as e:
                if DEBUG_MODE: print(f"Lỗi khi dừng luồng RealSense: {e}")

        self.start_btn.configure(text="🎥 BẮT ĐẦU CAMERA", fg_color="#28a745", hover_color="#218838")
        self.status_var.set("Hệ thống đã dừng")
        self.canvas.delete("all")
        self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2,
                                anchor="center", text="Camera Đã Dừng",
                                fill=TEXT_COLOR, font=("Arial", 16))
        self.depth_var.set("Độ lệch chuẩn độ sâu: -- mm")
        self.nose_eye_var.set("Chênh lệch Mũi-Mắt: -- mm")

    def initialize_camera(self):
        try:
            self.pipeline = rs.pipeline()
            config = rs.config()
            ctx = rs.context()
            if not ctx.query_devices():
                if DEBUG_MODE: print("Không tìm thấy thiết bị RealSense nào.")
                return False
            config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            self.pipeline.start(config)
            self.align = rs.align(rs.stream.color)
            if DEBUG_MODE: print("RealSense đã khởi tạo thành công.")
            return True
        except Exception as e:
            if DEBUG_MODE: print(f"Khởi tạo RealSense thất bại: {traceback.format_exc()}")
            return False

    def initialize_face_detection(self):
        try:
            self.app = FaceAnalysis(allowed_modules=['detection'],
                                    providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            self.app.prepare(ctx_id=0, det_size=(640, 480))
            if DEBUG_MODE: print("InsightFace đã khởi tạo thành công.")
            return True
        except Exception as e:
            if DEBUG_MODE: print(f"Khởi tạo InsightFace thất bại: {traceback.format_exc()}")
            return False

    def initialize_landmarks(self):
        try:
            if not os.path.exists(DLIB_LANDMARK_MODEL):
                raise FileNotFoundError(f"Tệp mô hình điểm mốc Dlib không tìm thấy: {DLIB_LANDMARK_MODEL}")
            self.landmark_predictor = dlib.shape_predictor(DLIB_LANDMARK_MODEL)
            _ = self.landmark_predictor(np.zeros((100, 100, 3), dtype=np.uint8), dlib.rectangle(0, 0, 100, 100))
            if DEBUG_MODE: print("Bộ dự đoán điểm mốc Dlib đã khởi tạo thành công.")
            return True
        except Exception as e:
            if DEBUG_MODE: print(f"Khởi tạo Dlib thất bại: {traceback.format_exc()}")
            return False

    def camera_loop(self):
        font_size_metrics = 15  # Cỡ chữ cho số liệu
        font_size_collected = 20  # Cỡ chữ cho số lượng đã thu thập
        font_size_error = 12  # Cỡ chữ cho lỗi xử lý mặt

        while self.is_running:
            frame_metrics_for_gui = None
            frame_bbox_for_gui = None
            display_image = None
            try:
                frames = self.pipeline.wait_for_frames(timeout_ms=1000)
                if not frames:
                    if DEBUG_MODE: print("Hết thời gian chờ khung hình.")
                    time.sleep(0.05)
                    continue
                aligned_frames = self.align.process(frames)
                depth_frame = aligned_frames.get_depth_frame()
                color_frame = aligned_frames.get_color_frame()
                if not depth_frame or not color_frame:
                    if DEBUG_MODE: print("Thiếu khung hình độ sâu hoặc màu.")
                    continue
                color_image = np.asanyarray(color_frame.get_data())
                display_image = color_image.copy()
                faces = self.app.get(color_image)
                if DEBUG_MODE and faces: print(f"Đã phát hiện {len(faces)} khuôn mặt")

                processed_face_in_frame = False
                for face_idx, face in enumerate(faces):
                    if processed_face_in_frame and face_idx > 0:
                        bbox = face.bbox.astype(int)
                        x1, y1, x2, y2 = bbox
                        cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 100, 255), 1)
                        continue
                    bbox = face.bbox.astype(int)
                    x1, y1, x2, y2 = np.clip(bbox, 0, [639, 479, 639, 479])
                    cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    try:
                        dlib_rect = dlib.rectangle(left=int(x1), top=int(y1), right=int(x2), bottom=int(y2))
                        landmarks = self.landmark_predictor(color_image, dlib_rect)
                        if self.landmark_var.get():
                            landmark_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(68)]
                            for group_name, indices in LANDMARK_GROUPS.items():
                                color = LANDMARK_COLORS.get(group_name, (255, 255, 255))
                                for i in indices:
                                    px, py = landmark_points[i]
                                    cv2.circle(display_image, (px, py), 2, color, -1)
                                if group_name == "jaw":
                                    for k in range(len(indices) - 1):
                                        cv2.line(display_image, landmark_points[indices[k]],
                                                 landmark_points[indices[k + 1]], color, 1)
                        metrics = calculate_depth_metrics(depth_frame, landmarks, face.bbox)
                        if metrics:
                            frame_metrics_for_gui = metrics
                            frame_bbox_for_gui = face.bbox
                            # Sử dụng hàm vẽ tiếng Việt
                            display_image = draw_text_vietnamese(display_image, f"ĐLC: {metrics['face_std_dev']:.1f}",
                                                                 (x1, y2 + 5), VIETNAMESE_FONT_PATH, font_size_metrics,
                                                                 (0, 255, 255))  # Yellow text
                            display_image = draw_text_vietnamese(display_image,
                                                                 f"Mũi-Mắt: {metrics['nose_eye_diff']:.1f}",
                                                                 (x1, y2 + 5 + font_size_metrics + 2),
                                                                 VIETNAMESE_FONT_PATH, font_size_metrics,
                                                                 (0, 255, 255))  # Yellow text
                        processed_face_in_frame = True
                    except Exception as e_face:
                        if DEBUG_MODE: print(f"Lỗi xử lý khuôn mặt (điểm mốc/số liệu): {traceback.format_exc()}")
                        cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 0, 255), 1)
                        # Sử dụng hàm vẽ tiếng Việt
                        display_image = draw_text_vietnamese(display_image, "Lỗi Xử Lý Mặt",
                                                             (x1, y1 - (font_size_error + 2)),
                                                             VIETNAMESE_FONT_PATH, font_size_error,
                                                             (255, 0, 0))  # Red text
                    if processed_face_in_frame: break

                # Sửa lại "Thu thap" thành "Đã thu thập"
                text_to_show = f"Đã thu thập: {len(self.collected_data)}"
                # Vẽ với viền đen và chữ trắng
                display_image = draw_text_vietnamese(display_image, text_to_show, (10, 10), VIETNAMESE_FONT_PATH,
                                                     font_size_collected,
                                                     (255, 255, 255), outline_color_bgr=(0, 0, 0), outline_thickness=1)

                if display_image is not None:
                    if not self.frame_queue.full():
                        self.frame_queue.put(
                            {'image': display_image, 'metrics': frame_metrics_for_gui, 'bbox': frame_bbox_for_gui})
                    elif DEBUG_MODE:
                        print("Hàng đợi khung hình đầy. Bỏ qua khung hình cho GUI.")
            except rs.error as rse:
                if DEBUG_MODE: print(f"Lỗi cụ thể của RealSense trong camera_loop: {rse}")
                time.sleep(0.1)
            except Exception as e:
                if DEBUG_MODE: print(f"Lỗi trong xử lý chính của camera_loop: {traceback.format_exc()}")
                if display_image is None:
                    display_image = np.zeros((480, 640, 3), dtype=np.uint8)
                    # Sử dụng hàm vẽ tiếng Việt
                    display_image = draw_text_vietnamese(display_image, "Lỗi Vòng Lặp Camera", (50, 220),
                                                         VIETNAMESE_FONT_PATH, 20, (255, 0, 0))  # Red text
                if not self.frame_queue.full(): self.frame_queue.put(
                    {'image': display_image, 'metrics': None, 'bbox': None})
            if not self.is_running: break
            time.sleep(0.01)
        if DEBUG_MODE: print("Vòng lặp camera đã kết thúc.")

    def update_display(self):
        if not self.is_running and self.frame_queue.empty(): return
        try:
            if not self.frame_queue.empty():
                frame_data = self.frame_queue.get_nowait()
                image = frame_data['image']
                canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
                img_height, img_width, _ = image.shape
                scale = min(canvas_width / img_width, canvas_height / img_height)
                new_width, new_height = int(img_width * scale), int(img_height * scale)
                resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
                image_pil = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
                self.photo_image = ImageTk.PhotoImage(image_pil)
                self.canvas.delete("all")
                x_offset, y_offset = (canvas_width - new_width) // 2, (canvas_height - new_height) // 2
                self.canvas.create_image(x_offset, y_offset, anchor="nw", image=self.photo_image)
                gui_metrics = frame_data['metrics']
                if gui_metrics:
                    self.depth_var.set(f"Độ lệch chuẩn độ sâu: {gui_metrics['face_std_dev']:.1f} mm")
                    self.nose_eye_var.set(f"Chênh lệch Mũi-Mắt: {gui_metrics['nose_eye_diff']:.1f} mm")
                else:
                    self.depth_var.set("Độ lệch chuẩn độ sâu: -- mm")
                    self.nose_eye_var.set("Chênh lệch Mũi-Mắt: -- mm")
        except Queue.Empty:
            pass
        except Exception as e:
            if DEBUG_MODE: print(f"Lỗi cập nhật hiển thị: {traceback.format_exc()}")
        if self.is_running or not self.frame_queue.empty():
            self.root.after(15, self.update_display)

    def capture_sample(self):
        if self.frame_queue.empty():
            self.show_message("Warning", "Không có dữ liệu khung hình để ghi nhận.", "warning")
            return
        if not self.selected_label:
            self.show_message("Warning", "Vui lòng chọn nhãn THẬT hoặc GIẢ MẠO trước!", "warning")
            return
        try:
            frame_data_for_capture = self.frame_queue.get(timeout=0.1)
            metrics_to_capture = frame_data_for_capture.get('metrics')
            if metrics_to_capture:
                capture_data = metrics_to_capture.copy()
                capture_data['label'] = self.selected_label
                self.collected_data.append(capture_data)
                self.sample_count_var.set(f"Số mẫu: {len(self.collected_data)}")
                display_label_vietnamese = "THẬT" if self.selected_label == 'real' else "GIẢ MẠO"
                self.status_var.set(f"✅ Đã ghi mẫu #{len(self.collected_data)} là {display_label_vietnamese}")
                self.selected_label = None
                self.real_btn.configure(fg_color=REAL_COLOR)
                self.spoof_btn.configure(fg_color=SPOOF_COLOR)
                self.selection_var.set("Chưa chọn")
            else:
                self.show_message("Warning",
                                  "Không phát hiện số liệu khuôn mặt hợp lệ trong khung hình hiện tại để ghi nhận.",
                                  "warning")
        except Queue.Empty:
            self.show_message("Warning", "Không có dữ liệu khung hình mới để ghi nhận. Thử lại.", "warning")
        except Exception as e:
            self.show_message("Error", f"Lỗi trong quá trình ghi nhận: {e}", "error")
            if DEBUG_MODE: print(f"Lỗi ghi nhận: {traceback.format_exc()}")

    def save_data(self):
        if not self.collected_data:
            self.show_message("Warning", "Không có dữ liệu để lưu!", "warning")
            return
        try:
            df = pd.DataFrame(self.collected_data)
            if DEBUG_MODE:
                print(f"\nĐã thu thập {len(df)} mẫu:")
                print(df.groupby('label').size())
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            file_path = ctk.filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"depth_data_{timestamp}.csv",
                title="Lưu Dữ Liệu Đã Thu Thập"
            )
            if not file_path:
                self.status_var.set("Hủy lưu.")
                return
            df.to_csv(file_path, index=False)
            if DEBUG_MODE: print(f"Dữ liệu đã được lưu vào {file_path}")
            self.status_var.set(f"💾 Đã lưu dữ liệu: {os.path.basename(file_path)}")
            self.plot_results(df)
        except Exception as e:
            self.show_message("Error", f"Lưu dữ liệu thất bại: {traceback.format_exc()}", "error")

    def plot_results(self, df):
        if df.empty or not all(col in df.columns for col in ['nose_eye_diff', 'face_std_dev', 'label']):
            self.show_message("Warning", "Không đủ dữ liệu hoặc thiếu cột để vẽ biểu đồ!", "warning")
            return
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Phân Tích Số Liệu Độ Sâu Khuôn Mặt', fontsize=16)
            sns.histplot(data=df, x='nose_eye_diff', hue='label', kde=True,
                         palette={'real': REAL_COLOR, 'spoof': SPOOF_COLOR}, ax=axes[0, 0])
            axes[0, 0].set_title('Chênh Lệch Độ Sâu Mũi-Mắt (mm)')
            axes[0, 0].set_xlabel('Chênh lệch (mm)')
            axes[0, 0].set_ylabel('Tần suất')
            sns.histplot(data=df, x='face_std_dev', hue='label', kde=True,
                         palette={'real': REAL_COLOR, 'spoof': SPOOF_COLOR}, ax=axes[0, 1])
            axes[0, 1].set_title('Độ Lệch Chuẩn Độ Sâu Khuôn Mặt (mm)')
            axes[0, 1].set_xlabel('Độ lệch chuẩn (mm)')
            axes[0, 1].set_ylabel('Tần suất')
            sns.scatterplot(data=df, x='nose_eye_diff', y='face_std_dev', hue='label',
                            palette={'real': REAL_COLOR, 'spoof': SPOOF_COLOR}, alpha=0.7, ax=axes[1, 0])
            axes[1, 0].set_title('Mối Quan Hệ Số Liệu Độ Sâu')
            axes[1, 0].set_xlabel('Chênh lệch Mũi-Mắt (mm)')
            axes[1, 0].set_ylabel('Độ Lệch Chuẩn Độ Sâu Mặt (mm)')
            if not df.empty:
                plot_data = pd.melt(df, id_vars=['label'], value_vars=['nose_eye_diff', 'face_std_dev'],
                                    var_name='Metric', value_name='Value')
                sns.boxplot(data=plot_data, x='Metric', y='Value', hue='label',
                            palette={'real': '#a2d5ab', 'spoof': '#f8b195'}, ax=axes[1, 1])
                axes[1, 1].set_title('So Sánh Số Liệu (Biểu Đồ Hộp)')
                axes[1, 1].set_ylabel('Giá trị (mm)')
            else:
                axes[1, 1].text(0.5, 0.5, "Không có dữ liệu cho biểu đồ hộp", ha='center', va='center')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.show()
        except Exception as e:
            self.show_message("Error", f"Vẽ biểu đồ thất bại: {e}", "error")
            if DEBUG_MODE: print(f"Lỗi vẽ biểu đồ: {traceback.format_exc()}")

    def on_closing(self):
        if DEBUG_MODE: print("Đang đóng ứng dụng...")
        if self.is_running: self.stop_system()
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except Queue.Empty:
                break
        self.root.quit()
        self.root.destroy()
        if DEBUG_MODE: print("Ứng dụng đã đóng.")

    def run(self):
        print("🎭 Hệ Thống Phân Tích Độ Sâu Khuôn Mặt - Phiên Bản GUI")
        print("Nhấn 'BẮT ĐẦU CAMERA' để bắt đầu")
        self.root.mainloop()


def calculate_depth_metrics(depth_frame_rs, landmarks_dlib, face_bbox_insight):
    try:
        depth_image_np = np.asanyarray(depth_frame_rs.get_data())
        h, w = depth_image_np.shape
        if DEBUG_MODE and np.all(depth_image_np == 0):
            print("Cảnh báo: Tất cả giá trị độ sâu trong depth_image_np đều bằng không.")
        landmark_points_list = []
        for i in range(68):
            pt = landmarks_dlib.part(i)
            landmark_points_list.append((pt.x, pt.y))
        landmark_depths_mm = []
        valid_landmark_indices = []
        for idx, (x, y) in enumerate(landmark_points_list):
            if 0 <= x < w and 0 <= y < h:
                depth_value_mm = depth_frame_rs.get_distance(x, y) * 1000.0
                if depth_value_mm > 0:
                    landmark_depths_mm.append(depth_value_mm)
                    valid_landmark_indices.append(idx)
                else:
                    landmark_depths_mm.append(0)
            else:
                landmark_depths_mm.append(0)
        actual_nose_tip_idx = 30
        nose_depth_mm = 0
        if actual_nose_tip_idx in valid_landmark_indices:
            nose_depth_mm = landmark_depths_mm[valid_landmark_indices.index(actual_nose_tip_idx)]

        left_eye_depth_values_mm = [landmark_depths_mm[valid_landmark_indices.index(i)] for i in LEFT_EYE_INDICES if
                                    i in valid_landmark_indices and landmark_depths_mm[
                                        valid_landmark_indices.index(i)] > 0]
        right_eye_depth_values_mm = [landmark_depths_mm[valid_landmark_indices.index(i)] for i in RIGHT_EYE_INDICES if
                                     i in valid_landmark_indices and landmark_depths_mm[
                                         valid_landmark_indices.index(i)] > 0]

        mean_left_eye_depth_mm = np.mean(left_eye_depth_values_mm) if left_eye_depth_values_mm else 0
        mean_right_eye_depth_mm = np.mean(right_eye_depth_values_mm) if right_eye_depth_values_mm else 0
        avg_eye_depth_mm = 0
        if mean_left_eye_depth_mm > 0 and mean_right_eye_depth_mm > 0:
            avg_eye_depth_mm = (mean_left_eye_depth_mm + mean_right_eye_depth_mm) / 2.0
        elif mean_left_eye_depth_mm > 0:
            avg_eye_depth_mm = mean_left_eye_depth_mm
        elif mean_right_eye_depth_mm > 0:
            avg_eye_depth_mm = mean_right_eye_depth_mm

        x1, y1, x2, y2 = face_bbox_insight.astype(int)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w - 1, x2), min(h - 1, y2)
        face_std_dev_mm = 0
        if x1 < x2 and y1 < y2:
            face_region_depth_values = []
            for r_idx in range(y1, y2 + 1):
                for c_idx in range(x1, x2 + 1):
                    d = depth_frame_rs.get_distance(c_idx, r_idx) * 1000.0
                    if d > 0: face_region_depth_values.append(d)
            if len(face_region_depth_values) > 10:
                face_std_dev_mm = np.std(face_region_depth_values)
        nose_eye_diff_mm = 0
        if avg_eye_depth_mm > 0 and nose_depth_mm > 0:
            nose_eye_diff_mm = avg_eye_depth_mm - nose_depth_mm
        if nose_depth_mm > 0 and avg_eye_depth_mm > 0 and face_std_dev_mm > 0:
            return {'nose_depth': nose_depth_mm, 'avg_eye_depth': avg_eye_depth_mm, 'face_std_dev': face_std_dev_mm,
                    'nose_eye_diff': nose_eye_diff_mm}
        if DEBUG_MODE:
            print(
                f"Tính toán số liệu: ĐộSâuMũi={nose_depth_mm:.1f}, ĐộSâuMắt={avg_eye_depth_mm:.1f}, ĐộLệchChuẩn={face_std_dev_mm:.1f}, ChênhLệch={nose_eye_diff_mm:.1f} -> Không phải tất cả đều hợp lệ.")
        return None
    except Exception as e:
        if DEBUG_MODE: print(f"Lỗi trong calculate_depth_metrics: {traceback.format_exc()}")
        return None


if __name__ == "__main__":
    if not os.path.exists(DLIB_LANDMARK_MODEL):
        print(f"LỖI: Không tìm thấy mô hình điểm mốc Dlib '{DLIB_LANDMARK_MODEL}'.")
        print("Vui lòng tải về từ http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
        print("Và giải nén vào cùng thư mục với tập lệnh, hoặc cung cấp đường dẫn chính xác.")
    else:
        # Kiểm tra xem font có tồn tại không (bước tùy chọn, nhưng hữu ích)
        if not os.path.exists(VIETNAMESE_FONT_PATH):
            print(f"CẢNH BÁO: Không tìm thấy file font '{VIETNAMESE_FONT_PATH}'.")
            print("Văn bản tiếng Việt trên video có thể không hiển thị đúng.")
            print("Vui lòng cài đặt một font .ttf hỗ trợ tiếng Việt và cập nhật biến VIETNAMESE_FONT_PATH.")
        app_gui = FaceDepthAnalyzerGUI()
        app_gui.run()
