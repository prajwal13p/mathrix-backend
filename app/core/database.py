from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_missing_tables():
    """Create missing tables if they don't exist"""
    try:
        with engine.connect() as connection:
            # Check if team_requests table exists
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'team_requests'
            """))
            
            if result.scalar() == 0:
                print("🔧 Creating missing team_requests table...")
                connection.execute(text("""
                    CREATE TABLE team_requests (
                        request_id UUID PRIMARY KEY,
                        from_participant_id UUID NOT NULL,
                        to_participant_id UUID NOT NULL,
                        team_id UUID NULL,
                        message TEXT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        responded_at TIMESTAMP NULL,
                        
                        FOREIGN KEY (from_participant_id) REFERENCES participants(participant_id),
                        FOREIGN KEY (to_participant_id) REFERENCES participants(participant_id),
                        FOREIGN KEY (team_id) REFERENCES teams(team_id)
                    )
                """))
                
                # Create indexes
                connection.execute(text("""
                    CREATE INDEX idx_team_requests_from ON team_requests(from_participant_id)
                """))
                connection.execute(text("""
                    CREATE INDEX idx_team_requests_to ON team_requests(to_participant_id)
                """))
                connection.execute(text("""
                    CREATE INDEX idx_team_requests_team ON team_requests(team_id)
                """))
                connection.execute(text("""
                    CREATE INDEX idx_team_requests_status ON team_requests(status)
                """))
                
                connection.commit()
                print("✅ team_requests table created successfully!")
            
            # Check if teams table has new columns
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'teams' 
                AND column_name = 'is_locked'
            """))
            
            if result.scalar() == 0:
                print("🔧 Adding new columns to teams table...")
                connection.execute(text("""
                    ALTER TABLE teams 
                    ADD COLUMN description TEXT NULL,
                    ADD COLUMN is_locked BOOLEAN DEFAULT FALSE,
                    ADD COLUMN is_open_to_requests BOOLEAN DEFAULT TRUE,
                    ADD COLUMN max_members VARCHAR(10) DEFAULT '4',
                    ADD COLUMN tags VARCHAR(200) NULL
                """))
                
                # Update existing teams with default values
                connection.execute(text("""
                    UPDATE teams SET 
                        is_locked = FALSE,
                        is_open_to_requests = TRUE,
                        max_members = '4'
                    WHERE is_locked IS NULL
                """))
                
                connection.commit()
                print("✅ Teams table updated successfully!")
                
    except Exception as e:
        print(f"⚠️ Warning: Could not create missing tables: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create missing tables on import
create_missing_tables()
