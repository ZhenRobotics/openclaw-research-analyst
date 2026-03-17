#!/usr/bin/env python3
"""
Async Architecture Core Module
Version: 1.1.0-alpha
Author: Backend Architect

This module provides the foundational async architecture for parallel
data fetching with caching, circuit breaker, and graceful degradation.

Performance Target:
- Reduce report generation from 38.98s to <20s
- Support cache hit rate >60%
- Maintain 100% reliability with partial failures
"""

import asyncio
import aiohttp
import time
import hashlib
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# =============================================================================
# Data Structures
# =============================================================================

class FetchStatus(Enum):
    """Status codes for fetch operations"""
    SUCCESS = "success"
    CACHED = "cached"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"
    PARTIAL = "partial"


@dataclass
class FetchResult:
    """
    Standardized result container for data source operations

    Attributes:
        source: Name of the data source
        status: Current fetch status
        data: Retrieved data (None on failure)
        error: Error message if failed
        duration_ms: Time taken for operation
        from_cache: Whether data came from cache
        retry_count: Number of retries attempted
        timestamp: When the data was fetched
    """
    source: str
    status: FetchStatus
    data: Optional[dict]
    error: Optional[str] = None
    duration_ms: float = 0.0
    from_cache: bool = False
    retry_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'source': self.source,
            'status': self.status.value,
            'data': self.data,
            'error': self.error,
            'duration_ms': self.duration_ms,
            'from_cache': self.from_cache,
            'retry_count': self.retry_count,
            'timestamp': self.timestamp
        }


@dataclass
class DataSource:
    """
    Configuration for a single data source

    Attributes:
        name: Unique identifier for the source
        fetch_func: Async function to fetch data
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        cache_ttl: Cache time-to-live in seconds
        required: Whether this source is critical (report fails if this fails)
        fallback_sources: Alternative sources to try if this fails
    """
    name: str
    fetch_func: Callable
    timeout: int = 30
    max_retries: int = 3
    cache_ttl: int = 300
    required: bool = False
    fallback_sources: List[str] = field(default_factory=list)


# =============================================================================
# Circuit Breaker Pattern
# =============================================================================

class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests blocked temporarily
    - HALF_OPEN: Testing if service recovered

    Usage:
        breaker = CircuitBreaker(threshold=5, timeout=60)

        if breaker.is_open('api_name'):
            # Skip request, service is down
            return cached_data

        try:
            data = fetch_from_api()
            breaker.record_success('api_name')
        except:
            breaker.record_failure('api_name')
    """

    def __init__(self, threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker

        Args:
            threshold: Number of failures before opening circuit
            timeout: Seconds before attempting recovery (HALF_OPEN state)
        """
        self.threshold = threshold
        self.timeout = timeout
        self.failures: Dict[str, int] = {}
        self.last_failure_time: Dict[str, float] = {}
        self.last_success_time: Dict[str, float] = {}

    def is_open(self, source: str) -> bool:
        """
        Check if circuit is open for a source

        Returns:
            True if circuit is open (service blocked)
        """
        if source not in self.failures:
            return False

        # Check if timeout expired (move to HALF_OPEN)
        time_since_failure = time.time() - self.last_failure_time.get(source, 0)
        if time_since_failure > self.timeout:
            # Reset to HALF_OPEN state
            self.failures[source] = self.threshold - 1
            return False

        return self.failures.get(source, 0) >= self.threshold

    def record_failure(self, source: str):
        """Record a failure for a source"""
        self.failures[source] = self.failures.get(source, 0) + 1
        self.last_failure_time[source] = time.time()

    def record_success(self, source: str):
        """Record a success - reset failure counter"""
        self.failures[source] = 0
        self.last_success_time[source] = time.time()

    def get_status(self, source: str) -> dict:
        """Get current circuit status for monitoring"""
        is_open = self.is_open(source)
        return {
            'source': source,
            'is_open': is_open,
            'failure_count': self.failures.get(source, 0),
            'threshold': self.threshold,
            'last_failure': self.last_failure_time.get(source),
            'last_success': self.last_success_time.get(source)
        }


# =============================================================================
# Cache Manager
# =============================================================================

class SimpleCacheManager:
    """
    Simple in-memory cache manager (L1 cache)

    This is a minimal implementation for Phase 1.
    Will be enhanced in Phase 2 with DiskCache and Redis.

    Features:
    - TTL-based expiration
    - Memory size limit
    - LRU eviction
    """

    def __init__(self, max_size_mb: int = 100):
        """
        Initialize cache manager

        Args:
            max_size_mb: Maximum cache size in megabytes
        """
        self.cache: Dict[str, tuple] = {}  # key -> (data, expiry_time)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.access_times: Dict[str, float] = {}  # For LRU

    def generate_key(self, source: str, params: Optional[dict] = None) -> str:
        """
        Generate cache key from source and parameters

        Args:
            source: Data source name
            params: Optional parameters (e.g., ticker list)

        Returns:
            Cache key string
        """
        key_data = {
            'source': source,
            'params': params or {},
            'version': 'v1'
        }

        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:8]

        return f"cn_market:{source}:{key_hash}"

    def get(self, key: str) -> Optional[dict]:
        """
        Get value from cache

        Returns:
            Cached data or None if not found/expired
        """
        if key not in self.cache:
            return None

        data, expiry = self.cache[key]

        # Check expiration
        if time.time() > expiry:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return None

        # Update access time for LRU
        self.access_times[key] = time.time()

        return data

    def set(self, key: str, data: dict, ttl: int):
        """
        Set value in cache with TTL

        Args:
            key: Cache key
            data: Data to cache
            ttl: Time-to-live in seconds
        """
        expiry = time.time() + ttl
        self.cache[key] = (data, expiry)
        self.access_times[key] = time.time()

        # Check memory limit and evict if needed
        self._evict_if_needed()

    def _evict_if_needed(self):
        """Evict least recently used items if over memory limit"""
        # Simplified eviction - just count entries
        # Real implementation should measure actual memory usage
        max_entries = 1000  # Rough estimate for 100MB

        if len(self.cache) > max_entries:
            # Find least recently used
            lru_key = min(self.access_times, key=self.access_times.get)
            del self.cache[lru_key]
            del self.access_times[lru_key]

    def clear(self):
        """Clear all cached data"""
        self.cache.clear()
        self.access_times.clear()

    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'max_entries': 1000,
            'hit_rate': 0.0  # TODO: Track hits/misses
        }


# =============================================================================
# Async Data Orchestrator
# =============================================================================

class AsyncDataOrchestrator:
    """
    Orchestrates parallel data fetching with caching and error handling

    Features:
    - Parallel async I/O for all data sources
    - Automatic retry with exponential backoff
    - Circuit breaker pattern
    - Cache integration
    - Graceful degradation on partial failures

    Usage:
        cache = SimpleCacheManager()

        async with AsyncDataOrchestrator(cache) as orchestrator:
            sources = [
                DataSource('sina', fetch_sina_async, cache_ttl=15),
                DataSource('eastmoney', fetch_eastmoney_async, cache_ttl=300)
            ]

            results = await orchestrator.fetch_all_sources(sources)

            # results['sina'].data contains the data
            # results['sina'].status indicates success/failure
    """

    def __init__(
        self,
        cache_manager: SimpleCacheManager,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60
    ):
        """
        Initialize orchestrator

        Args:
            cache_manager: Cache manager instance
            circuit_breaker_threshold: Failures before circuit opens
            circuit_breaker_timeout: Seconds before retry attempt
        """
        self.cache_manager = cache_manager
        self.circuit_breaker = CircuitBreaker(
            threshold=circuit_breaker_threshold,
            timeout=circuit_breaker_timeout
        )
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry - create HTTP session"""
        connector = aiohttp.TCPConnector(
            limit=10,           # Max concurrent connections
            limit_per_host=2,   # Max per host to avoid overwhelming
            ttl_dns_cache=300   # DNS cache TTL
        )

        timeout = aiohttp.ClientTimeout(
            total=60,     # Total timeout
            connect=10,   # Connection timeout
            sock_read=30  # Socket read timeout
        )

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup session"""
        if self.session:
            await self.session.close()

    async def fetch_all_sources(
        self,
        sources: List[DataSource],
        params: Optional[dict] = None
    ) -> Dict[str, FetchResult]:
        """
        Fetch data from all sources in parallel

        Args:
            sources: List of DataSource configurations
            params: Optional parameters (e.g., ticker list)

        Returns:
            Dictionary mapping source name to FetchResult
        """
        # Create tasks for all sources
        tasks = []
        for source in sources:
            task = self._fetch_with_retry(source, params)
            tasks.append(task)

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results back to source names
        result_map = {}
        for source, result in zip(sources, results):
            if isinstance(result, Exception):
                # Task raised unhandled exception
                result_map[source.name] = FetchResult(
                    source=source.name,
                    status=FetchStatus.FAILED,
                    data=None,
                    error=f"Unhandled exception: {str(result)}",
                    duration_ms=0
                )
            else:
                result_map[source.name] = result

        return result_map

    async def _fetch_with_retry(
        self,
        source: DataSource,
        params: Optional[dict]
    ) -> FetchResult:
        """
        Fetch from a single source with retry logic

        Args:
            source: DataSource configuration
            params: Optional parameters

        Returns:
            FetchResult with data or error
        """
        start_time = time.time()

        # Check circuit breaker
        if self.circuit_breaker.is_open(source.name):
            return FetchResult(
                source=source.name,
                status=FetchStatus.CIRCUIT_OPEN,
                data=None,
                error="Circuit breaker open - too many recent failures",
                duration_ms=0
            )

        # Check cache
        cache_key = self.cache_manager.generate_key(source.name, params)
        cached_data = self.cache_manager.get(cache_key)

        if cached_data:
            return FetchResult(
                source=source.name,
                status=FetchStatus.CACHED,
                data=cached_data,
                error=None,
                duration_ms=(time.time() - start_time) * 1000,
                from_cache=True
            )

        # Retry loop
        last_error = None
        for attempt in range(source.max_retries):
            try:
                # Call fetch function
                if asyncio.iscoroutinefunction(source.fetch_func):
                    # Async function - call directly
                    data = await source.fetch_func(self.session, params)
                else:
                    # Sync function - run in executor
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(
                        None,
                        source.fetch_func,
                        params
                    )

                duration_ms = (time.time() - start_time) * 1000

                # Success - cache the result
                self.cache_manager.set(cache_key, data, source.cache_ttl)

                # Reset circuit breaker
                self.circuit_breaker.record_success(source.name)

                return FetchResult(
                    source=source.name,
                    status=FetchStatus.SUCCESS,
                    data=data,
                    error=None,
                    duration_ms=duration_ms,
                    from_cache=False,
                    retry_count=attempt
                )

            except asyncio.TimeoutError:
                last_error = f"Timeout after {source.timeout}s"

                if attempt < source.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)

            except Exception as e:
                last_error = str(e)

                if attempt < source.max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)

        # All retries failed
        duration_ms = (time.time() - start_time) * 1000

        # Record failure in circuit breaker
        self.circuit_breaker.record_failure(source.name)

        return FetchResult(
            source=source.name,
            status=FetchStatus.FAILED,
            data=None,
            error=last_error,
            duration_ms=duration_ms,
            from_cache=False,
            retry_count=source.max_retries
        )


# =============================================================================
# Helper Functions
# =============================================================================

def validate_fetch_results(
    results: Dict[str, FetchResult],
    required_sources: List[str]
) -> tuple[bool, str]:
    """
    Validate that all required sources succeeded

    Args:
        results: Fetch results from orchestrator
        required_sources: List of required source names

    Returns:
        Tuple of (is_valid, error_message)
    """
    for source_name in required_sources:
        result = results.get(source_name)

        if not result:
            return False, f"Required source '{source_name}' not found in results"

        if result.status not in [FetchStatus.SUCCESS, FetchStatus.CACHED]:
            return False, f"Required source '{source_name}' failed: {result.error}"

    return True, ""


def get_performance_summary(results: Dict[str, FetchResult]) -> dict:
    """
    Generate performance summary from fetch results

    Args:
        results: Fetch results from orchestrator

    Returns:
        Performance metrics dictionary
    """
    total_sources = len(results)
    successful = sum(
        1 for r in results.values()
        if r.status in [FetchStatus.SUCCESS, FetchStatus.CACHED]
    )
    from_cache = sum(1 for r in results.values() if r.from_cache)

    durations = [r.duration_ms for r in results.values()]
    max_duration = max(durations) if durations else 0
    avg_duration = sum(durations) / len(durations) if durations else 0

    return {
        'total_sources': total_sources,
        'successful': successful,
        'failed': total_sources - successful,
        'success_rate': successful / total_sources if total_sources > 0 else 0,
        'cache_hit_rate': from_cache / total_sources if total_sources > 0 else 0,
        'max_duration_ms': max_duration,
        'avg_duration_ms': avg_duration,
        'total_time_parallel_ms': max_duration,  # Parallel execution time
        'details': {
            source: {
                'status': result.status.value,
                'duration_ms': result.duration_ms,
                'from_cache': result.from_cache,
                'retry_count': result.retry_count
            }
            for source, result in results.items()
        }
    }


# =============================================================================
# Example Usage
# =============================================================================

async def example_usage():
    """
    Example demonstrating how to use the async architecture
    """

    # Define example fetch functions
    async def fetch_example_api(session: aiohttp.ClientSession, params: dict) -> dict:
        """Example async fetch function"""
        async with session.get('https://api.example.com/data') as response:
            return await response.json()

    # Create cache manager
    cache = SimpleCacheManager(max_size_mb=100)

    # Define data sources
    sources = [
        DataSource(
            name='example_api',
            fetch_func=fetch_example_api,
            timeout=30,
            max_retries=3,
            cache_ttl=300,
            required=True
        )
    ]

    # Fetch data
    async with AsyncDataOrchestrator(cache) as orchestrator:
        results = await orchestrator.fetch_all_sources(sources)

        # Validate required sources
        is_valid, error = validate_fetch_results(results, ['example_api'])

        if is_valid:
            print("All required data fetched successfully")
            print(f"Performance: {get_performance_summary(results)}")
        else:
            print(f"Data fetch failed: {error}")


if __name__ == '__main__':
    # Run example
    asyncio.run(example_usage())
