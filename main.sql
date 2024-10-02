CREATE TABLE Students (
    student_id INT PRIMARY KEY,      -- 學號
    class VARCHAR(50),               -- 班級
    name VARCHAR(100),               -- 姓名
    seat_number INT                  -- 座號
);

CREATE TABLE Teachers (
    teacher_id INT PRIMARY KEY,      -- 教師編號
    name VARCHAR(100)                -- 姓名
);

CREATE TABLE EntryExitLogs (
    log_id SERIAL PRIMARY KEY,       -- 自動生成的紀錄編號
    person_id INT,                   -- 學號或教師編號
    name VARCHAR(100),               -- 姓名
    class VARCHAR(50),               -- 班級（適用於學生，老師可以為NULL）
    timestamp TIMESTAMP,             -- 時間點
    entry_exit VARCHAR(10),          -- '進場'或'出場'
    person_type VARCHAR(10),         -- '學生'或'老師'
);

CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,      -- 使用者編號
    username VARCHAR(50) UNIQUE,     -- 帳號
    password VARCHAR(100),           -- 密碼
    name VARCHAR(100),               -- 姓名
);
