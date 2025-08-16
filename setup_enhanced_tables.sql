-- Enhanced Participant Table for MCA Event Registration
-- This script updates the existing participants table with new fields

-- Drop existing participants table if it exists
DROP TABLE IF EXISTS participants;

-- Create new participants table with updated schema
CREATE TABLE participants (
    participant_id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    usn VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    skills JSON NOT NULL,
    team_id CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_usn (usn),
    INDEX idx_team_id (team_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL
);

-- Create teams table if it doesn't exist
CREATE TABLE IF NOT EXISTS teams (
    team_id CHAR(36) PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    leader_id CHAR(36),
    max_members INT DEFAULT 4,
    is_locked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (leader_id) REFERENCES participants(participant_id) ON DELETE SET NULL
);

-- Add any additional indexes for performance
CREATE INDEX IF NOT EXISTS idx_participants_created_at ON participants(created_at);
CREATE INDEX IF NOT EXISTS idx_teams_created_at ON teams(created_at);
