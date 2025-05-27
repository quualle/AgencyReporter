"""
Cache decorator for unified caching across all endpoints
"""
from functools import wraps
from typing import Callable, Optional, List, Any, Dict
import hashlib
import json
import logging
from datetime import datetime
import inspect
import asyncio

from ..services.database_cache_service import get_cache_service

logger = logging.getLogger(__name__)


def cache_endpoint(
    ttl_hours: int = 48,
    key_params: Optional[List[str]] = None,
    preloadable: bool = False,
    cache_key_prefix: Optional[str] = None
):
    """
    Decorator for caching endpoint responses
    
    Args:
        ttl_hours: Time to live for cached data in hours
        key_params: List of parameter names to include in cache key
        preloadable: Whether this endpoint supports preloading
        cache_key_prefix: Optional prefix for cache key (defaults to endpoint path)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_service = get_cache_service()
            
            # Extract endpoint information
            endpoint_path = cache_key_prefix or func.__name__
            
            # Build cache key from specified parameters
            cache_params = {}
            
            if key_params:
                # Get function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Extract specified parameters for cache key
                for param in key_params:
                    if param in bound_args.arguments:
                        value = bound_args.arguments[param]
                        # Only include non-None values
                        if value is not None:
                            cache_params[param] = value
            
            # Generate cache key using the same logic as frontend
            cache_key = generate_cache_key(endpoint_path, **cache_params)
            
            # Try to get from cache
            start_time = datetime.now()
            cached_data = await cache_service.get_cached_data(cache_key)
            
            if cached_data is not None:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                logger.info(
                    f"[CACHE] Endpoint: {endpoint_path} | Status: HIT | "
                    f"Response Time: {response_time:.0f}ms | Cache Key: {cache_key}"
                )
                return cached_data
            
            # Cache miss - fetch fresh data
            logger.info(
                f"[CACHE] Endpoint: {endpoint_path} | Status: MISS | "
                f"Fetching fresh data | Cache Key: {cache_key}"
            )
            
            # Call the original function
            fetch_start = datetime.now()
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
            except Exception as e:
                logger.error(f"[CACHE] Error fetching data for {endpoint_path}: {str(e)}")
                raise
            
            fetch_time = (datetime.now() - fetch_start).total_seconds() * 1000
            
            # Cache the result
            try:
                # Extract parameters for caching
                cache_params = {}
                if key_params and bound_args:
                    for param in key_params:
                        if param in bound_args.arguments:
                            cache_params[param] = bound_args.arguments[param]
                
                await cache_service.save_cached_data(
                    cache_key=cache_key,
                    data=result,
                    endpoint=endpoint_path,
                    agency_id=cache_params.get('agency_id'),
                    time_period=cache_params.get('time_period'),
                    params=cache_params,
                    expires_hours=ttl_hours,
                    is_preloaded=False
                )
                
                logger.info(
                    f"[CACHE] Endpoint: {endpoint_path} | Status: MISS | "
                    f"Fetch Time: {fetch_time:.0f}ms | Cached for: {ttl_hours}h | "
                    f"Cache Key: {cache_key}"
                )
            except Exception as e:
                logger.error(f"[CACHE] Failed to cache data for {endpoint_path}: {str(e)}")
                # Don't fail the request if caching fails
            
            return result
        
        # For sync functions
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For now, just call the function without caching
            # This can be extended if needed
            return func(*args, **kwargs)
        
        # Set attributes for introspection
        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper._cache_config = {
            'ttl_hours': ttl_hours,
            'key_params': key_params,
            'preloadable': preloadable,
            'cache_key_prefix': cache_key_prefix
        }
        
        return wrapper
    
    return decorator


def generate_cache_key(endpoint: str, **params) -> str:
    """
    Generate a consistent cache key from endpoint and parameters
    
    Args:
        endpoint: The endpoint path
        **params: Parameters to include in the cache key
    
    Returns:
        A consistent cache key string
    """
    # Sort parameters for consistency
    sorted_params = sorted(params.items())
    
    # Build query string
    if sorted_params:
        query_parts = []
        for key, value in sorted_params:
            if value is not None:
                query_parts.append(f"{key}={value}")
        
        if query_parts:
            return f"{endpoint}?{'&'.join(query_parts)}"
    
    return endpoint


def hash_cache_key(cache_key: str) -> str:
    """
    Create a hash of the cache key for storage efficiency
    
    Args:
        cache_key: The cache key to hash
    
    Returns:
        SHA256 hash of the cache key
    """
    return hashlib.sha256(cache_key.encode()).hexdigest()