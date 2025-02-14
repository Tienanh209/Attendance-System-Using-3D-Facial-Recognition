import os
import numpy as np
import pyrealsense2 as rs
import cv2
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
import logging
import time

def run_face_recognition_3d(embeddings_dir='../../assets/DataEmbeddings/', depth_min=0, depth_max=2500,
                            similarity_threshold=0.5, frame_width=640, frame_height=480):
    # Cấu hình logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def _load_database():
        database = {}
        try:
            for file in os.listdir(embeddings_dir):
                if file.endswith(".npy"):
                    person_id = os.path.splitext(file)[0]
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
        config.enable_stream(rs.stream.color, frame_width, frame_height, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, frame_width, frame_height, rs.format.z16, 30)

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

    def _process_face(face, depth_image, database):
        box = face.bbox.astype(int)
        embedding = face.embedding

        # Lấy vùng depth của khuôn mặt
        center_x = (box[0] + box[2]) // 2
        center_y = (box[1] + box[3]) // 2
        depth_value = depth_frame.get_distance(center_x, center_y) * 1000  # Đổi sang mm

        # Kiểm tra liveness
        if not (depth_min < depth_value < depth_max):
            return box, "Fake Face", depth_value, 0

        person_id, confidence = _find_best_match(embedding, database)
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
                executor.submit(_process_face, face, depth_image, database)
                for face in faces
            ]

            # Hiển thị kết quả
            for future in face_futures:
                box, person_id, depth_value, confidence = future.result()

                # Vẽ khung và thông tin trên ảnh màu
                color = (0, 255, 0) if person_id != "Fake Face" else (0, 0, 255)
                cv2.rectangle(color_image, (box[0], box[1]), (box[2], box[3]), color, 2)

                label = f"{person_id} ({confidence:.2f})" if person_id != "Fake Face" else person_id
                cv2.putText(color_image, label, (box[0], box[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(color_image, f"Depth: {depth_value:.0f}mm",
                            (box[0], box[3] + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Áp dụng colormap trên hình ảnh độ sâu
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            # Vẽ khung trên hình ảnh độ sâu tương tự như trên ảnh màu
            for future in face_futures:
                box, person_id, depth_value, confidence = future.result()

                # Vẽ khung trên ảnh độ sâu
                color = (0, 255, 0) if person_id != "Fake Face" else (0, 0, 255)
                cv2.rectangle(depth_colormap, (box[0], box[1]), (box[2], box[3]), color, 2)

            # Hiển thị FPS
            cv2.putText(color_image, f"FPS: {fps}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Hiển thị ảnh màu và ảnh độ sâu
            cv2.imshow("3D Face Recognition", color_image)
           # cv2.imshow("Depth Image", depth_colormap)

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

if __name__ == "__main__":
    run_face_recognition_3d()