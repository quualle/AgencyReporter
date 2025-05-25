#!/usr/bin/env python3
"""
Database Cache Diagnostic Tool
Checks if the database migration is working correctly.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.database_cache_service import get_cache_service
from app.utils.database_connection import get_database_manager
from sqlalchemy import select, func
from app.models.database import CachedData, PreloadSession, DataFreshness

async def run_diagnostics():
    print("🔍 DATABASE CACHE DIAGNOSTIC REPORT")
    print("=" * 50)
    
    try:
        cache_service = get_cache_service()
        db_manager = get_database_manager()
        
        # Test 1: Database Connection
        print("\n1️⃣ DATABASE CONNECTION")
        connection_ok = await db_manager.test_connection()
        print(f"   Status: {'✅ Connected' if connection_ok else '❌ Failed'}")
        
        # Test 2: Cache Stats
        print("\n2️⃣ CACHE STATISTICS")
        stats = await cache_service.get_cache_stats()
        print(f"   Total entries: {stats.get('total_entries', 'N/A')}")
        print(f"   Preloaded entries: {stats.get('preloaded_entries', 'N/A')}")
        print(f"   Expired entries: {stats.get('expired_entries', 'N/A')}")
        print(f"   Recent sessions: {stats.get('recent_sessions_24h', 'N/A')}")
        
        # Test 3: Direct Database Query
        print("\n3️⃣ DIRECT DATABASE INSPECTION")
        async with db_manager.get_async_session() as session:
            # Count all cached data
            result = await session.execute(select(func.count(CachedData.id)))
            total_count = result.scalar()
            print(f"   Raw DB entries: {total_count}")
            
            # Count by endpoint type
            result = await session.execute(
                select(CachedData.endpoint, func.count(CachedData.id))
                .group_by(CachedData.endpoint)
            )
            endpoints = result.all()
            print("   Entries by endpoint:")
            for endpoint, count in endpoints:
                print(f"     {endpoint}: {count}")
            
            # Check freshness entries
            result = await session.execute(select(func.count(DataFreshness.id)))
            freshness_count = result.scalar()
            print(f"   Freshness entries: {freshness_count}")
            
            # Check preload sessions
            result = await session.execute(select(func.count(PreloadSession.id)))
            session_count = result.scalar()
            print(f"   Preload sessions: {session_count}")
        
        # Test 4: Agency-Specific Data Check
        print("\n4️⃣ AGENCY CACHE CHECK (649aa2dc2d847c6e7cbe0b56)")
        agency_id = "649aa2dc2d847c6e7cbe0b56"
        
        async with db_manager.get_async_session() as session:
            # Check cached data for this agency
            result = await session.execute(
                select(CachedData.cache_key, CachedData.endpoint, CachedData.created_at, CachedData.is_preloaded)
                .where(CachedData.agency_id == agency_id)
                .order_by(CachedData.created_at.desc())
                .limit(10)
            )
            recent_cache = result.all()
            
            print(f"   Recent cache entries: {len(recent_cache)}")
            for cache_key, endpoint, created_at, is_preloaded in recent_cache:
                preload_flag = "🟢" if is_preloaded else "🔵"
                print(f"     {preload_flag} {endpoint} ({created_at})")
        
        # Test 5: Freshness Data Check
        print("\n5️⃣ FRESHNESS TRACKING")
        freshness_data = await cache_service.get_stale_data_types(agency_id)
        print(f"   Stale data types: {len(freshness_data)}")
        for item in freshness_data:
            print(f"     {item['data_type']}/{item['time_period']} (age: {item['age_hours']:.1f}h)")
        
        # Test 6: Test Cache Key Lookup
        print("\n6️⃣ CACHE KEY TESTS")
        test_keys = [
            "quotas/649aa2dc2d847c6e7cbe0b56/all?time_period=last_quarter",
            "reaction_times/649aa2dc2d847c6e7cbe0b56?time_period=last_quarter", 
            "problematic_stays/overview?agency_id=649aa2dc2d847c6e7cbe0b56&time_period=last_quarter&useExtendedCache=true"
        ]
        
        for key in test_keys:
            data = await cache_service.get_cached_data(key)
            status = "✅ Found" if data else "❌ Missing"
            print(f"   {status}: {key}")
        
        # Test 7: Freshness Check for Different Data Types
        print("\n7️⃣ FRESHNESS STATUS BY DATA TYPE")
        data_types = ["quotas", "reaction_times", "problematic_stays"]
        time_periods = ["last_quarter", "last_year", "last_month", "all_time"]
        
        for data_type in data_types:
            print(f"   {data_type}:")
            for time_period in time_periods:
                is_fresh, hours_until_stale = await cache_service.is_data_fresh(
                    data_type, agency_id, time_period
                )
                status = "🟢 Fresh" if is_fresh else "🔴 Stale"
                print(f"     {time_period}: {status}")
        
        print("\n" + "=" * 50)
        print("✅ Diagnostic completed!")
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_diagnostics())