"""
Performance optimization utilities for zero-0002 repository.
Implements caching and efficient algorithms to improve execution speed.
"""

import functools
import time
from typing import Any, Callable, Dict


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, float] = {}
        self.call_counts: Dict[str, int] = {}
    
    def record_execution(self, name: str, duration: float) -> None:
        """Record function execution time."""
        if name not in self.metrics:
            self.metrics[name] = 0.0
            self.call_counts[name] = 0
        self.metrics[name] += duration
        self.call_counts[name] += 1
    
    def get_average_time(self, name: str) -> float:
        """Get average execution time for a function."""
        if name not in self.call_counts or self.call_counts[name] == 0:
            return 0.0
        return self.metrics[name] / self.call_counts[name]
    
    def get_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        return {
            name: {
                'total_time': self.metrics[name],
                'call_count': self.call_counts[name],
                'average_time': self.get_average_time(name)
            }
            for name in self.metrics.keys()
        }


# Global performance monitor, shared by every profiled function.
_perf_monitor = PerformanceMonitor()

# Upper bound on memoize caches so long-running processes cannot grow without limit.
MEMOIZE_MAXSIZE = 128


def memoize(func: Callable) -> Callable:
    """Decorator to cache function results."""
    cache: Dict[Any, Any] = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        try:
            hash(key)
        except TypeError:
            # Unhashable arguments cannot be cached; still return a correct result.
            return func(*args, **kwargs)
        if key not in cache:
            if len(cache) >= MEMOIZE_MAXSIZE:
                cache.pop(next(iter(cache)))
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache  # type: ignore
    return wrapper


def profile_execution(func: Callable) -> Callable:
    """Decorator to profile function execution time."""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.perf_counter() - start_time
            _perf_monitor.record_execution(func.__name__, duration)
    
    wrapper.monitor = _perf_monitor  # type: ignore
    return wrapper


class OptimizedOperations:
    """Collection of optimized operations."""
    
    @staticmethod
    @memoize
    def compute_hash(data: str) -> int:
        """Compute hash with caching."""
        return hash(data)
    
    @staticmethod
    def batch_process(items: list, batch_size: int = 100):
        """Process items in batches for better performance."""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]


def get_performance_report() -> Dict[str, Any]:
    """Get overall performance report."""
    return _perf_monitor.get_report()
