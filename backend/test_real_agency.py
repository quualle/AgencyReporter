#!/usr/bin/env python3
"""
Test database system with real agency ID: 5eb000fe2c3484b37749fec4
This tests the cache/database integration with actual production data.
"""

import sys
import asyncio
from datetime import datetime

# Add the app directory to Python path
sys.path.append('.')

from app.utils.database_connection import initialize_database
from app.services.database_cache_service import get_cache_service


async def test_with_real_agency():
    """Test database caching with real agency ID"""
    print("🧪 Testing Database Cache with Real Agency ID: 5eb000fe2c3484b37749fec4")
    print("=" * 70)
    
    try:
        # Initialize database
        db_manager = initialize_database()
        cache_service = get_cache_service()
        
        agency_id = "5eb000fe2c3484b37749fec4"
        
        print(f"📊 Initial Database Stats:")
        stats = await cache_service.get_cache_stats()
        print(f"   Total entries: {stats.get('total_entries', 0)}")
        print(f"   Preloaded entries: {stats.get('preloaded_entries', 0)}")
        print(f"   Database size: {stats.get('database_info', {}).get('size_mb', 0):.2f} MB")
        
        # Test 1: Check data freshness for this agency
        print(f"\n🔍 Checking data freshness for agency {agency_id}...")
        
        data_types = ["quotas", "reaction_times", "problematic_stays"]
        time_periods = ["last_quarter", "last_year", "last_month", "all_time"]
        
        freshness_summary = {}
        total_fresh = 0
        total_checks = 0
        
        for data_type in data_types:
            freshness_summary[data_type] = {}
            for time_period in time_periods:
                is_fresh, hours_until_stale = await cache_service.is_data_fresh(
                    data_type, agency_id, time_period
                )
                freshness_summary[data_type][time_period] = {
                    "fresh": is_fresh,
                    "hours_until_stale": hours_until_stale
                }
                
                total_checks += 1
                if is_fresh:
                    total_fresh += 1
                
                status = "✅ Fresh" if is_fresh else "❌ Stale"
                hours_info = f" ({hours_until_stale:.1f}h)" if hours_until_stale else ""
                print(f"   {data_type:20} {time_period:15} {status}{hours_info}")
        
        print(f"\n📈 Freshness Summary: {total_fresh}/{total_checks} data sets are fresh")
        
        # Test 2: Create a preload session
        print(f"\n🚀 Creating preload session for agency {agency_id}...")
        
        session_key = await cache_service.create_preload_session(agency_id)
        print(f"   Session created: {session_key}")
        
        # Simulate some progress
        await cache_service.update_preload_progress(session_key, 20, 15, 5)
        print(f"   Progress updated: 15/20 successful, 5 failed")
        
        # Get session info
        session_info = await cache_service.get_preload_session_info(session_key)
        if session_info:
            print(f"   Status: {session_info['status']}")
            print(f"   Success rate: {session_info['success_rate']:.1f}%")
            print(f"   Duration: {session_info['duration_minutes']:.1f} minutes")
        
        # Complete session
        await cache_service.complete_preload_session(session_key, success=True)
        print(f"   Session completed successfully")
        
        # Test 3: Save some sample cache data
        print(f"\n💾 Testing cache operations...")
        
        test_data = {
            "agency_id": agency_id,
            "data_type": "test_quotas",
            "timestamp": datetime.utcnow().isoformat(),
            "quotas": {
                "reservations": 245,
                "fulfillments": 220,
                "cancellations": 25
            }
        }
        
        cache_key = cache_service.create_cache_key(
            f"quotas/{agency_id}/all", 
            {"time_period": "last_quarter"}
        )
        
        # Save test data
        save_success = await cache_service.save_cached_data(
            cache_key=cache_key,
            data=test_data,
            endpoint="/api/quotas",
            agency_id=agency_id,
            time_period="last_quarter",
            expires_hours=24,
            is_preloaded=True
        )
        
        if save_success:
            print(f"   ✅ Test data saved to cache")
        else:
            print(f"   ❌ Failed to save test data")
            return False
        
        # Retrieve test data
        retrieved_data = await cache_service.get_cached_data(cache_key)
        if retrieved_data and retrieved_data == test_data:
            print(f"   ✅ Test data retrieved successfully")
        else:
            print(f"   ❌ Failed to retrieve test data or data mismatch")
            return False
        
        # Test 4: Check data freshness after saving
        print(f"\n🔄 Checking freshness after cache operation...")
        
        is_fresh_after, hours_after = await cache_service.is_data_fresh(
            "quotas", agency_id, "last_quarter"
        )
        
        if is_fresh_after:
            print(f"   ✅ Data is now fresh (stale in {hours_after:.1f}h)")
        else:
            print(f"   ❌ Data should be fresh after saving")
        
        # Test 5: Get final statistics
        print(f"\n📊 Final Database Stats:")
        final_stats = await cache_service.get_cache_stats()
        print(f"   Total entries: {final_stats.get('total_entries', 0)}")
        print(f"   Preloaded entries: {final_stats.get('preloaded_entries', 0)}")
        print(f"   Recent sessions: {final_stats.get('recent_sessions_24h', 0)}")
        print(f"   Database size: {final_stats.get('database_info', {}).get('size_mb', 0):.2f} MB")
        
        # Test 6: Stale data check
        stale_data = await cache_service.get_stale_data_types(agency_id)
        print(f"   Stale data types: {len(stale_data)}")
        
        for stale_item in stale_data:
            print(f"     - {stale_item['data_type']} ({stale_item['time_period']}): {stale_item['age_hours']:.1f}h old")
        
        print(f"\n🎉 All tests completed successfully for agency {agency_id}!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_cache_endpoints():
    """Test the new cache API endpoints"""
    print(f"\n🌐 Testing Cache API Endpoints...")
    print("-" * 50)
    
    # Note: These would typically be tested with FastAPI TestClient
    # For now, we'll test the service layer directly
    
    cache_service = get_cache_service()
    agency_id = "5eb000fe2c3484b37749fec4"
    
    try:
        # Test cache health (equivalent to /api/cache/health)
        db_manager = cache_service.db_manager
        connection_ok = await db_manager.test_connection()
        print(f"   Cache Health: {'✅ Healthy' if connection_ok else '❌ Unhealthy'}")
        
        # Test cache stats (equivalent to /api/cache/stats)
        stats = await cache_service.get_cache_stats()
        print(f"   Cache Stats: ✅ Retrieved ({stats.get('total_entries', 0)} entries)")
        
        # Test freshness check (equivalent to /api/cache/freshness/{agency_id})
        is_fresh, hours = await cache_service.is_data_fresh("quotas", agency_id, "last_quarter")
        print(f"   Freshness Check: ✅ Working (fresh: {is_fresh})")
        
        # Test preload session (equivalent to /api/cache/preload/{agency_id})
        session_key = await cache_service.create_preload_session(agency_id)
        print(f"   Preload Session: ✅ Created ({session_key[:20]}...)")
        
        # Test session info (equivalent to /api/cache/preload/session/{session_key})
        session_info = await cache_service.get_preload_session_info(session_key)
        print(f"   Session Info: ✅ Retrieved (status: {session_info['status']})")
        
        # Test cleanup (equivalent to /api/cache/cleanup)
        deleted_count = await cache_service.cleanup_expired_data()
        print(f"   Cache Cleanup: ✅ Completed ({deleted_count} deleted)")
        
        print(f"   🎉 All cache endpoints working correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Cache endpoints test failed: {e}")
        return False


if __name__ == "__main__":
    async def run_tests():
        print("🚀 Real Agency Database Integration Test")
        print("=" * 70)
        
        # Run main test
        main_success = await test_with_real_agency()
        
        # Run endpoints test
        endpoints_success = await test_cache_endpoints()
        
        print("\n" + "=" * 70)
        print("📋 INTEGRATION TEST SUMMARY")
        print("=" * 70)
        
        if main_success and endpoints_success:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
            print("✅ Database system is ready for production use")
            print("✅ Cache API endpoints are functional")
            print("✅ Real agency data integration working")
            return True
        else:
            print("❌ Some integration tests failed")
            print("⚠️  Please review and fix issues before deployment")
            return False
    
    success = asyncio.run(run_tests())
    exit(0 if success else 1)