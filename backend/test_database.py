#!/usr/bin/env python3
"""
Comprehensive test suite for the database-backed cache system.
Tests all aspects of the database migration from in-memory cache.
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta

# Add the app directory to Python path
sys.path.append('.')

from app.utils.database_connection import initialize_database, get_database_manager
from app.services.database_cache_service import get_cache_service
from app.models.database import CachedData, PreloadSession, DataFreshness


async def test_database_initialization():
    """Test 1: Database initialization and table creation"""
    print("🧪 Test 1: Database Initialization")
    try:
        # Initialize database
        db_manager = initialize_database()
        print("✅ Database initialized successfully")
        
        # Test connection
        connection_ok = await db_manager.test_connection()
        if connection_ok:
            print("✅ Database connection test passed")
        else:
            print("❌ Database connection test failed")
            return False
        
        # Get database info
        info = db_manager.get_database_info()
        print(f"📊 Database info: {info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_cache_service_basic_operations():
    """Test 2: Basic cache service operations"""
    print("\n🧪 Test 2: Cache Service Basic Operations")
    try:
        cache_service = get_cache_service()
        
        # Test data
        test_data = {
            "agency_id": "test_agency_123",
            "quotas": [{"type": "reservations", "count": 150}],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cache_key = "test/quotas/test_agency_123"
        
        # Test saving data
        save_success = await cache_service.save_cached_data(
            cache_key=cache_key,
            data=test_data,
            endpoint="/api/quotas",
            agency_id="test_agency_123",
            time_period="last_quarter",
            expires_hours=24,
            is_preloaded=True
        )
        
        if save_success:
            print("✅ Cache data saved successfully")
        else:
            print("❌ Failed to save cache data")
            return False
        
        # Test retrieving data
        retrieved_data = await cache_service.get_cached_data(cache_key)
        
        if retrieved_data:
            print("✅ Cache data retrieved successfully")
            if retrieved_data == test_data:
                print("✅ Retrieved data matches saved data")
            else:
                print(f"❌ Data mismatch: {retrieved_data} != {test_data}")
                return False
        else:
            print("❌ Failed to retrieve cache data")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Cache service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_data_freshness_system():
    """Test 3: Data freshness checking system"""
    print("\n🧪 Test 3: Data Freshness System")
    try:
        cache_service = get_cache_service()
        
        # Test freshness for non-existent data (use unique agency ID)
        is_fresh, hours_until_stale = await cache_service.is_data_fresh(
            data_type="quotas",
            agency_id="non_existent_agency_999",
            time_period="last_quarter"
        )
        
        print(f"DEBUG: Non-existent data freshness check: is_fresh={is_fresh}, hours_until_stale={hours_until_stale}")
        
        if not is_fresh:
            print("✅ Non-existent data correctly marked as not fresh")
        else:
            print("❌ Non-existent data incorrectly marked as fresh")
            return False
        
        # Save some data to create freshness entry
        test_data = {"test": "freshness_data"}
        cache_key = cache_service.create_cache_key("quotas/test_agency_123/all", {"time_period": "last_quarter"})
        
        save_success = await cache_service.save_cached_data(
            cache_key=cache_key,
            data=test_data,
            endpoint="/api/quotas",
            agency_id="test_agency_123",
            time_period="last_quarter",
            expires_hours=24
        )
        
        if not save_success:
            print("❌ Failed to save test data for freshness test")
            return False
        
        # Check freshness again
        is_fresh, hours_until_stale = await cache_service.is_data_fresh(
            data_type="quotas",
            agency_id="test_agency_123",
            time_period="last_quarter"
        )
        
        if is_fresh:
            print(f"✅ Fresh data correctly identified (stale in {hours_until_stale:.1f}h)")
        else:
            print("❌ Fresh data incorrectly marked as stale")
            return False
        
        # Test stale data detection
        stale_data = await cache_service.get_stale_data_types("test_agency_123")
        print(f"📊 Stale data types: {len(stale_data)} found")
        
        return True
        
    except Exception as e:
        print(f"❌ Data freshness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_preload_session_management():
    """Test 4: Preload session management"""
    print("\n🧪 Test 4: Preload Session Management")
    try:
        cache_service = get_cache_service()
        
        # Create preload session
        session_key = await cache_service.create_preload_session("test_agency_456")
        print(f"✅ Preload session created: {session_key}")
        
        # Get session info
        session_info = await cache_service.get_preload_session_info(session_key)
        if session_info:
            print(f"✅ Session info retrieved: {session_info['status']}")
        else:
            print("❌ Failed to retrieve session info")
            return False
        
        # Update progress
        progress_success = await cache_service.update_preload_progress(
            session_key=session_key,
            total_requests=10,
            successful_requests=7,
            failed_requests=3
        )
        
        if progress_success:
            print("✅ Progress updated successfully")
        else:
            print("❌ Failed to update progress")
            return False
        
        # Complete session
        complete_success = await cache_service.complete_preload_session(
            session_key=session_key,
            success=True
        )
        
        if complete_success:
            print("✅ Session completed successfully")
        else:
            print("❌ Failed to complete session")
            return False
        
        # Verify final session state
        final_info = await cache_service.get_preload_session_info(session_key)
        if final_info and final_info['status'] == 'completed':
            print(f"✅ Final session state verified: {final_info['success_rate']:.1f}% success rate")
        else:
            print("❌ Session completion not properly recorded")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Preload session test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_cache_expiry_and_cleanup():
    """Test 5: Cache expiry and cleanup mechanisms"""
    print("\n🧪 Test 5: Cache Expiry and Cleanup")
    try:
        cache_service = get_cache_service()
        
        # Create expired cache entry
        expired_key = "test/expired/data"
        test_data = {"expired": True}
        
        # Save with very short expiry (we'll manually expire it)
        save_success = await cache_service.save_cached_data(
            cache_key=expired_key,
            data=test_data,
            endpoint="/api/test",
            expires_hours=1  # 1 hour
        )
        
        if not save_success:
            print("❌ Failed to save test data for expiry test")
            return False
        
        # Manually expire the entry by updating the database
        db_manager = get_database_manager()
        async with db_manager.get_async_session() as session:
            from sqlalchemy import update
            
            # Set expiry to 1 hour ago
            past_time = datetime.utcnow() - timedelta(hours=1)
            await session.execute(
                update(CachedData)
                .where(CachedData.cache_key == expired_key)
                .values(expires_at=past_time)
            )
            await session.commit()
        
        print("✅ Test entry manually expired")
        
        # Try to retrieve expired data
        retrieved = await cache_service.get_cached_data(expired_key)
        if retrieved is None:
            print("✅ Expired data correctly not returned")
        else:
            print("❌ Expired data incorrectly returned")
            return False
        
        # Test cleanup
        deleted_count = await cache_service.cleanup_expired_data()
        print(f"✅ Cleanup completed: {deleted_count} entries removed")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache expiry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_cache_statistics():
    """Test 6: Cache statistics and monitoring"""
    print("\n🧪 Test 6: Cache Statistics")
    try:
        cache_service = get_cache_service()
        
        # Get cache stats
        stats = await cache_service.get_cache_stats()
        
        if 'total_entries' in stats:
            print(f"✅ Cache statistics retrieved: {stats['total_entries']} total entries")
            print(f"📊 Preloaded entries: {stats.get('preloaded_entries', 0)}")
            print(f"📊 Expired entries: {stats.get('expired_entries', 0)}")
            print(f"📊 Recent sessions: {stats.get('recent_sessions_24h', 0)}")
        else:
            print(f"❌ Invalid cache statistics: {stats}")
            return False
        
        # Check database info
        if 'database_info' in stats:
            db_info = stats['database_info']
            print(f"📊 Database size: {db_info.get('size_mb', 0):.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache statistics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """Test 7: Error handling and edge cases"""
    print("\n🧪 Test 7: Error Handling")
    try:
        cache_service = get_cache_service()
        
        # Test with invalid cache key
        invalid_data = await cache_service.get_cached_data("")
        if invalid_data is None:
            print("✅ Invalid cache key handled correctly")
        else:
            print("❌ Invalid cache key should return None")
        
        # Test non-existent session
        non_existent_info = await cache_service.get_preload_session_info("non_existent_session")
        if non_existent_info is None:
            print("✅ Non-existent session handled correctly")
        else:
            print("❌ Non-existent session should return None")
        
        # Test progress update on non-existent session
        progress_fail = await cache_service.update_preload_progress(
            "non_existent_session", 10, 5, 5
        )
        if not progress_fail:
            print("✅ Progress update on non-existent session handled correctly")
        else:
            print("❌ Progress update should fail for non-existent session")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_data_persistence():
    """Test 8: Data persistence across database manager restarts"""
    print("\n🧪 Test 8: Data Persistence")
    try:
        cache_service = get_cache_service()
        
        # Save persistent test data
        persistent_key = "test/persistent/data"
        persistent_data = {
            "test": "persistence",
            "timestamp": datetime.utcnow().isoformat(),
            "value": 42
        }
        
        save_success = await cache_service.save_cached_data(
            cache_key=persistent_key,
            data=persistent_data,
            endpoint="/api/test",
            expires_hours=48  # Long expiry
        )
        
        if not save_success:
            print("❌ Failed to save persistent test data")
            return False
        
        print("✅ Persistent data saved")
        
        # Close current database connections
        db_manager = get_database_manager()
        db_manager.close()
        
        # Reinitialize database manager (simulates restart)
        new_db_manager = initialize_database()
        
        # Create new cache service
        from app.services.database_cache_service import DatabaseCacheService
        new_cache_service = DatabaseCacheService()
        
        # Retrieve data with new service
        retrieved_data = await new_cache_service.get_cached_data(persistent_key)
        
        if retrieved_data and retrieved_data == persistent_data:
            print("✅ Data persisted across restart")
            return True
        else:
            print(f"❌ Data not persisted correctly: {retrieved_data}")
            return False
        
    except Exception as e:
        print(f"❌ Data persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run comprehensive test suite"""
    print("🚀 Starting Comprehensive Database Cache System Tests")
    print("=" * 60)
    
    tests = [
        ("Database Initialization", test_database_initialization),
        ("Cache Service Basic Operations", test_cache_service_basic_operations),
        ("Data Freshness System", test_data_freshness_system),
        ("Preload Session Management", test_preload_session_management),
        ("Cache Expiry and Cleanup", test_cache_expiry_and_cleanup),
        ("Cache Statistics", test_cache_statistics),
        ("Error Handling", test_error_handling),
        ("Data Persistence", test_data_persistence),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print results summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:12} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Database system is ready for production.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review and fix issues before proceeding.")
    
    return failed == 0


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)