-- 데이터베이스가 이미 존재하면 삭제하고 새로 생성
DROP DATABASE IF EXISTS bolla;
CREATE DATABASE bolla;
USE bolla;
-- 기존의 테이블이 있으면 삭제
DROP TABLE IF EXISTS license_plates;
-- 테이블 생성
CREATE TABLE license_plates (
id INT AUTO_INCREMENT PRIMARY KEY, -- id : 자동 증가 기본 키
license_plate VARCHAR(20) NOT NULL, -- 최대 20자의 문자열, 비어 있을 수 없음
plate_type ENUM('장애인', '전기차') NOT NULL -- '장애인' 또는 '전기차'만 허용
);
-- 데이터 삽입
INSERT INTO license_plates (license_plate, plate_type)
VALUES
('55구1601', '전기차'),
('154러7070', '장애인'),
('97보5321', '장애인'),
('50노6821', '전기차'),
('45가6492', '장애인'),
('786조3725', '전기차'),
('05하4727', '장애인'),
('19오7777', '장애인'),
('55나2222', '전기차'),
('111호1111', '장애인'),
('77더7777', '전기차'),
('40서1498', '장애인'),
('123가4568', '장애인'),
('68오8269', '장애인');