from datetime import datetime, timedelta


def format_date(date: datetime):
    return date.strftime("%Y-%m-%d")


def today():
    return format_date(datetime.today())


def yesterday():
    return format_date(datetime.today() - timedelta(days=1))


def two_weeks_ago():
    """Returns date 14 days ago"""
    return format_date(datetime.today() - timedelta(days=14))
