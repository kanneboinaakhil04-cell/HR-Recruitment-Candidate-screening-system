-- MySQL Schema for HR Recruitment & Candidate Screening System
-- Database creation
CREATE DATABASE IF NOT EXISTS hr_screening_db;
USE hr_screening_db;

-- 1. Users Table (Stores authentication credentials for HR and Candidates)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('hr', 'candidate')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. HR Profiles Table
CREATE TABLE IF NOT EXISTS hr_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    company VARCHAR(100) NOT NULL,
    department VARCHAR(100) DEFAULT 'Human Resources',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Candidate Profiles Table
CREATE TABLE IF NOT EXISTS candidate_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    education VARCHAR(100),
    experience_years INT DEFAULT 0,
    resume_filename VARCHAR(255),
    resume_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hr_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    required_skills_text TEXT NOT NULL,
    min_qualification VARCHAR(100) NOT NULL,
    min_experience_years INT NOT NULL DEFAULT 0,
    location VARCHAR(100) DEFAULT 'Remote',
    status VARCHAR(20) DEFAULT 'Open' CHECK (status IN ('Open', 'Closed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hr_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Master Skills Table
CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE,
    category VARCHAR(50) DEFAULT 'Technical'
);

-- 6. Job Skills (Junction Table)
CREATE TABLE IF NOT EXISTS job_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    skill_id INT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY unique_job_skill (job_id, skill_id)
);

-- 7. Candidate Skills (Junction Table)
CREATE TABLE IF NOT EXISTS candidate_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    skill_id INT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY unique_cand_skill (candidate_id, skill_id)
);

-- 8. Applications Table
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    candidate_id INT NOT NULL,
    match_score FLOAT NOT NULL DEFAULT 0.0,
    skill_score FLOAT NOT NULL DEFAULT 0.0,
    exp_score FLOAT NOT NULL DEFAULT 0.0,
    edu_score FLOAT NOT NULL DEFAULT 0.0,
    status VARCHAR(30) DEFAULT 'Applied' CHECK (status IN ('Applied', 'Reviewing', 'Shortlisted', 'Rejected')),
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    UNIQUE KEY unique_job_candidate (job_id, candidate_id)
);
