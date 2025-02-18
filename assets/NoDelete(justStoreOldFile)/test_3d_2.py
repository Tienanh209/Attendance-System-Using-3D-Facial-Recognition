import os
import numpy as np
import pyrealsense2 as rs
import cv2
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
import logging
import time
import open3d as o3d  # Thêm Open3D để xử lý Point Cloud

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_point_cloud_1(depth_frame, intrinsics):
    """Chuyển depth frame thành point cloud để tái tạo 3D mesh."""
    points = []
    for y in range(depth_frame.height):
        for x in range(depth_frame.width):
            depth = depth_frame.get_distance(x, y)
            if depth > 0:
                point = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], depth)
                points.append(point)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    # return pcd
    # Giảm độ phân giải bằng voxel downsampling
    pcd_down = pcd.voxel_down_sample(voxel_size=0.01)  # Điều chỉnh voxel_size để tối ưu
    return pcd_down

def process_point_cloud_2(depth_frame, intrinsics):
    """Chuyển depth frame thành 3D mesh thay vì chỉ point cloud."""
    points = []
    for y in range(depth_frame.height):
        for x in range(depth_frame.width):
            depth = depth_frame.get_distance(x, y)
            if depth > 0:
                point = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], depth)
                points.append(point)

    # Tạo point cloud từ danh sách điểm
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    # Giảm độ phân giải bằng voxel downsampling
    pcd_down = pcd.voxel_down_sample(voxel_size=0.01)

    # Chuyển Point Cloud thành Mesh bằng Alpha Shape
    pcd_down.estimate_normals()  # Tính toán normal
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd_down, alpha=0.03)
    mesh.compute_vertex_normals()  # Tính toán normal cho Mesh

    return mesh  # Trả về Mesh thay vì Point Cloud

def process_point_cloud(depth_frame, intrinsics, stride=3, voxel_size=0.02):
    """Tạo Point Cloud với stride và Octree để giảm số điểm."""
    points = []
    width, height = depth_frame.width, depth_frame.height

    for y in range(0, height, stride):  # Lấy mẫu từng stride pixel
        for x in range(0, width, stride):
            depth = depth_frame.get_distance(x, y)
            if 0 < depth < 2.5:  # Giới hạn khoảng cách hợp lệ
                point = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], depth)
                points.append(point)

    if not points:
        return None

    # Chuyển sang Open3D Point Cloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    # Giảm số điểm bằng Octree (tối ưu hơn voxel downsampling)
    octree = o3d.geometry.Octree(max_depth=4)
    octree.convert_from_point_cloud(pcd, size_expand=0.01)

    return octree.to_voxel_grid()  # Trả về dạng lưới voxel (nhẹ hơn)

def run_face_recognition_3d(embeddings_dir='../../assets/DataEmbeddings/', depth_min=0, depth_max=2500,
                            similarity_threshold=0.5, frame_width=640, frame_height=480):
    def _load_database():
        database = {}
        try:
            for file in os.listdir(embeddings_dir):
                if file.endswith(".npy"):
                    person_id = os.path.splitext(file)[0]
                    database[person_id] = np.load(os.path.join(embeddings_dir, file))
            logger.info(f"Đã tải {len(database)} embeddings")
            return database
        except Exception as e:
            logger.error(f"Lỗi tải database: {str(e)}")
            raise

    def _setup_realsense():
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, frame_width, frame_height, rs.format.bgr8, 15) #giảm từ 30 xuống 15
        config.enable_stream(rs.stream.depth, frame_width, frame_height, rs.format.z16, 15) #giảm từ 30 xuống 15
        align = rs.align(rs.stream.color)
        pipeline.start(config)
        return pipeline, align

    def _setup_face_analyzer():
        # app = FaceAnalysis(providers=['CPUExecutionProvider'])
        app = FaceAnalysis(providers=['CUDAExecutionProvider'])  # Chạy trên GPU thay vì CPU

        app.prepare(ctx_id=-1)
        return app

    database = _load_database()
    pipeline, align = _setup_realsense()
    face_analyzer = _setup_face_analyzer()
    executor = ThreadPoolExecutor(max_workers=2)

    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            if not color_frame or not depth_frame:
                continue

            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())
            intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics

            # Tạo Point Cloud
            point_cloud = process_point_cloud(depth_frame, intrinsics)

            # Nhận diện khuôn mặt
            faces = face_analyzer.get(color_image)

            if not faces:
                logger.warning("Không phát hiện khuôn mặt nào, bỏ qua frame này.")
                cv2.imshow("3D Face Recognition", color_image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue  # Bỏ qua frame này và tiếp tục vòng lặp

            for face in faces:
                box = face.bbox.astype(int)
                embedding = face.embedding
                center_x = (box[0] + box[2]) // 2
                center_y = (box[1] + box[3]) // 2
                depth_value = depth_frame.get_distance(center_x, center_y) * 1000

                if not (depth_min < depth_value < depth_max):
                    person_id, confidence = "Fake Face", 0
                else:
                    similarities = {k: cosine_similarity([embedding], [v])[0][0] for k, v in database.items()}
                    best_match = max(similarities, key=similarities.get, default="Unknown")
                    confidence = similarities.get(best_match, 0)
                    person_id = best_match if confidence > similarity_threshold else "Unknown"

                color = (0, 255, 0) if person_id != "Fake Face" else (0, 0, 255)
                cv2.rectangle(color_image, (box[0], box[1]), (box[2], box[3]), color, 2)
                cv2.putText(color_image, f"{person_id} ({confidence:.2f})", (box[0], box[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(color_image, f"Depth: {depth_value:.0f}mm", (box[0], box[3] + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            cv2.imshow("3D Face Recognition", color_image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        logger.error(f"Lỗi xử lý: {str(e)}")
    finally:
        pipeline.stop()
        executor.shutdown()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run_face_recognition_3d()
