import pyrealsense2 as rs
import numpy as np
import dlib
import cv2
import csv
import os
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from PIL import Image, ImageTk
import threading
import time
import json


class Face3DAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Face Analysis")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")

        # Khởi tạo biến
        self.person_id = ""
        self.session_id = time.strftime("%Y%m%d_%H%M%S")
        self.frame_number = 0
        self.landmark_3d = None
        self.current_image = None
        self.display_image = None
        self.running = False
        self.show_landmarks = tk.BooleanVar(value=True)
        self.continuous_capture = tk.BooleanVar(value=False)
        self.capture_interval = tk.IntVar(value=3)  # seconds
        self.last_capture_time = 0

        # Tạo thư mục lưu trữ
        self.base_folder = "FileObject3D"
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)

        # Tạo layout
        self.create_layout()

        # Khởi tạo Intel RealSense
        try:
            self.pipeline = rs.pipeline()
            self.config = rs.config()
            self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
            self.align = rs.align(rs.stream.color)
            self.pipeline.start(self.config)
            self.status_label.config(text="Status: Camera initialized")
        except Exception as e:
            self.status_label.config(text=f"Error initializing camera: {e}")
            messagebox.showerror("Camera Error", f"Failed to initialize RealSense camera: {e}")

        # Khởi tạo Dlib
        try:
            self.face_detector = dlib.get_frontal_face_detector()
            model_path = "../../manage_attendance/shape_predictor_68_face_landmarks.dat"
            if not os.path.exists(model_path):
                self.status_label.config(text="Error: Missing shape_predictor_68_face_landmarks.dat")
                messagebox.showerror("Error",
                                     "Missing face landmark model file.\nPlease download shape_predictor_68_face_landmarks.dat")
            else:
                self.landmark_predictor = dlib.shape_predictor(model_path)
                self.status_label.config(text="Status: Dlib initialized")
        except Exception as e:
            self.status_label.config(text=f"Error initializing Dlib: {e}")
            messagebox.showerror("Dlib Error", f"Failed to initialize face detector: {e}")

        # Landmark group definitions
        self.landmark_groups = {
            "jaw": list(range(0, 17)),
            "eyebrows": list(range(17, 27)),
            "nose": list(range(27, 36)),
            "left_eye": list(range(36, 42)),
            "right_eye": list(range(42, 48)),
            "mouth_outer": list(range(48, 60)),
            "mouth_inner": list(range(60, 68))
        }

        # Khởi tạo InsightFace (nếu cần)
        try:
            from insightface.app import FaceAnalysis
            self.app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            self.use_insightface = True
        except:
            self.use_insightface = False
            print("InsightFace not available, skipping...")

        # Bắt đầu cập nhật video
        self.update_video()

    def create_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Camera feed
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Camera canvas with border
        canvas_frame = ttk.LabelFrame(left_frame, text="Camera Feed")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, width=640, height=480, bg="black")
        self.canvas.pack(padx=5, pady=5)

        # Status bar
        status_frame = ttk.Frame(left_frame)
        status_frame.pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(status_frame, text="Status: Initializing...", font=("Arial", 10))
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.landmarks_count_label = ttk.Label(status_frame, text="Landmarks: 0/68", font=("Arial", 10))
        self.landmarks_count_label.pack(side=tk.RIGHT, padx=5)

        # Right panel - Controls
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        # Person ID section
        id_frame = ttk.LabelFrame(right_frame, text="Person Identification")
        id_frame.pack(fill=tk.X, pady=5)

        ttk.Label(id_frame, text="Person ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.id_entry = ttk.Entry(id_frame, width=15)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(id_frame, text="Set ID", command=self.set_person_id).grid(row=0, column=2, padx=5, pady=5)

        self.id_label = ttk.Label(id_frame, text="Current ID: None")
        self.id_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        # Capture options
        options_frame = ttk.LabelFrame(right_frame, text="Capture Options")
        options_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(options_frame, text="Show Landmarks", variable=self.show_landmarks).pack(anchor="w", padx=5,
                                                                                                 pady=2)

        continuous_frame = ttk.Frame(options_frame)
        continuous_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Checkbutton(continuous_frame, text="Continuous Capture", variable=self.continuous_capture).pack(
            side=tk.LEFT)

        interval_frame = ttk.Frame(options_frame)
        interval_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(interval_frame, text="Interval (sec):").pack(side=tk.LEFT)
        interval_spin = ttk.Spinbox(interval_frame, from_=1, to=10, textvariable=self.capture_interval, width=5)
        interval_spin.pack(side=tk.LEFT, padx=5)

        # Capture buttons
        capture_frame = ttk.LabelFrame(right_frame, text="Data Collection")
        capture_frame.pack(fill=tk.X, pady=5)

        ttk.Button(capture_frame, text="Single Capture", command=self.start_capture, style="Accent.TButton").pack(
            fill=tk.X, padx=5, pady=5)
        ttk.Button(capture_frame, text="Start Continuous ( every " + str(self.capture_interval.get()) + " sec)", command=self.start_continuous_capture).pack(fill=tk.X,
                                                                                                       padx=5, pady=5)
        ttk.Button(capture_frame, text="Stop Continuous", command=self.stop_continuous_capture).pack(fill=tk.X, padx=5,
                                                                                                     pady=5)

        # Info panel
        info_frame = ttk.LabelFrame(right_frame, text="Information")
        info_frame.pack(fill=tk.X, pady=5)

        self.info_text = tk.Text(info_frame, height=8, width=30, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, padx=5, pady=5)
        self.info_text.insert(tk.END, "Welcome to 3D Face Analysis\n\n")
        self.info_text.insert(tk.END, "1. Set Person ID\n")
        self.info_text.insert(tk.END, "2. Select capture mode\n")
        self.info_text.insert(tk.END, "3. Data will be saved to FileObject3D folder\n")
        self.info_text.config(state=tk.DISABLED)

        # Exit button
        ttk.Button(right_frame, text="Exit Application", command=self.exit_app).pack(fill=tk.X, pady=10)

        # Apply styles
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))

    def set_person_id(self):
        new_id = self.id_entry.get().strip()
        if not new_id:
            new_id = simpledialog.askstring("Person ID", "Enter Person ID:", parent=self.root)

        if new_id:
            self.person_id = new_id
            self.id_label.config(text=f"Current ID: {self.person_id}")

            # Create person folder
            person_folder = os.path.join(self.base_folder, self.person_id)
            if not os.path.exists(person_folder):
                os.makedirs(person_folder)

            self.update_info(f"Set ID: {self.person_id}")
            self.status_label.config(text=f"Status: Ready to capture for {self.person_id}")
        else:
            messagebox.showwarning("Missing ID", "Please enter a Person ID")

    def collect_data(self):
        try:
            # Get frames from RealSense
            frames = self.pipeline.wait_for_frames()
            aligned_frames = self.align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            if not color_frame or not depth_frame:
                self.status_label.config(text="Status: No color/depth frame")
                return None, None

            # Convert to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())

            # Create a copy for visualization
            display_image = color_image.copy()

            # Detect faces using dlib
            gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector(gray_image)

            if not faces:
                self.status_label.config(text="Status: No faces detected")
                self.landmarks_count_label.config(text="Landmarks: 0/68")
                return None, display_image

            # Process the first detected face
            face = faces[0]

            # Draw face rectangle
            cv2.rectangle(display_image,
                          (face.left(), face.top()),
                          (face.right(), face.bottom()),
                          (0, 255, 0), 2)

            # Get facial landmarks
            landmarks = self.landmark_predictor(gray_image, face)
            landmark_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)]

            # Draw landmarks on display image if enabled
            if self.show_landmarks.get():
                # Draw different landmark groups with different colors
                colors = {
                    "jaw": (255, 0, 0),  # Blue
                    "eyebrows": (0, 255, 0),  # Green
                    "nose": (0, 255, 255),  # Yellow
                    "left_eye": (255, 0, 255),  # Magenta
                    "right_eye": (255, 128, 0),  # Orange
                    "mouth_outer": (0, 0, 255),  # Red
                    "mouth_inner": (0, 128, 255)  # Light red
                }

                # Draw landmark points by group
                for group_name, indices in self.landmark_groups.items():
                    color = colors.get(group_name, (255, 255, 255))
                    for i in indices:
                        cv2.circle(display_image, (landmark_points[i][0], landmark_points[i][1]),
                                   3, color, -1)

                # Connect landmarks with lines for better visualization
                # Jaw line
                for i in range(1, 17):
                    cv2.line(display_image,
                             (landmark_points[i - 1][0], landmark_points[i - 1][1]),
                             (landmark_points[i][0], landmark_points[i][1]),
                             (255, 0, 0), 1)

                # Left eyebrow
                for i in range(18, 22):
                    cv2.line(display_image,
                             (landmark_points[i - 1][0], landmark_points[i - 1][1]),
                             (landmark_points[i][0], landmark_points[i][1]),
                             (0, 255, 0), 1)

                # Right eyebrow
                for i in range(23, 27):
                    cv2.line(display_image,
                             (landmark_points[i - 1][0], landmark_points[i - 1][1]),
                             (landmark_points[i][0], landmark_points[i][1]),
                             (0, 255, 0), 1)

                # Nose bridge
                for i in range(28, 31):
                    cv2.line(display_image,
                             (landmark_points[i - 1][0], landmark_points[i - 1][1]),
                             (landmark_points[i][0], landmark_points[i][1]),
                             (0, 255, 255), 1)

                # Nose base
                cv2.line(display_image,
                         (landmark_points[30][0], landmark_points[30][1]),
                         (landmark_points[31][0], landmark_points[31][1]),
                         (0, 255, 255), 1)
                cv2.line(display_image,
                         (landmark_points[31][0], landmark_points[31][1]),
                         (landmark_points[32][0], landmark_points[32][1]),
                         (0, 255, 255), 1)
                cv2.line(display_image,
                         (landmark_points[32][0], landmark_points[32][1]),
                         (landmark_points[33][0], landmark_points[33][1]),
                         (0, 255, 255), 1)
                cv2.line(display_image,
                         (landmark_points[33][0], landmark_points[33][1]),
                         (landmark_points[34][0], landmark_points[34][1]),
                         (0, 255, 255), 1)
                cv2.line(display_image,
                         (landmark_points[34][0], landmark_points[34][1]),
                         (landmark_points[35][0], landmark_points[35][1]),
                         (0, 255, 255), 1)

                # Left eye
                for i in range(37, 42):
                    cv2.line(display_image,
                             (landmark_points[i - 1][0], landmark_points[i - 1][1]),
                             (landmark_points[i][0], landmark_points[i][1]),
                             (255, 0, 255), 1)
                cv2.line(display_image,
                         (landmark_points[41][0], landmark_points[41][1]),
                         (landmark_points[36][0], landmark_points[36][1]),
                         (255, 0, 255), 1)

                # Right eye
                for i in range(43, 48):
                    cv2.line(display_image,
                             (landmark_points[i - 1][0], landmark_points[i - 1][1]),
                             (landmark_points[i][0], landmark_points[i][1]),
                             (255, 128, 0), 1)
                cv2.line(display_image,
                         (landmark_points[47][0], landmark_points[47][1]),
                         (landmark_points[42][0], landmark_points[42][1]),
                         (255, 128, 0), 1)

                # Outer lip
                for i in range(49, 60):
                    cv2.line(display_image,
                             (landmark_points[i - 1][0], landmark_points[i - 1][1]),
                             (landmark_points[i][0], landmark_points[i][1]),
                             (0, 0, 255), 1)
                cv2.line(display_image,
                         (landmark_points[59][0], landmark_points[59][1]),
                         (landmark_points[48][0], landmark_points[48][1]),
                         (0, 0, 255), 1)

                # Inner lip
                for i in range(61, 68):
                    cv2.line(display_image,
                             (landmark_points[i - 1][0], landmark_points[i - 1][1]),
                             (landmark_points[i][0], landmark_points[i][1]),
                             (0, 128, 255), 1)
                cv2.line(display_image,
                         (landmark_points[67][0], landmark_points[67][1]),
                         (landmark_points[60][0], landmark_points[60][1]),
                         (0, 128, 255), 1)

            # Get depth information and convert to 3D coordinates
            depth_scale = self.pipeline.get_active_profile().get_device().first_depth_sensor().get_depth_scale()
            intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics

            # Collect 3D landmark points
            landmark_3d = []
            valid_points = 0

            for x, y in landmark_points:
                if 0 <= y < depth_image.shape[0] and 0 <= x < depth_image.shape[1]:
                    # Get depth value
                    z = depth_image[y, x]

                    # Check if depth is valid
                    if z == 0 or z > 10000:  # Invalid depth
                        # Look for valid depth in surrounding area
                        z_values = []
                        for dy in range(-3, 4):
                            for dx in range(-3, 4):
                                nx, ny = x + dx, y + dy
                                if 0 <= ny < depth_image.shape[0] and 0 <= nx < depth_image.shape[1]:
                                    nz = depth_image[ny, nx]
                                    if nz > 0 and nz < 10000:
                                        z_values.append(nz)

                        # Use median of valid neighbors
                        if z_values:
                            z = np.median(z_values)
                        else:
                            landmark_3d.append([0, 0, 0])
                            continue

                    # Convert to meters and deproject to 3D point
                    z_meters = z * depth_scale
                    point_3d = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], z)

                    # Validate 3D point
                    if not np.isnan(point_3d).any() and not np.isinf(point_3d).any():
                        landmark_3d.append(point_3d)
                        valid_points += 1
                    else:
                        landmark_3d.append([0, 0, 0])
                else:
                    landmark_3d.append([0, 0, 0])

            # Update landmarks count label
            self.landmarks_count_label.config(text=f"Landmarks: {valid_points}/68")

            # Add processing with InsightFace if available
            face_embedding = None
            if self.use_insightface:
                face_crop = color_image[face.top():face.bottom(), face.left():face.right()]
                if face_crop.size > 0:  # Ensure face crop is not empty
                    faces_insight = self.app.get(face_crop)
                    if faces_insight:
                        face_embedding = faces_insight[0].embedding

            return landmark_3d, display_image

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_label.config(text=f"Error: {str(e)[:50]}")
            return None, None

    def start_capture(self):
        """Capture a single frame of 3D landmarks"""
        if not self.person_id:
            messagebox.showwarning("Missing ID", "Please set a Person ID first")
            return

        self.status_label.config(text="Status: Capturing...")
        self.root.update()

        # Get landmarks and update display
        self.landmark_3d, self.display_image = self.collect_data()

        if self.landmark_3d:
            # Save the data
            self.save_data()
            self.status_label.config(text=f"Status: Data captured for {self.person_id}")
        else:
            self.status_label.config(text="Status: Failed to capture data")

    def start_continuous_capture(self):
        """Start continuous capture mode"""
        if not self.person_id:
            messagebox.showwarning("Missing ID", "Please set a Person ID first")
            return

        self.continuous_capture.set(True)
        self.update_info("Starting continuous capture")
        self.status_label.config(text=f"Status: Continuous capture for {self.person_id}")

    def stop_continuous_capture(self):
        """Stop continuous capture mode"""
        self.continuous_capture.set(False)
        self.update_info("Stopped continuous capture")
        self.status_label.config(text="Status: Continuous capture stopped")

    def save_data(self):
        """Save the captured 3D landmarks to files"""
        if self.landmark_3d is None or len(self.landmark_3d) == 0:
            return False

        try:
            # Create folder structure
            person_folder = os.path.join(self.base_folder, self.person_id)
            if not os.path.exists(person_folder):
                os.makedirs(person_folder)

            session_folder = os.path.join(person_folder, self.session_id)
            if not os.path.exists(session_folder):
                os.makedirs(session_folder)

            # Save OBJ file
            timestamp = time.strftime("%H%M%S")
            obj_file = os.path.join(session_folder, f"{self.person_id}_{self.frame_number}_{timestamp}.obj")

            with open(obj_file, 'w') as f:
                f.write('# 3D Face Landmarks\n')
                for x_3d, y_3d, z_3d in self.landmark_3d:
                    f.write(f'v {x_3d} {y_3d} {z_3d}\n')

            # Save metadata JSON
            meta_file = os.path.join(session_folder, f"{self.person_id}_{self.frame_number}_{timestamp}.json")

            metadata = {
                "person_id": self.person_id,
                "frame_number": self.frame_number,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "valid_landmarks": sum(1 for p in self.landmark_3d if not (p[0] == 0 and p[1] == 0 and p[2] == 0)),
                "total_landmarks": len(self.landmark_3d)
            }

            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Increment frame counter
            self.frame_number += 1

            # Log info
            self.update_info(f"Saved: Frame {self.frame_number - 1}")
            return True

        except Exception as e:
            self.status_label.config(text=f"Error saving data: {str(e)[:50]}")
            return False

    def update_info(self, message):
        """Update the info text box"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)

    def update_video(self):
        """Update the video feed and process continuous capture"""
        try:
            # Process continuous capture if enabled
            if self.continuous_capture.get() and self.person_id:
                current_time = time.time()
                if current_time - self.last_capture_time >= self.capture_interval.get():
                    self.landmark_3d, self.display_image = self.collect_data()
                    if self.landmark_3d:
                        if self.save_data():
                            self.last_capture_time = current_time

            # Regular video update
            landmark_3d, display_image = self.collect_data()

            if display_image is not None:
                # Convert to RGB for PIL
                img_rgb = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
                img_pil = img_pil.resize((640, 480), Image.LANCZOS)

                # Convert to PhotoImage
                self.photo = ImageTk.PhotoImage(img_pil)

                # Update canvas
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        except Exception as e:
            self.status_label.config(text=f"Video update error: {str(e)[:50]}")

        # Schedule next update
        self.root.after(30, self.update_video)  # ~30 FPS

    def exit_app(self):
        """Safely exit the application"""
        try:
            self.pipeline.stop()
        except:
            pass
        self.root.quit()
        self.root.destroy()


if __name__ == "__main__":
    # Apply a nicer theme if available
    try:
        import ttkthemes

        root = ttkthemes.ThemedTk(theme="arc")
    except:
        root = tk.Tk()

    app = Face3DAnalysisApp(root)
    root.mainloop()