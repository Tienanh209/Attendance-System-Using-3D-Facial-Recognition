import pyrealsense2 as rs
import numpy as np
import cv2
import dlib

# Khởi tạo camera RealSense
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Khởi tạo dlib detector và predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')  # cần tải file này

def get_landmarks(img, gray):
    faces = detector(gray)
    if len(faces) == 0: return None
    shape = predictor(gray, faces[0])
    coords = np.array([[p.x, p.y] for p in shape.parts()])
    return coords

try:
    while True:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        landmarks = get_landmarks(color_image, gray)
        if landmarks is not None:
            # 1. Chỉ số nose_eye_diff (mũi - mắt)
            nose_z = depth_frame.get_distance(*landmarks[30])  # Mũi
            left_eye_z = depth_frame.get_distance(*landmarks[36])  # Mắt trái
            right_eye_z = depth_frame.get_distance(*landmarks[45])  # Mắt phải
            eye_z = (left_eye_z + right_eye_z) / 2
            nose_eye_diff = eye_z - nose_z

            # 2. Độ lệch chuẩn vùng mặt
            face_points = landmarks[0:68]
            face_depths = []
            for (x, y) in face_points:
                d = depth_frame.get_distance(x, y)
                if d > 0:
                    face_depths.append(d)
            face_std_dev = np.std(face_depths)

            # Hiển thị thông số
            cv2.putText(color_image, f'nose_eye_diff: {nose_eye_diff:.3f} m', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            cv2.putText(color_image, f'face_std_dev: {face_std_dev:.3f} m', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

            # Vẽ landmark
            for (x, y) in landmarks:
                cv2.circle(color_image, (x, y), 2, (255, 0, 0), -1)

        cv2.imshow('Depth Face Detection', color_image)
        if cv2.waitKey(1) == 27:
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
