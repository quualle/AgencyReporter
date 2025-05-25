"""
Database connection management for SQLite-based cache storage.
Handles database initialization, session management, and connection pooling.
"""

import os
import logging
from typing import AsyncGenerator, Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager, contextmanager

from ..models.database import Base, CachedData, PreloadSession, DataFreshness

# Set up logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages database connections and sessions for the cache system.
    Provides both sync and async interfaces.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Optional database URL. If None, uses default SQLite location.
        """
        if database_url is None:
            # Default to SQLite in the database folder
            db_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database")
            os.makedirs(db_folder, exist_ok=True)
            database_url = f"sqlite:///{os.path.join(db_folder, 'agency_cache.db')}"
        
        self.database_url = database_url
        self.async_database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")
        
        # Sync engine for migrations and initial setup
        self.sync_engine = create_engine(
            database_url,
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,  # Allow multiple threads to use the same connection
                "timeout": 20  # 20 second timeout for database operations
            },
            echo=False  # Set to True for SQL debugging
        )
        
        # Async engine for application use
        self.async_engine = create_async_engine(
            self.async_database_url,
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
                "timeout": 20
            },
            echo=False
        )
        
        # Session makers
        self.sync_session_maker = sessionmaker(
            bind=self.sync_engine,
            autocommit=False,
            autoflush=False
        )
        
        self.async_session_maker = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        # Enable WAL mode and other optimizations for SQLite
        self._configure_sqlite()
        
        logger.info(f"Database manager initialized with URL: {database_url}")
    
    def _configure_sqlite(self):
        """Configure SQLite for optimal performance."""
        
        @event.listens_for(self.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for better performance."""
            cursor = dbapi_connection.cursor()
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            # Set synchronous to NORMAL for better performance while maintaining safety
            cursor.execute("PRAGMA synchronous=NORMAL")
            # Increase cache size to 128MB
            cursor.execute("PRAGMA cache_size=-128000")
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            # Set busy timeout to 60 seconds
            cursor.execute("PRAGMA busy_timeout=60000")
            # Use READ UNCOMMITTED isolation level for better concurrency
            cursor.execute("PRAGMA read_uncommitted=0")
            # Optimize for many concurrent writes
            cursor.execute("PRAGMA wal_autocheckpoint=1000")
            cursor.close()
        
        @event.listens_for(self.async_engine.sync_engine, "connect")
        def set_sqlite_pragma_async(dbapi_connection, connection_record):
            """Set SQLite pragmas for async engine."""
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-128000")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=60000")
            cursor.execute("PRAGMA read_uncommitted=0")
            cursor.execute("PRAGMA wal_autocheckpoint=1000")
            cursor.close()
    
    def create_tables(self):
        """Create all database tables. Should be called during app startup."""
        try:
            Base.metadata.create_all(bind=self.sync_engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables. Use with caution!"""
        try:
            Base.metadata.drop_all(bind=self.sync_engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping database tables: {e}")
            raise
    
    @contextmanager
    def get_sync_session(self) -> Session:
        """
        Get a synchronous database session with automatic cleanup.
        
        Usage:
            with db_manager.get_sync_session() as session:
                # Use session here
                session.add(object)
                session.commit()
        """
        session = self.sync_session_maker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an asynchronous database session with automatic cleanup.
        
        Usage:
            async with db_manager.get_async_session() as session:
                # Use session here
                session.add(object)
                await session.commit()
        """
        session = self.async_session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            async with self.get_async_session() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_database_size(self) -> int:
        """Get database file size in bytes."""
        if "sqlite" in self.database_url:
            db_path = self.database_url.replace("sqlite:///", "")
            if os.path.exists(db_path):
                return os.path.getsize(db_path)
        return 0
    
    def get_database_info(self) -> dict:
        """Get database information for debugging."""
        info = {
            "database_url": self.database_url,
            "size_bytes": self.get_database_size(),
            "size_mb": round(self.get_database_size() / 1024 / 1024, 2)
        }
        
        # Get table counts
        try:
            with self.get_sync_session() as session:
                info["cached_data_count"] = session.query(CachedData).count()
                info["preload_sessions_count"] = session.query(PreloadSession).count()
                info["data_freshness_count"] = session.query(DataFreshness).count()
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            info["error"] = str(e)
        
        return info
    
    async def cleanup_expired_data(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed.
        """
        try:
            async with self.get_async_session() as session:
                # Find expired entries
                result = await session.execute(
                    text("DELETE FROM cached_data WHERE expires_at IS NOT NULL AND expires_at < datetime('now')")
                )
                await session.commit()
                
                deleted_count = result.rowcount
                logger.info(f"Cleaned up {deleted_count} expired cache entries")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {e}")
            return 0
    
    async def vacuum_database(self):
        """Optimize database by running VACUUM (SQLite only)."""
        if "sqlite" in self.database_url:
            try:
                async with self.get_async_session() as session:
                    await session.execute(text("VACUUM"))
                    await session.commit()
                    logger.info("Database VACUUM completed")
            except Exception as e:
                logger.error(f"Error running VACUUM: {e}")
    
    def close(self):
        """Close all database connections."""
        try:
            self.sync_engine.dispose()
            if hasattr(self, 'async_engine'):
                # Note: async engine disposal should be done in async context
                pass
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Global database manager instance
db_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def initialize_database(database_url: Optional[str] = None) -> DatabaseManager:
    """
    Initialize the database and create tables.
    Should be called during application startup.
    """
    global db_manager
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()
    return db_manager

async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function for FastAPI to get async database sessions.
    
    Usage in FastAPI routes:
        @app.get("/endpoint")
        async def endpoint(session: AsyncSession = Depends(get_async_db_session)):
            # Use session here
    """
    db = get_database_manager()
    async with db.get_async_session() as session:
        yield session