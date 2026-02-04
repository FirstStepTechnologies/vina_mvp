"""
Database initialization script.
Drops all existing tables and recreates them with the current schema.

WARNING: This will delete all existing data. Use only for development/hackathon.
For production, use proper migrations (Alembic).
"""
import sys
from pathlib import Path

# Add src to path so we can import vina_backend
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vina_backend.integrations.db.engine import engine
from vina_backend.integrations.db.models.user import UserProfile
# Import any other models you have
# from vina_backend.integrations.db.models.session import LearnerSession
# from vina_backend.integrations.db.models.quiz import QuizAttempt

from sqlmodel import SQLModel


def init_database(drop_existing: bool = True):
    """
    Initialize the database with all tables.
    
    Args:
        drop_existing: If True, drops all existing tables before recreating.
                      If False, only creates tables that don't exist.
    """
    print("🗄️  Initializing database...")
    print(f"   Database: {engine.url}")
    
    if drop_existing:
        print("\n⚠️  WARNING: Dropping all existing tables...")
        print("   This will DELETE ALL DATA in the database.")
        
        # In production, you'd want confirmation here
        # For hackathon, we auto-confirm
        response = input("   Continue? (yes/no): ").lower().strip()
        
        if response != "yes":
            print("   Aborted.")
            return
        
        # Drop all tables
        SQLModel.metadata.drop_all(engine)
        print("   ✅ All tables dropped")
    
    # Create all tables
    print("\n📋 Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("   ✅ All tables created")
    
    # List created tables
    print("\n📊 Database schema:")
    for table_name in SQLModel.metadata.tables.keys():
        print(f"   - {table_name}")
    
    print("\n✅ Database initialization complete!")


def reset_database():
    """
    Convenience function: drop and recreate (no confirmation).
    Use this for automated scripts.
    """
    print("🔄 Resetting database (no confirmation)...")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print("✅ Database reset complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize the Vina database")
    parser.add_argument(
        "--no-drop",
        action="store_true",
        help="Don't drop existing tables, only create new ones"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reset without confirmation (dangerous!)"
    )
    
    args = parser.parse_args()
    
    if args.force:
        reset_database()
    else:
        init_database(drop_existing=not args.no_drop)