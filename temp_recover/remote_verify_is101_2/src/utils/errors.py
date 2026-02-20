class WarmupError(Exception):
    """Raised when data collection is skipped due to insufficient history (Warm-up)."""
    pass

class SkipError(Exception):
    """Raised when data collection is skipped due to expected data absence (e.g. market holiday)."""
    pass
