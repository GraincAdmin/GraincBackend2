from django.utils import timezone
from datetime import timedelta

def create_date_formatter(create_date):
    now = timezone.now()

    # Define the time intervals
    create_date_within_24h = now - timedelta(hours=24)
    create_date_within_1h = now - timedelta(hours=1)

    # Calculate the difference from the current time
    time_diff = now - create_date

    if create_date > create_date_within_1h:
        # If the create_date is within the last hour, show minutes ago
        formatted_date = f"{int(time_diff.total_seconds() // 60)}분 전"
    elif create_date > create_date_within_24h:
        # If the create_date is within the last 24 hours but more than an hour ago, show hours ago
        formatted_date = f"{int(time_diff.total_seconds() // 3600)}시간 전"
    else:
        # If the create_date is older than 24 hours, show the full date
        formatted_date = create_date.strftime('%Y.%m.%d')

    return formatted_date