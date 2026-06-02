CREATE DATABASE IF NOT EXISTS recruitment_db;
USE recruitment_db;

-- Drop dependent tables first to avoid foreign key issues
DROP TABLE IF EXISTS CandidateSkills;
DROP TABLE IF EXISTS RequirementSkills;
DROP TABLE IF EXISTS JobRequirements;
DROP TABLE IF EXISTS Candidates;
DROP TABLE IF EXISTS CandidateAuditLog;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Skills;

-- 1. Users Table (Handles Authentication & Approvals)
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'recruiter', 'candidate') NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Candidates Table (Linked directly to Users)
CREATE TABLE Candidates (
    candidate_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE, -- Nullable if imported manually by a recruiter
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(15) DEFAULT '',
    qualification VARCHAR(100) DEFAULT '',
    experience DECIMAL(4,1) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 3. Skills Master Table
CREATE TABLE Skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) DEFAULT 'General'
);

-- 4. CandidateSkills Bridge Table
CREATE TABLE CandidateSkills (
    candidate_id INT,
    skill_id INT,
    proficiency VARCHAR(20) DEFAULT 'Intermediate',
    PRIMARY KEY (candidate_id, skill_id),
    FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES Skills(skill_id) ON DELETE CASCADE
);

-- 5. JobRequirements Table (Linked to Recruiter)
CREATE TABLE JobRequirements (
    requirement_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    created_by INT, -- Recruiter/Admin User ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES Users(user_id) ON DELETE SET NULL
);

-- 6. RequirementSkills Bridge Table
CREATE TABLE RequirementSkills (
    requirement_id INT,
    skill_id INT,
    is_mandatory BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (requirement_id, skill_id),
    FOREIGN KEY (requirement_id) REFERENCES JobRequirements(requirement_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES Skills(skill_id) ON DELETE CASCADE
);

-- 7. Audit Log Table
CREATE TABLE CandidateAuditLog (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT,
    old_name VARCHAR(100),
    new_name VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Audit Trigger
DELIMITER $$
CREATE TRIGGER log_candidate_update
AFTER UPDATE ON Candidates
FOR EACH ROW
BEGIN
    INSERT INTO CandidateAuditLog (candidate_id, old_name, new_name, changed_at)
    VALUES (NEW.candidate_id, OLD.name, NEW.name, CURRENT_TIMESTAMP);
END$$
DELIMITER ;

-- ==========================================
-- SEED DATA
-- ==========================================
INSERT INTO Skills (skill_name, category) VALUES
('Python', 'Programming'),
('SQL', 'Database'),
('Data Visualization', 'Analytics'),
('Flask', 'Web Development'),
('Machine Learning', 'Artificial Intelligence'),
('Java', 'Programming'),
('HTML/CSS', 'Web Development'),
('JavaScript', 'Web Development');