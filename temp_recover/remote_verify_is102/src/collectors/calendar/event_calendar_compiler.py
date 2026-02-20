from typing import List, Dict, Any
from pathlib import Path
from .earnings_calendar_connector import EarningsCalendarConnector
from .policy_calendar_connector import PolicyCalendarConnector

class EventCalendarCompiler:
    """
    (IS-88) Aggregates all calendar events into a single timeline.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.earnings = EarningsCalendarConnector(base_dir)
        self.policy = PolicyCalendarConnector(base_dir)

    def compile(self) -> List[Dict[str, Any]]:
        """
        Aggregates earnings and policy events.
        Returns sorted list of events by date.
        """
        all_events = []
        
        # Collect
        all_events.extend(self.earnings.fetch_upcoming())
        all_events.extend(self.policy.fetch_upcoming())
        
        # Sort by date
        all_events.sort(key=lambda x: x["event_date"])
        
        return all_events
