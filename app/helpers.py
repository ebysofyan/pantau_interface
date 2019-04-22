from calendar import monthrange
from datetime import date, timedelta

def get_week_boundaries(year, week):
    """function to get range of date in a week by week number"""
    start_of_year = date(year, 1, 1)
    week0 = start_of_year - timedelta(days=start_of_year.isoweekday())
    sun = week0 + timedelta(weeks=week)
    sat = sun + timedelta(days=6)
    return sun, sat


def get_month_boundaries(year, month):
    """get_month_boundaries"""
    dt1 = date(year, month, 1)
    dt2 = date(year, month, monthrange(year, month)[1])
    return dt1, dt2
