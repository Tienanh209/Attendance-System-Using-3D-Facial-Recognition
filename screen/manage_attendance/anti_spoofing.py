import pyrealsense2 as rs
import dlib
import numpy as np
import cv2

class FaceAntiSpoofing:
    def __init__(self):
        # Thiết lập camera RealSense
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.profile = self.pipeline.start(config)
        self.align = rs.align(rs.stream.color)  # Căn chỉnh với stream color

        # Tải mô hình dlib
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        # Định nghĩa chỉ số điểm mốc
        self.nose_tip_index = 33
        self.left_eye_indices = list(range(36, 42))
        self.right_eye_indices = list(range(42, 48))
        self.jaw_indices = list(range(0, 17))

        # Tham số
        self.tolerance = 20  # Dung sai cho so sánh chiều sâu (mm)
        self.std_dev_threshold = 15  # Ngưỡng độ lệch chuẩn cho vùng khuôn mặt

    def process_frame(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not color_frame or not depth_frame:
            return None

        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        return color_image, depth_image

    def detect_faces(self, color_image, depth_image):
        faces = self.face_detector(color_image)
        results = []

        for face in faces:
            # Lấy điểm mốc
            landmarks = self.landmark_predictor(color_image, face)

            # Trích xuất tọa độ điểm mốc
            landmark_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(68)]

            # Lấy giá trị chiều sâu cho các điểm mốc
            landmark_depths = []
            for x, y in landmark_points:
                if 0 <= x < depth_image.shape[1] and 0 <= y < depth_image.shape[0]:
                    depth = depth_image[y, x]
                    landmark_depths.append(depth)
                else:
                    landmark_depths.append(0)  # Giá trị không hợp lệ

            # Kiểm tra dữ liệu chiều sâu thô
            valid_depths = [d for d in landmark_depths if d > 0]
            if len(valid_depths) < 0.5 * len(landmark_depths):  # Nếu dưới 50% điểm hợp lệ
                print("Dữ liệu chiều sâu không hợp lệ")
                continue

            # Tính toán các giá trị chiều sâu
            nose_depth = landmark_depths[self.nose_tip_index]
            mean_left_eye_depth = np.mean([landmark_depths[i] for i in self.left_eye_indices if landmark_depths[i] > 0])
            mean_right_eye_depth = np.mean([landmark_depths[i] for i in self.right_eye_indices if landmark_depths[i] > 0])
            mean_jaw_depth = np.mean([landmark_depths[i] for i in self.jaw_indices if landmark_depths[i] > 0])

            # Tính độ lệch chuẩn của vùng khuôn mặt
            face_region_depth = depth_image[face.top():face.bottom(), face.left():face.right()]
            std_dev = np.std(face_region_depth)

            # Kiểm tra cấu trúc chiều sâu (mũi gần hơn trung bình mắt)
            avg_eye_depth = (mean_left_eye_depth + mean_right_eye_depth) / 2 if (mean_left_eye_depth and mean_right_eye_depth) else 0
            is_nose_closer = nose_depth < avg_eye_depth - self.tolerance

            # Quyết định dựa trên độ lệch chuẩn và cấu trúc
            is_real = std_dev > self.std_dev_threshold and is_nose_closer

            results.append({
                'face': face,  # dlib rectangle
                'is_real': is_real,
                'nose_depth': nose_depth,
                'mean_left_eye_depth': mean_left_eye_depth,
                'mean_right_eye_depth': mean_right_eye_depth,
                'mean_jaw_depth': mean_jaw_depth,
                'std_dev': std_dev
            })

        return results

    def draw_results(self, color_image, results):
        for result in results:
            face = result['face']
            is_real = result['is_real']
            color = (0, 255, 0) if is_real else (0, 0, 255)
            label = "Real" if is_real else "Fake"
            cv2.rectangle(color_image, (face.left(), face.top()), (face.right(), face.bottom()), color, 2)
            cv2.putText(color_image, label, (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        return color_image

    def run(self):
        try:
            while True:
                result = self.process_frame()
                if result is None:
                    continue
                color_image, depth_image = result
                face_results = self.detect_faces(color_image, depth_image)
                output_image = self.draw_results(color_image, face_results)
                cv2.imshow("Face Anti-Spoofing", output_image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Thoát chương trình")
                    break
        finally:
            self.pipeline.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    fas = FaceAntiSpoofing()
    fas.run()