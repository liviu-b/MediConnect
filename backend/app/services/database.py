"""
Database Service with Retry Logic and Connection Management
Implements best practices for database operations
"""

import logging
from typing import Optional, Any, Dict, List
from functools import wraps
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger("mediconnect")


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry database operations on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Usage:
        @retry_on_failure(max_retries=3, delay=1.0)
        async def get_user(user_id: str):
            return await db.users.find_one({"user_id": user_id})
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            f"Database operation failed (attempt {attempt + 1}/{max_retries}). "
                            f"Retrying in {wait_time}s... Error: {e}"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(
                            f"Database operation failed after {max_retries} attempts: {e}"
                        )
                except Exception as e:
                    # Don't retry on other exceptions
                    logger.error(f"Database operation failed with non-retryable error: {e}")
                    raise
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator


class DatabaseService:
    """
    Database service with connection management and best practices.
    
    Features:
    - Connection pooling
    - Automatic retries
    - Query optimization
    - Index management
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    @retry_on_failure(max_retries=3)
    async def find_one(
        self,
        collection: str,
        filter: Dict[str, Any],
        projection: Optional[Dict[str, int]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single document with retry logic.
        
        Args:
            collection: Collection name
            filter: Query filter
            projection: Fields to include/exclude
            
        Returns:
            Document or None
        """
        return await self.db[collection].find_one(filter, projection)
    
    @retry_on_failure(max_retries=3)
    async def find_many(
        self,
        collection: str,
        filter: Dict[str, Any],
        projection: Optional[Dict[str, int]] = None,
        limit: int = 100,
        skip: int = 0,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents with retry logic.
        
        Args:
            collection: Collection name
            filter: Query filter
            projection: Fields to include/exclude
            limit: Maximum number of documents
            skip: Number of documents to skip
            sort: Sort order
            
        Returns:
            List of documents
        """
        cursor = self.db[collection].find(filter, projection)
        
        if sort:
            cursor = cursor.sort(sort)
        
        if skip > 0:
            cursor = cursor.skip(skip)
        
        if limit > 0:
            cursor = cursor.limit(limit)
        
        return await cursor.to_list(length=limit)
    
    @retry_on_failure(max_retries=3)
    async def insert_one(
        self,
        collection: str,
        document: Dict[str, Any]
    ) -> str:
        """
        Insert a single document with retry logic.
        
        Args:
            collection: Collection name
            document: Document to insert
            
        Returns:
            Inserted document ID
        """
        result = await self.db[collection].insert_one(document)
        return str(result.inserted_id)
    
    @retry_on_failure(max_retries=3)
    async def update_one(
        self,
        collection: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False
    ) -> int:
        """
        Update a single document with retry logic.
        
        Args:
            collection: Collection name
            filter: Query filter
            update: Update operations
            upsert: Create if not exists
            
        Returns:
            Number of modified documents
        """
        result = await self.db[collection].update_one(filter, update, upsert=upsert)
        return result.modified_count
    
    @retry_on_failure(max_retries=3)
    async def delete_one(
        self,
        collection: str,
        filter: Dict[str, Any]
    ) -> int:
        """
        Delete a single document with retry logic.
        
        Args:
            collection: Collection name
            filter: Query filter
            
        Returns:
            Number of deleted documents
        """
        result = await self.db[collection].delete_one(filter)
        return result.deleted_count
    
    async def create_indexes(self):
        """
        Create database indexes for optimal performance.
        
        Best Practice:
        - Create indexes on frequently queried fields
        - Use compound indexes for multi-field queries
        - Monitor index usage and remove unused indexes
        """
        try:
            # Users collection indexes
            await self.db.users.create_index("email", unique=True)
            await self.db.users.create_index("user_id", unique=True)
            await self.db.users.create_index([("organization_id", 1), ("role", 1)])
            
            # Doctors collection indexes
            await self.db.doctors.create_index("doctor_id", unique=True)
            await self.db.doctors.create_index("email")
            await self.db.doctors.create_index([("clinic_id", 1), ("is_active", 1)])
            await self.db.doctors.create_index([("location_id", 1), ("is_active", 1)])
            await self.db.doctors.create_index("specialty")
            
            # Appointments collection indexes
            await self.db.appointments.create_index("appointment_id", unique=True)
            await self.db.appointments.create_index([("doctor_id", 1), ("date_time", 1)])
            await self.db.appointments.create_index([("patient_id", 1), ("date_time", -1)])
            await self.db.appointments.create_index([("clinic_id", 1), ("status", 1)])
            await self.db.appointments.create_index("date_time")
            
            # Clinics collection indexes
            await self.db.clinics.create_index("clinic_id", unique=True)
            await self.db.clinics.create_index("organization_id")
            await self.db.clinics.create_index([("county", 1), ("city", 1)])
            
            # Locations collection indexes
            await self.db.locations.create_index("location_id", unique=True)
            await self.db.locations.create_index("organization_id")
            await self.db.locations.create_index([("county", 1), ("city", 1)])
            
            # Medical records indexes
            await self.db.medical_records.create_index("record_id", unique=True)
            await self.db.medical_records.create_index([("patient_id", 1), ("created_at", -1)])
            await self.db.medical_records.create_index("doctor_id")
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database indexes: {e}")
    
    async def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """
        Get statistics for a collection.
        
        Args:
            collection: Collection name
            
        Returns:
            Collection statistics
        """
        try:
            stats = await self.db.command("collStats", collection)
            return {
                "count": stats.get("count", 0),
                "size": stats.get("size", 0),
                "avgObjSize": stats.get("avgObjSize", 0),
                "storageSize": stats.get("storageSize", 0),
                "indexes": stats.get("nindexes", 0),
                "totalIndexSize": stats.get("totalIndexSize", 0),
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}
