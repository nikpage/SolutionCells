from datetime import datetime

def format_expiry_time(expires_at):
    """Format expiry time into human-readable string."""
    now = datetime.now()
    diff = expires_at - now
    hours = int(diff.total_seconds() / 3600)
    return f"{hours}h" if hours > 1 else "soon"
