-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th2 28, 2025 lúc 03:16 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `face_recognition_sys`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `attendance`
--

CREATE TABLE `attendance` (
  `id_student` varchar(8) NOT NULL,
  `id_session` int(11) NOT NULL,
  `attendance_time` time DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `attendance`
--

INSERT INTO `attendance` (`id_student`, `id_session`, `attendance_time`, `status`) VALUES
('B2105661', 1, '09:27:00', 'Present'),
('B2105661', 2, '09:51:00', 'Present'),
('B2105684', 1, '00:00:00', 'Absent'),
('B2105684', 2, '00:00:00', 'Absent'),
('B2105709', 1, '00:00:00', 'Absent'),
('B2105709', 2, '00:00:00', 'Absent'),
('B2110011', 1, '09:27:00', 'Present'),
('B2110011', 2, '09:51:00', 'Present'),
('B2111930', 1, '00:00:00', 'Absent'),
('B2111930', 2, '00:00:00', 'Absent'),
('B2111946', 1, '00:00:00', 'Absent'),
('B2111946', 2, '00:00:00', 'Absent'),
('B2111949', 1, '00:00:00', 'Absent'),
('B2111949', 2, '00:00:00', 'Absent'),
('B2111952', 1, '00:00:00', 'Absent'),
('B2111952', 2, '00:00:00', 'Absent'),
('B2111955', 1, '09:27:00', 'Present'),
('B2111955', 2, '09:51:00', 'Present'),
('B2111959', 1, '00:00:00', 'Absent'),
('B2111959', 2, '00:00:00', 'Absent'),
('B2112004', 1, '00:00:00', 'Absent'),
('B2112004', 2, '00:00:00', 'Absent'),
('B2112010', 1, '09:27:00', 'Present'),
('B2112010', 2, '09:51:00', 'Present');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `class_subject`
--

CREATE TABLE `class_subject` (
  `id_class_subject` varchar(8) NOT NULL,
  `id_subject` varchar(8) DEFAULT NULL,
  `id_teacher` varchar(8) DEFAULT NULL,
  `year` varchar(9) DEFAULT NULL,
  `semester` int(11) DEFAULT NULL,
  `gr` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `class_subject`
--

INSERT INTO `class_subject` (`id_class_subject`, `id_subject`, `id_teacher`, `year`, `semester`, `gr`) VALUES
('DI0001', 'CT101H', '000001', '2023-2024', 1, 1),
('DI0002', 'CT101H', '000001', '2023-2024', 1, 2),
('DI0003', 'CT102H', '000002', '2023-2024', 1, 1),
('DI0004', 'CT103H', '000002', '2023-2024', 1, 1),
('DI0005', 'CT104H', '000002', '2023-2024', 2, 1),
('DI0006', 'CT105H', '000003', '2023-2024', 2, 2);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `register`
--

CREATE TABLE `register` (
  `id_student` varchar(8) NOT NULL,
  `id_class_subject` varchar(8) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `register`
--

INSERT INTO `register` (`id_student`, `id_class_subject`) VALUES
('B1910716', 'DI0003'),
('B2014956', 'DI0003'),
('B2105661', 'DI0003'),
('B2105663', 'DI0003'),
('B2105670', 'DI0003'),
('B2105686', 'DI0003'),
('B2105688', 'DI0003'),
('B2105689', 'DI0003'),
('B2105709', 'DI0003'),
('B2105727', 'DI0003'),
('B2110011', 'DI0003'),
('B2110058', 'DI0003'),
('B2111807', 'DI0003'),
('B2111862', 'DI0003'),
('B2111885', 'DI0003'),
('B2111919', 'DI0003'),
('B2111922', 'DI0003'),
('B2111927', 'DI0003'),
('B2111935', 'DI0003'),
('B2111940', 'DI0003'),
('B2111943', 'DI0003'),
('B2111945', 'DI0003'),
('B2111949', 'DI0003'),
('B2111955', 'DI0003'),
('B2111957', 'DI0003'),
('B2111959', 'DI0003'),
('B2111964', 'DI0003'),
('B2111971', 'DI0003'),
('B2111972', 'DI0003'),
('B2111974', 'DI0003'),
('B2111975', 'DI0003'),
('B2111978', 'DI0003'),
('B2111988', 'DI0003'),
('B2111989', 'DI0003'),
('B2111993', 'DI0003'),
('B2111994', 'DI0003'),
('B2111996', 'DI0003'),
('B2112000', 'DI0003'),
('B2112009', 'DI0003'),
('B2112010', 'DI0003'),
('B2112021', 'DI0003');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `session`
--

CREATE TABLE `session` (
  `id_session` int(11) NOT NULL,
  `id_class_subject` varchar(8) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `session`
--

INSERT INTO `session` (`id_session`, `id_class_subject`, `date`, `start_time`, `end_time`) VALUES
(1, 'DI0001', '2024-09-24', '07:00:00', '10:40:00'),
(2, 'DI0001', '2024-09-24', '07:00:00', '09:40:00');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `student`
--

CREATE TABLE `student` (
  `id_student` varchar(8) NOT NULL,
  `name_student` varchar(100) DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `pwd` varchar(8) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `student`
--

INSERT INTO `student` (`id_student`, `name_student`, `birthday`, `email`, `pwd`) VALUES
('B1910716', 'Phạm Thanh Tiến', '2003-01-01', 'tienb1910716@student.ctu.edu.vn', '123456az'),
('B2014956', 'Quan Cao Phuc Tri', '2003-01-01', 'trib2014956@student.ctu.edu.vn', '123456az'),
('B2103492', 'Tran Thanh Duy', '2003-08-04', 'duyb2103492@student.ctu.edu.vn', '123456az'),
('B2105661', 'Cao Tien Anh', '2003-02-10', 'anhb2105661@student.ctu.edu.vn', '123456az'),
('B2105662', 'Tran Duy Bao Anh', '2003-01-01', 'tranb2105662@student.ctu.edu.vn', '123456az'),
('B2105663', 'Tôn Thị Ngọc Châu', '2003-01-01', 'chaub2105663@student.ctu.edu.vn', '123456az'),
('B2105665', 'Lam Nhat Hao', '2003-01-01', 'lamb2105665@student.ctu.edu.vn', '123456az'),
('B2105667', 'Le Trung Huy', '2003-06-22', 'huyb2105667@student.ctu.edu.vn', '123456az'),
('B2105668', 'Truong Gia Huy', '2003-01-01', 'truongb2105668@student.ctu.edu.vn', '123456az'),
('B2105670', 'Duong Minh Khang', '2003-01-01', 'duongb2105670@student.ctu.edu.vn', '123456az'),
('B2105684', 'Le Anh Quan', '2003-11-19', 'quanb2105684@student.ctu.edu.vn', '123456az'),
('B2105686', 'Kim Duy Thanh', '2003-01-01', 'kimb2105686@student.ctu.edu.vn', '123456az'),
('B2105688', 'Nguyen Phuong Thuy', '2003-01-01', 'nguyenb2105688@student.ctu.edu.vn', '123456az'),
('B2105689', 'Nguyễn Trung Tín', '2003-01-01', 'tinb2105689@student.ctu.edu.vn', '123456az'),
('B2105695', 'Le Huy Anh', '2003-05-30', 'anhb2105695@student.ctu.edu.vn', '123456az'),
('B2105709', 'Khuc Bao Minh', '2003-10-27', 'minhb2105709@student.ctu.edu.vn', '123456az'),
('B2105718', 'Nguyen Van Quy', '2003-01-01', 'nguyenb2105718@student.ctu.edu.vn', '123456az'),
('B2105721', 'Nguyen Thai Thuan', '2003-01-01', 'nguyenb2105721@student.ctu.edu.vn', '123456az'),
('B2105723', 'Danh Tan Toi', '2003-01-01', 'danhb2105723@student.ctu.edu.vn', '123456az'),
('B2105727', 'Nguyen Quang Vinh', '2003-01-01', 'nguyenb2105727@student.ctu.edu.vn', '123456az'),
('B2108121', 'Nguyen Duy Thanh', '2003-01-01', 'nguyenb2108121@student.ctu.edu.vn', '123456az'),
('B2109666', 'To Kieu Diem Quynh', '2003-01-01', 'tob2109666@student.ctu.edu.vn', '123456az'),
('B2110011', 'Nguyen Nhat Hao', '2003-05-18', 'haob2110011@student.ctu.edu.vn', '123456az'),
('B2110058', 'Ho Chi Thanh', '2003-01-01', 'hoab2110058@student.ctu.edu.vn', '123456az'),
('B2110080', 'Dao Huu Khang', '2003-09-17', 'khangb2110080@student.ctu.edu.vn', '123456az'),
('B2110103', 'Ma Thanh Thong', '2003-10-11', 'thongb2110103@student.ctu.edu.vn', '123456az'),
('B2110128', 'Le Tuan Kiet', '2003-07-08', 'kietb2110128@student.ctu.edu.vn', '123456az'),
('B2111787', 'Doan Kha Ai', '2003-11-25', 'aib2111787@student.ctu.edu.vn', '123456az'),
('B2111807', 'Nguyễn Tấn Lộc', '2003-01-01', 'locb2111807@student.ctu.edu.vn', '123456az'),
('B2111862', 'Pham Tran Anh Tai', '2003-01-01', 'phamb2111862@student.ctu.edu.vn', '123456az'),
('B2111879', 'Dang Thanh Dat', '2003-04-25', 'datb2111879@student.ctu.edu.vn', '123456az'),
('B2111885', 'Ha Quoc Huy', '2003-01-01', 'hab2111885@student.ctu.edu.vn', '123456az'),
('B2111886', 'Nguyen Le Gia Hung', '2003-01-01', 'nguyenb2111886@student.ctu.edu.vn', '123456az'),
('B2111916', 'Vo Quoc Bang', '2003-01-01', 'vob2111916@student.ctu.edu.vn', '123456az'),
('B2111918', 'Duong Quoc Duy', '2003-01-01', 'duongb2111918@student.ctu.edu.vn', '123456az'),
('B2111919', 'Ho Duc Dung', '2003-01-01', 'hob2111919@student.ctu.edu.vn', '123456az'),
('B2111922', 'Nguyễn Trường Dũng Em', '2003-01-01', 'dungb2111922@student.ctu.edu.vn', '123456az'),
('B2111924', 'Nguyen Huynh Bao Han', '2003-01-01', 'nguyenb2111924@student.ctu.edu.vn', '123456az'),
('B2111927', 'Cao Minh Nhat Huy', '2003-01-01', 'caob2111927@student.ctu.edu.vn', '123456az'),
('B2111929', 'Tran Dinh Khang', '2003-01-01', 'tranb2111929@student.ctu.edu.vn', '123456az'),
('B2111930', 'Ly Phuong Khai', '2003-06-11', 'khaib2111930@student.ctu.edu.vn', '123456az'),
('B2111933', 'Truong Dang Truc Lam', '2003-01-01', 'truongb2111933@student.ctu.edu.vn', '123456az'),
('B2111935', 'Ngô Thành Lộc', '2003-01-01', 'locb2111935@student.ctu.edu.vn', '123456az'),
('B2111939', 'Nguyen Yen Ngoc', '2003-03-05', 'ngocb2111939@student.ctu.edu.vn', '123456az'),
('B2111940', 'Trần Thị Hồng Nhan', '2003-01-01', 'nhanb2111940@student.ctu.edu.vn', '123456az'),
('B2111943', 'Lê Trần Đại Phát', '2003-01-01', 'phatb2111943@student.ctu.edu.vn', '123456az'),
('B2111945', 'Hồ Phúc Hồng Phước', '2003-01-01', 'phuocb2111945@student.ctu.edu.vn', '123456az'),
('B2111946', 'Tran Minh Quang', '2003-04-05', 'quangb2111946@student.ctu.edu.vn', '123456az'),
('B2111948', 'Vo Tan Tai', '2003-01-01', 'vob2111948@student.ctu.edu.vn', '123456az'),
('B2111949', 'Ngo Thuy Thanh Tam', '2003-07-09', 'tamb2111949@student.ctu.edu.vn', '123456az'),
('B2111951', 'Vu Tran Quoc Thai', '2003-01-01', 'vub2111951@student.ctu.edu.vn', '123456az'),
('B2111952', 'Le Xuan Thanh', '2003-09-03', 'thanhb2111952@student.ctu.edu.vn', '123456az'),
('B2111955', 'Chau Dinh Thong', '2003-01-15', 'thongb2111955@student.ctu.edu.vn', '123456az'),
('B2111957', 'Phan Trung Thuan', '2003-01-01', 'phanb2111957@student.ctu.edu.vn', '123456az'),
('B2111959', 'Nguyen Thi Hoai Thuong', '2003-08-16', 'thuongb2111959@student.ctu.edu.vn', '123456az'),
('B2111961', 'Phan Thi Bich Tran', '2003-01-01', 'phanb2111961@student.ctu.edu.vn', '123456az'),
('B2111963', 'Ho Kim Trong', '2003-01-23', 'trongb2111963@student.ctu.edu.vn', '123456az'),
('B2111964', 'Bùi Ngọc Trúc', '2003-01-01', 'trucb2111964@student.ctu.edu.vn', '123456az'),
('B2111965', 'Trat Lam Truong', '2003-01-01', 'tratb2111965@student.ctu.edu.vn', '123456az'),
('B2111971', 'Nguyen Duy Bang', '2003-01-01', 'nguyenb2111971@student.ctu.edu.vn', '123456az'),
('B2111972', 'Nguyễn Trần Quang Bình', '2003-01-01', 'binhb2111972@student.ctu.edu.vn', '123456az'),
('B2111974', 'Trần Quốc Duy', '2003-01-01', 'duyb2111974@student.ctu.edu.vn', '123456az'),
('B2111975', 'Đỗ Thành Đạt', '2003-01-01', 'datb2111975@student.ctu.edu.vn', '123456az'),
('B2111976', 'Hoang Tien Dat', '2003-01-01', 'hoangb2111976@student.ctu.edu.vn', '123456az'),
('B2111978', 'Kiều Hoàng Giang', '2003-01-01', 'giangb2111978@student.ctu.edu.vn', '123456az'),
('B2111981', 'Nguyen Truong Thien Hieu', '2003-01-01', 'nguyenb2111981@student.ctu.edu.vn', '123456az'),
('B2111984', 'Dang Hoang Hung', '2003-01-01', 'dangb2111984@student.ctu.edu.vn', '123456az'),
('B2111988', 'Lê Cát Lam', '2003-01-01', 'lamb2111988@student.ctu.edu.vn', '123456az'),
('B2111989', 'Dao Thi Khanh Linh', '2003-01-01', 'daob2111989@student.ctu.edu.vn', '123456az'),
('B2111992', 'Ngo Thanh Nam', '2003-01-01', 'ngob2111992@student.ctu.edu.vn', '123456az'),
('B2111993', 'Nguyễn Thị Kim Ngân', '2003-01-01', 'nganb2111993@student.ctu.edu.vn', '123456az'),
('B2111994', 'Ngo Bao Ngoc', '2003-01-01', 'ngob2111994@student.ctu.edu.vn', '123456az'),
('B2111995', 'Tran Trung Nguyen', '2003-02-14', 'nguyenb2111995@student.ctu.edu.vn', '123456az'),
('B2111996', 'La Hoang Nhan', '2003-01-01', 'lab2111996@student.ctu.edu.vn', '123456az'),
('B2112000', 'Nguyễn Duy Diễm Phụng', '2003-01-01', 'phungb2112000@student.ctu.edu.vn', '123456az'),
('B2112002', 'Tran Van Sang', '2003-01-01', 'tranb2112002@student.ctu.edu.vn', '123456az'),
('B2112004', 'Le Thanh Tam', '2003-12-12', 'tamb2112004@student.ctu.edu.vn', '123456az'),
('B2112005', 'Do Huy Thinh', '2003-01-01', 'dob2112005@student.ctu.edu.vn', '123456az'),
('B2112009', 'Đỗ Huy Thịnh', '2003-01-01', 'thinhb2112009@student.ctu.edu.vn', '123456az'),
('B2112010', 'Nguyen Phu Thinh', '2003-03-22', 'thinhb2112010@student.ctu.edu.vn', '123456az'),
('B2112021', 'Hà Nhựt Tuấn', '2003-01-01', 'tuanb2112021@student.ctu.edu.vn', '123456az');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `subject`
--

CREATE TABLE `subject` (
  `id_subject` varchar(8) NOT NULL,
  `name_subject` varchar(100) DEFAULT NULL,
  `credit` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `subject`
--

INSERT INTO `subject` (`id_subject`, `name_subject`, `credit`) VALUES
('CT101H', 'Basic Programming', 4),
('CT102H', 'Data Structure', 4),
('CT103H', 'Database', 3),
('CT104H', 'College Study Skills', 2),
('CT105H', 'Discrete Math', 3);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `teacher`
--

CREATE TABLE `teacher` (
  `id_teacher` varchar(8) NOT NULL,
  `pwd` varchar(8) DEFAULT NULL,
  `name_teacher` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `teacher`
--

INSERT INTO `teacher` (`id_teacher`, `pwd`, `name_teacher`, `email`) VALUES
('000001', '123456aZ', 'Pham Nguyen Khang', 'pnkhang@ctu.edu.vn'),
('000002', '123456aZ', 'Pham Thi Ngoc Diem', 'ptndiem@ctu.edu.vn'),
('000003', '123456aZ', 'Nguyen Thu Huong', 'nthuong@ctu.edu.vn'),
('admin', '123456', 'Nguyen Van A ', 'abc@ctu.edu.vn');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`id_student`,`id_session`),
  ADD KEY `id_session` (`id_session`);

--
-- Chỉ mục cho bảng `class_subject`
--
ALTER TABLE `class_subject`
  ADD PRIMARY KEY (`id_class_subject`),
  ADD KEY `id_subject` (`id_subject`),
  ADD KEY `id_teacher` (`id_teacher`);

--
-- Chỉ mục cho bảng `register`
--
ALTER TABLE `register`
  ADD PRIMARY KEY (`id_student`,`id_class_subject`),
  ADD KEY `id_class_subject` (`id_class_subject`);

--
-- Chỉ mục cho bảng `session`
--
ALTER TABLE `session`
  ADD PRIMARY KEY (`id_session`),
  ADD KEY `id_class_subject` (`id_class_subject`);

--
-- Chỉ mục cho bảng `student`
--
ALTER TABLE `student`
  ADD PRIMARY KEY (`id_student`);

--
-- Chỉ mục cho bảng `subject`
--
ALTER TABLE `subject`
  ADD PRIMARY KEY (`id_subject`);

--
-- Chỉ mục cho bảng `teacher`
--
ALTER TABLE `teacher`
  ADD PRIMARY KEY (`id_teacher`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `session`
--
ALTER TABLE `session`
  MODIFY `id_session` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `attendance`
--
ALTER TABLE `attendance`
  ADD CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`id_student`) REFERENCES `student` (`id_student`),
  ADD CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`id_session`) REFERENCES `session` (`id_session`);

--
-- Các ràng buộc cho bảng `class_subject`
--
ALTER TABLE `class_subject`
  ADD CONSTRAINT `class_subject_ibfk_1` FOREIGN KEY (`id_subject`) REFERENCES `subject` (`id_subject`),
  ADD CONSTRAINT `class_subject_ibfk_2` FOREIGN KEY (`id_teacher`) REFERENCES `teacher` (`id_teacher`);

--
-- Các ràng buộc cho bảng `register`
--
ALTER TABLE `register`
  ADD CONSTRAINT `register_ibfk_1` FOREIGN KEY (`id_student`) REFERENCES `student` (`id_student`),
  ADD CONSTRAINT `register_ibfk_2` FOREIGN KEY (`id_class_subject`) REFERENCES `class_subject` (`id_class_subject`);

--
-- Các ràng buộc cho bảng `session`
--
ALTER TABLE `session`
  ADD CONSTRAINT `session_ibfk_1` FOREIGN KEY (`id_class_subject`) REFERENCES `class_subject` (`id_class_subject`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
