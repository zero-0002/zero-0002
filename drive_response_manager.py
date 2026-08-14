"""
Drive/Response engagement system for pull request and issue management.
Tracks response times, engagement metrics, and collaboration indicators.
"""

import datetime
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class ResponsePriority(Enum):
    """Priority levels for responses."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class Response:
    """Track individual response metrics."""
    id: str
    type: str  # 'pull_request' or 'issue'
    created_at: datetime.datetime
    responded_at: Optional[datetime.datetime] = None
    priority: ResponsePriority = ResponsePriority.MEDIUM
    author: str = ""
    status: str = "open"  # open, in_progress, closed, merged
    
    @property
    def response_time_hours(self) -> Optional[float]:
        """Calculate response time in hours."""
        if not self.responded_at:
            return None
        delta = self.responded_at - self.created_at
        return delta.total_seconds() / 3600
    
    def is_overdue(self, sla_hours: int = 24) -> bool:
        """Check if response is overdue based on SLA."""
        if self.responded_at:
            return self.response_time_hours > sla_hours
        current_time = datetime.datetime.now()
        hours_elapsed = (current_time - self.created_at).total_seconds() / 3600
        return hours_elapsed > sla_hours


class EngagementMetrics:
    """Track engagement and collaboration metrics."""
    
    def __init__(self):
        self.responses: List[Response] = []
        self.comments_count: int = 0
        self.reviews_completed: int = 0
        self.discussions_started: int = 0
    
    def add_response(self, response: Response) -> None:
        """Record a new response."""
        self.responses.append(response)
    
    def mark_responded(self, response_id: str, responded_at: datetime.datetime) -> None:
        """Mark a response as responded to."""
        for response in self.responses:
            if response.id == response_id:
                response.responded_at = responded_at
                break
    
    def add_comment(self) -> None:
        """Increment comment counter."""
        self.comments_count += 1
    
    def add_review(self) -> None:
        """Increment review counter."""
        self.reviews_completed += 1
    
    def add_discussion(self) -> None:
        """Increment discussion counter."""
        self.discussions_started += 1
    
    def get_average_response_time(self) -> Optional[float]:
        """Calculate average response time in hours."""
        responded = [r for r in self.responses if r.responded_at]
        if not responded:
            return None
        total_hours = sum(r.response_time_hours for r in responded)
        return total_hours / len(responded)
    
    def get_response_rate(self) -> float:
        """Calculate percentage of items responded to."""
        if not self.responses:
            return 0.0
        responded = len([r for r in self.responses if r.responded_at])
        return (responded / len(self.responses)) * 100
    
    def get_overdue_items(self, sla_hours: int = 24) -> List[Response]:
        """Get all overdue items."""
        return [r for r in self.responses if r.is_overdue(sla_hours)]
    
    def get_engagement_score(self) -> float:
        """Calculate overall engagement score (0-100)."""
        score = 0.0
        
        # Response rate component (max 40 points)
        response_rate = self.get_response_rate()
        score += (response_rate / 100) * 40
        
        # Average response time component (max 30 points)
        avg_time = self.get_average_response_time()
        if avg_time:
            # Faster is better - 24 hours = max points
            time_score = max(0, 30 * (1 - (avg_time / 48)))
            score += time_score
        
        # Engagement activity component (max 30 points)
        total_activity = self.comments_count + self.reviews_completed + self.discussions_started
        activity_score = min(30, total_activity)
        score += activity_score
        
        return min(100, score)


class DriveManager:
    """Manage drive and response metrics for repository."""
    
    def __init__(self):
        self.metrics = EngagementMetrics()
        self.pull_requests: List[Response] = []
        self.issues: List[Response] = []
    
    def create_pull_request(self, pr_id: str, author: str) -> Response:
        """Create a pull request entry."""
        response = Response(
            id=pr_id,
            type='pull_request',
            created_at=datetime.datetime.now(),
            author=author,
            priority=ResponsePriority.HIGH
        )
        self.pull_requests.append(response)
        self.metrics.add_response(response)
        return response
    
    def create_issue(self, issue_id: str, author: str) -> Response:
        """Create an issue entry."""
        response = Response(
            id=issue_id,
            type='issue',
            created_at=datetime.datetime.now(),
            author=author,
            priority=ResponsePriority.MEDIUM
        )
        self.issues.append(response)
        self.metrics.add_response(response)
        return response
    
    def respond_to_item(self, item_id: str) -> None:
        """Mark an item as responded to."""
        self.metrics.mark_responded(item_id, datetime.datetime.now())
    
    def get_drive_report(self) -> Dict:
        """Generate comprehensive drive/response report."""
        return {
            'total_pull_requests': len(self.pull_requests),
            'total_issues': len(self.issues),
            'average_response_time_hours': self.metrics.get_average_response_time(),
            'response_rate_percent': self.metrics.get_response_rate(),
            'overdue_items_count': len(self.metrics.get_overdue_items()),
            'total_comments': self.metrics.comments_count,
            'total_reviews': self.metrics.reviews_completed,
            'total_discussions': self.metrics.discussions_started,
            'engagement_score': self.metrics.get_engagement_score()
        }


# Global drive manager
drive_manager = DriveManager()
