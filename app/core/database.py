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
            # First, create base tables if they don't exist
            # Check if participants table exists
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'participants'
            """))
            
            if result.scalar() == 0:
                print("🔧 Creating participants table...")
                connection.execute(text("""
                    CREATE TABLE participants (
                        participant_id UUID PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        usn VARCHAR(20) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        skills JSON NOT NULL,
                        team_id UUID NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                connection.commit()
                print("✅ participants table created successfully!")
            
            # Check if teams table exists
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'teams'
            """))
            
            if result.scalar() == 0:
                print("🔧 Creating teams table...")
                connection.execute(text("""
                    CREATE TABLE teams (
                        team_id UUID PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        leader_id UUID NOT NULL,
                        description TEXT NULL,
                        is_locked BOOLEAN DEFAULT FALSE,
                        is_open_to_requests BOOLEAN DEFAULT TRUE,
                        max_members VARCHAR(10) DEFAULT '4',
                        tags VARCHAR(200) NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (leader_id) REFERENCES participants(participant_id)
                    )
                """))
                connection.commit()
                print("✅ teams table created successfully!")
            
            # Now create team_requests table (after base tables exist)
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'team_requests'
            """))
            
            if result.scalar() == 0:
                print("🔧 Creating team_requests table...")
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
            
            # Check if teams table has new columns and add them if missing
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'teams' 
                AND column_name = 'is_locked'
            """))
            
            if result.scalar() == 0:
                print("🔧 Adding new columns to teams table...")
                try:
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
                except Exception as alter_error:
                    print(f"⚠️ Warning: Could not alter teams table: {alter_error}")
                
    except Exception as e:
        print(f"⚠️ Warning: Could not create missing tables: {e}")

def migrate_existing_tables():
    """Migrate existing tables to new schema if needed"""
    try:
        with engine.connect() as connection:
            # Check if participants table needs migration
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'participants' 
                AND column_name = 'password_hash'
            """))
            
            if result.scalar() == 0:
                print("🔧 Migrating participants table to new schema...")
                try:
                    # First try to add columns
                    try:
                        connection.execute(text("""
                            ALTER TABLE participants 
                            ADD COLUMN password_hash VARCHAR(255) DEFAULT 'temp_hash',
                            ADD COLUMN skills JSON DEFAULT '[]'::json
                        """))
                        connection.commit()
                        print("✅ Participants table migrated successfully!")
                    except Exception as alter_error:
                        print(f"⚠️ Alter failed, trying to recreate table: {alter_error}")
                        
                        # If alter fails, recreate the table
                        # First backup existing data
                        try:
                            backup_result = connection.execute(text("SELECT * FROM participants"))
                            existing_data = backup_result.fetchall()
                            print(f"📋 Backed up {len(existing_data)} existing participants")
                        except:
                            existing_data = []
                            print("📋 No existing data to backup")
                        
                        # Drop and recreate table
                        connection.execute(text("DROP TABLE IF EXISTS participants CASCADE"))
                        connection.execute(text("""
                            CREATE TABLE participants (
                                participant_id UUID PRIMARY KEY,
                                email VARCHAR(255) UNIQUE NOT NULL,
                                usn VARCHAR(20) UNIQUE NOT NULL,
                                name VARCHAR(255) NOT NULL,
                                password_hash VARCHAR(255) NOT NULL,
                                skills JSON NOT NULL,
                                team_id UUID NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """))
                        
                        # Reinsert data if any existed
                        if existing_data:
                            for row in existing_data:
                                try:
                                    connection.execute(text("""
                                        INSERT INTO participants (participant_id, email, usn, name, password_hash, skills, team_id, created_at)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    """), (row[0], row[1], row[2], row[3], 'temp_hash', '[]', row[4] if len(row) > 4 else None, row[5] if len(row) > 5 else None))
                                except Exception as insert_error:
                                    print(f"⚠️ Could not reinsert participant {row[0]}: {insert_error}")
                        
                        connection.commit()
                        print("✅ Participants table recreated successfully!")
                        
                except Exception as migrate_error:
                    print(f"⚠️ Warning: Could not migrate participants table: {migrate_error}")
                    
    except Exception as e:
        print(f"⚠️ Warning: Could not migrate existing tables: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Tables will be created on startup via main.py
