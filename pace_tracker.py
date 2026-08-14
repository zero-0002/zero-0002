"""
Pace/Package tracking utilities for commit frequency and release management.
Monitors development velocity and packaging metrics.
"""

import datetime
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class CommitMetric:
    """Track commit statistics."""
    date: datetime.date
    count: int
    authors: int
    message_length: float


class CommitPaceTracker:
    """Track commit pace and frequency metrics."""
    
    def __init__(self):
        self.commits: List[CommitMetric] = []
        self.weekly_stats: Dict[int, int] = {}
        self._by_date: Dict[datetime.date, CommitMetric] = {}
    
    def add_commit(self, date: datetime.date, message: str) -> None:
        """Add a commit entry."""
        # Look up by date rather than only comparing the last entry, so commits
        # supplied out of chronological order still collapse into one day.
        existing = self._by_date.get(date)
        if existing is None:
            metric = CommitMetric(
                date=date,
                count=1,
                authors=1,
                message_length=len(message)
            )
            self._by_date[date] = metric
            self.commits.append(metric)
        else:
            existing.count += 1
    
    def get_weekly_pace(self) -> Dict[str, float]:
        """Calculate weekly commit pace."""
        if not self.commits:
            return {}
        
        weekly_commits = {}
        for commit in self.commits:
            iso_year, week, _ = commit.date.isocalendar()
            # Include the ISO year so the same week number in different years
            # does not collapse into a single bucket.
            key = f"{iso_year}-W{week:02d}"
            weekly_commits[key] = weekly_commits.get(key, 0) + commit.count
        
        return weekly_commits
    
    def get_monthly_pace(self) -> Dict[str, int]:
        """Calculate monthly commit pace."""
        if not self.commits:
            return {}
        
        monthly_commits = {}
        for commit in self.commits:
            month_key = commit.date.strftime("%Y-%m")
            monthly_commits[month_key] = monthly_commits.get(month_key, 0) + commit.count
        
        return monthly_commits
    
    def calculate_average_pace(self) -> float:
        """Calculate average commits per day."""
        if not self.commits:
            return 0.0
        
        total_commits = sum(c.count for c in self.commits)
        days_active = len(self.commits)
        return total_commits / days_active if days_active > 0 else 0.0


class ReleaseManager:
    """Manage release and versioning metrics."""
    
    def __init__(self):
        self.releases: List[Tuple[str, datetime.date]] = []
    
    def add_release(self, version: str, date: datetime.date) -> None:
        """Record a release."""
        self.releases.append((version, date))
    
    def get_release_frequency(self) -> float:
        """Calculate release frequency (releases per month)."""
        if len(self.releases) < 2:
            return 0.0
        
        # Releases are not guaranteed to be recorded in chronological order.
        dates = sorted(date for _, date in self.releases)
        days_between = (dates[-1] - dates[0]).days
        months = days_between / 30.0
        
        return len(self.releases) / months if months > 0 else 0.0
    
    def get_release_report(self) -> Dict[str, Any]:
        """Generate release report."""
        return {
            'total_releases': len(self.releases),
            'latest_release': max(self.releases, key=lambda r: r[1]) if self.releases else None,
            'frequency_per_month': self.get_release_frequency(),
            'release_history': self.releases
        }


class PackageMetrics:
    """Track package quality and distribution metrics."""
    
    def __init__(self):
        self.packages: List[Dict] = []
    
    def add_package(self, name: str, version: str, size: int) -> None:
        """Record a package."""
        self.packages.append({
            'name': name,
            'version': version,
            'size': size,
            'timestamp': datetime.datetime.now()
        })
    
    def get_package_stats(self) -> Dict[str, Any]:
        """Get package statistics."""
        if not self.packages:
            return {}
        
        total_size = sum(p['size'] for p in self.packages)
        avg_size = total_size / len(self.packages)
        
        return {
            'total_packages': len(self.packages),
            'total_size': total_size,
            'average_size': avg_size,
            'largest_package': max(self.packages, key=lambda x: x['size'])
        }


# Global trackers
pace_tracker = CommitPaceTracker()
release_manager = ReleaseManager()
package_metrics = PackageMetrics()
