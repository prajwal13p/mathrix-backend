#!/usr/bin/env python3
"""
Script to set up the enhanced team formation system tables
"""

import pymysql
from pymysql.constants import CLIENT

def setup_database():
    # Database connection
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='130919@pP',
        database='college_events',
        charset='utf8mb4',
        client_flag=CLIENT.MULTI_STATEMENTS
    )
    
    try:
        with connection.cursor() as cursor:
            print("🔧 Setting up enhanced team formation tables...")
            
            # Add new fields to existing teams table
            print("📝 Adding new fields to teams table...")
            cursor.execute("""
                ALTER TABLE teams 
                ADD COLUMN IF NOT EXISTS description TEXT NULL,
                ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS is_open_to_requests BOOLEAN DEFAULT TRUE,
                ADD COLUMN IF NOT EXISTS max_members VARCHAR(10) DEFAULT '4',
                ADD COLUMN IF NOT EXISTS tags VARCHAR(200) NULL
            """)
            
            # Create team_requests table
            print("📝 Creating team_requests table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_requests (
                    request_id CHAR(36) PRIMARY KEY,
                    from_participant_id CHAR(36) NOT NULL,
                    to_participant_id CHAR(36) NOT NULL,
                    team_id CHAR(36) NULL,
                    message TEXT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    responded_at DATETIME NULL,
                    
                    FOREIGN KEY (from_participant_id) REFERENCES participants(participant_id),
                    FOREIGN KEY (to_participant_id) REFERENCES participants(participant_id),
                    FOREIGN KEY (team_id) REFERENCES teams(team_id)
                )
            """)
            
            # Create indexes
            print("📝 Creating indexes...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_team_requests_from ON team_requests(from_participant_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_team_requests_to ON team_requests(to_participant_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_team_requests_team ON team_requests(team_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_team_requests_status ON team_requests(status)
            """)
            
            # Update existing teams with default values
            print("📝 Updating existing teams...")
            cursor.execute("""
                UPDATE teams SET 
                    is_locked = FALSE,
                    is_open_to_requests = TRUE,
                    max_members = '4'
                WHERE is_locked IS NULL
            """)
            
            # Commit changes
            connection.commit()
            print("✅ Database setup completed successfully!")
            
            # Show table structure
            print("\n📊 Current table structure:")
            cursor.execute("DESCRIBE teams")
            teams_structure = cursor.fetchall()
            print("Teams table:")
            for row in teams_structure:
                print(f"  {row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]} - {row[5]}")
            
            cursor.execute("DESCRIBE team_requests")
            requests_structure = cursor.fetchall()
            print("\nTeam Requests table:")
            for row in requests_structure:
                print(f"  {row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]} - {row[5]}")
                
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    setup_database()
